import json, os, re, sys, hashlib
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urlunsplit
import feedparser, requests

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data","tracker.json")
NOW=datetime.now(timezone.utc)
SINCE=NOW-timedelta(hours=72)
FEEDS=[
 ("OpenAI","https://openai.com/news/rss.xml","AI labs"),
 ("Anthropic","https://www.anthropic.com/rss.xml","AI labs"),
 ("Google DeepMind","https://deepmind.google/blog/rss.xml","AI labs"),
 ("AWS Machine Learning","https://aws.amazon.com/blogs/machine-learning/feed/","Developer tools"),
 ("Stripe","https://stripe.com/blog/feed.rss","Fintech"),
 ("Razorpay","https://razorpay.com/blog/feed/","Fintech"),
 ("Hugging Face","https://huggingface.co/blog/feed.xml","Developer tools"),
 ("GitHub Blog","https://github.blog/feed/","Developer tools"),
 ("The Batch","https://www.deeplearning.ai/the-batch/feed/","Research"),
]
ARXIV="https://export.arxiv.org/api/query?search_query=all:%28agent%20OR%20LLM%20OR%20tool-use%20OR%20reasoning%29&start=0&max_results=35&sortBy=submittedDate&sortOrder=descending"

def parse_date(entry):
    for key in ("published_parsed","updated_parsed"):
        val=entry.get(key)
        if val:
            import calendar
            return datetime.fromtimestamp(calendar.timegm(val),timezone.utc)
    for key in ("published","updated"):
        if entry.get(key):
            try:
                dt=parsedate_to_datetime(entry[key])
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
            except Exception: pass
    return None

def clean_url(url):
    p=urlsplit(url.strip())
    return urlunsplit((p.scheme,p.netloc,p.path.rstrip("/"),"", ""))

def collect():
    items=[]; seen=set()
    for source,url,category in FEEDS:
        try:
            feed=feedparser.parse(url)
            for e in feed.entries[:30]:
                link=e.get("link","")
                if not link.startswith("http"): continue
                dt=parse_date(e)
                if not dt or dt<SINCE: continue
                key=clean_url(link)
                if key in seen: continue
                seen.add(key)
                items.append({"source":source,"category":category,"title":e.get("title","").strip(),"url":link,"published":dt.isoformat(),"summary":re.sub(r"\s+"," ",re.sub("<[^>]+>"," ",e.get("summary","")))[:1200]})
        except Exception as ex:
            print(f"Feed skipped: {source}: {ex}")
    try:
        r=requests.get(ARXIV,timeout=25,headers={"User-Agent":"AIResearchTracker/1.0"})
        r.raise_for_status()
        parsed=feedparser.parse(r.text)
        for e in parsed.entries:
            dt=parse_date(e); link=e.get("link","")
            if not dt or dt<SINCE or not link: continue
            key=clean_url(link)
            if key in seen: continue
            seen.add(key)
            items.append({"source":"arXiv","category":"Research","title":e.get("title","").replace("\n"," ").strip(),"url":link,"published":dt.isoformat(),"summary":re.sub(r"\s+"," ",e.get("summary",""))[:1200]})
    except Exception as ex: print(f"arXiv skipped: {ex}")
    items.sort(key=lambda x:x["published"],reverse=True)
    return items[:100]

def call_editor(items):
    api_key=os.environ.get("OPENAI_API_KEY")
    if not api_key: raise RuntimeError("Missing OPENAI_API_KEY secret")
    model=os.environ.get("OPENAI_MODEL") or "gpt-4o-mini"\n    local_today=datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %B %Y")
    prompt={
      "role":"You are the research editor of an independent daily briefing for a technically curious reader working around AI, agents, developer tools and fintech. Focus on original research, product releases, engineering blogs and primary sources. Include Razorpay, Stripe, global payments and fintech when there is a real signal.",
      "rules":[
        "Use only candidate items supplied below. Do not invent facts, dates, sources, URLs, product capabilities or quotes.",
        "Return 5 to 15 stories when the candidate pool supports it; otherwise return fewer rather than padding. Do not repeat stories.",
        "Each story URL must exactly match one candidate URL. Prefer original company, lab, paper or engineering source links.",
        "Explain what happened, why it matters, how it connects to broader shifts, and what to watch. Be specific, restrained and readable.",
        "Avoid generic AI hype and routine funding/marketing announcements unless strategically meaningful.",
        "Return valid JSON only with keys edition, status, thesis, intro, signals, stories, debates, watchlist.",
        "signals: exactly 3 objects with number,title,text. stories: objects with category,tag,title,summary,why,watch,source,url,date. debates: 2 or 3 objects with question,position,tension,signals. watchlist: 4 to 6 strings.",
        f"Today is {local_today} in Asia/Kolkata. Use this exact date for edition (format: DD Month YYYY). status should say Daily research edition.",
        "Story date should be the current date in format DD Mon YYYY. Categories should be concise such as Agents, Research, Developer tools, Fintech, Industry."
      ],
      "candidate_sources":items
    }
    response=requests.post("https://api.openai.com/v1/chat/completions",headers={"Authorization":f"Bearer {api_key}","Content-Type":"application/json"},json={"model":model,"temperature":0.3,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":prompt["role"]+"\nEDITORIAL RULES:\n"+"\n".join("- "+x for x in prompt["rules"])},{"role":"user","content":json.dumps(prompt["candidate_sources"],ensure_ascii=False)}]},timeout=120)
    if not response.ok: raise RuntimeError(f"OpenAI API error {response.status_code}: {response.text[:1000]}")
    content=response.json()["choices"][0]["message"]["content"]
    return json.loads(content)

def validate(result,items):
    allowed={x["url"] for x in items}
    stories=[]
    for s in result.get("stories",[]):
        if s.get("url") not in allowed: continue
        required=("category","tag","title","summary","why","watch","source","url","date")
        if not all(isinstance(s.get(k),str) and s[k].strip() for k in required): continue
        stories.append({k:s[k].strip() for k in required})
    result["stories"]=stories[:15]
    if not result["stories"]: raise RuntimeError("Editorial output contained no verifiable source URLs; refusing to publish.")
    for key in ("signals","debates","watchlist"):
        if not isinstance(result.get(key),list) or not result[key]: raise RuntimeError(f"Invalid editorial field: {key}")
    result["status"]="Daily research edition"
    return result

def main():
    items=collect()
    print(f"Collected {len(items)} recent source items")
    if not items: raise RuntimeError("No recent source items found; refusing to replace the current edition.")
    result=validate(call_editor(items),items)
    os.makedirs(os.path.dirname(DATA),exist_ok=True)
    with open(DATA,"w",encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write("\n")
    print(f"Published edition: {result.get('edition')} ({len(result['stories'])} stories)")
if __name__=="__main__": main()
