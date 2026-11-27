import json, os, re, hashlib
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit, urlunsplit, quote
import feedparser, requests

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR=os.path.join(ROOT,"data")
TRACKER=os.path.join(DATA_DIR,"tracker.json")
DB_FILE=os.path.join(DATA_DIR,"research-db.json")
NOW=datetime.now(timezone.utc)
LOCAL_NOW=datetime.now(ZoneInfo("Asia/Kolkata"))
TODAY=LOCAL_NOW.strftime("%Y-%m-%d")
THEMES=["Agents & orchestration","Context engineering","Memory","Evals & safety","Coding agents","Prompting","Models & releases","AI in payments","AI adoption & work","Research papers"]

# The source registry is persistent data, not a one-off search prompt.
SOURCES=[
 {
  "name": "Razorpay Engineering",
  "tier": "fintech",
  "watch": "Agents, LLMs, ML systems, developer infrastructure",
  "links": [
   {
    "label": "Engineering site",
    "url": "https://engineering.razorpay.com/"
   }
  ],
  "searches": [
   "site:engineering.razorpay.com AI OR agent OR LLM OR machine learning",
   "Razorpay AI agents engineering blog"
  ],
  "segment": "India"
 },
 {
  "name": "Razorpay",
  "tier": "fintech",
  "watch": "AI products, fraud, risk, payments and agentic commerce",
  "links": [
   {
    "label": "Blog",
    "url": "https://razorpay.com/blog/"
   }
  ],
  "feed": "https://razorpay.com/blog/feed/",
  "searches": [
   "site:razorpay.com/blog AI OR agent OR LLM OR machine learning"
  ],
  "segment": "India"
 },
 {
  "name": "Anthropic",
  "tier": "lab",
  "watch": "Engineering, research, alignment and agents",
  "links": [
   {
    "label": "News",
    "url": "https://www.anthropic.com/news"
   },
   {
    "label": "Engineering",
    "url": "https://www.anthropic.com/engineering"
   }
  ],
  "feed": "https://www.anthropic.com/rss.xml"
 },
 {
  "name": "OpenAI",
  "tier": "lab",
  "watch": "Research, product and engineering",
  "links": [
   {
    "label": "News",
    "url": "https://openai.com/news/"
   }
  ],
  "feed": "https://openai.com/news/rss.xml"
 },
 {
  "name": "Google DeepMind",
  "tier": "lab",
  "watch": "Gemini, research and agents",
  "links": [
   {
    "label": "Blog",
    "url": "https://deepmind.google/discover/blog/"
   }
  ],
  "feed": "https://deepmind.google/blog/rss.xml"
 },
 {
  "name": "Meta AI",
  "tier": "lab",
  "watch": "Open models, research and infrastructure",
  "links": [
   {
    "label": "Research",
    "url": "https://ai.meta.com/blog/"
   }
  ],
  "searches": [
   "site:ai.meta.com/blog AI research model agents"
  ]
 },
 {
  "name": "Mistral AI",
  "tier": "lab",
  "watch": "Models, releases and research",
  "links": [
   {
    "label": "News",
    "url": "https://mistral.ai/news/"
   }
  ],
  "searches": [
   "Mistral AI news models research agents"
  ]
 },
 {
  "name": "xAI",
  "tier": "lab",
  "watch": "Grok models, research and agent capabilities",
  "links": [
   {
    "label": "News",
    "url": "https://x.ai/news"
   }
  ],
  "searches": [
   "xAI Grok research models agents news"
  ]
 },
 {
  "name": "Hugging Face",
  "tier": "lab",
  "watch": "Models, datasets, papers and open-source tools",
  "links": [
   {
    "label": "Blog",
    "url": "https://huggingface.co/blog"
   }
  ],
  "feed": "https://huggingface.co/blog/feed.xml"
 },
 {
  "name": "Microsoft Research",
  "tier": "lab",
  "watch": "Research papers, agents and evaluation",
  "links": [
   {
    "label": "Research",
    "url": "https://www.microsoft.com/en-us/research/blog/"
   }
  ],
  "searches": [
   "site:microsoft.com/en-us/research/blog AI agents LLM"
  ]
 },
 {
  "name": "Cognition",
  "tier": "builder",
  "watch": "Coding agents, agent architecture and context",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.cognition.ai/blog"
   }
  ],
  "searches": [
   "Cognition AI blog coding agent architecture"
  ]
 },
 {
  "name": "LangChain",
  "tier": "builder",
  "watch": "Agents, orchestration, context engineering and evals",
  "links": [
   {
    "label": "Blog",
    "url": "https://blog.langchain.com/"
   }
  ],
  "feed": "https://blog.langchain.com/rss/"
 },
 {
  "name": "LlamaIndex",
  "tier": "builder",
  "watch": "Agents, retrieval, data and evaluation",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.llamaindex.ai/blog"
   }
  ],
  "searches": [
   "LlamaIndex blog agents memory evals"
  ]
 },
 {
  "name": "Cursor",
  "tier": "builder",
  "watch": "Coding agents and developer workflows",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.cursor.com/blog"
   }
  ],
  "searches": [
   "Cursor AI blog coding agents"
  ]
 },
 {
  "name": "Vercel",
  "tier": "builder",
  "watch": "AI SDK, agentic apps and developer tooling",
  "links": [
   {
    "label": "Blog",
    "url": "https://vercel.com/blog"
   }
  ],
  "feed": "https://vercel.com/atom"
 },
 {
  "name": "Replit",
  "tier": "builder",
  "watch": "Coding agents and software creation",
  "links": [
   {
    "label": "Blog",
    "url": "https://blog.replit.com/"
   }
  ],
  "searches": [
   "Replit blog AI agent coding"
  ]
 },
 {
  "name": "Modal",
  "tier": "builder",
  "watch": "AI infrastructure and model serving",
  "links": [
   {
    "label": "Blog",
    "url": "https://modal.com/blog"
   }
  ],
  "searches": [
   "Modal blog AI infrastructure agents"
  ]
 },
 {
  "name": "Stripe",
  "tier": "fintech",
  "watch": "AI, agentic commerce, payments and engineering",
  "links": [
   {
    "label": "Blog",
    "url": "https://stripe.com/blog"
   }
  ],
  "feed": "https://stripe.com/blog/feed.rss",
  "searches": [
   "site:stripe.com/blog AI agents machine learning agentic commerce"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Adyen",
  "tier": "fintech",
  "watch": "AI fraud, risk, authorisation and payment intelligence",
  "links": [
   {
    "label": "News",
    "url": "https://www.adyen.com/knowledge-hub"
   }
  ],
  "searches": [
   "Adyen AI fraud machine learning payments",
   "Adyen agentic commerce AI"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Checkout.com",
  "tier": "fintech",
  "watch": "AI fraud, risk and payment intelligence",
  "links": [
   {
    "label": "Insights",
    "url": "https://www.checkout.com/blog"
   }
  ],
  "searches": [
   "Checkout.com AI fraud machine learning agents"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "PayPal",
  "tier": "fintech",
  "watch": "AI fraud, risk, checkout and agentic commerce",
  "links": [
   {
    "label": "Newsroom",
    "url": "https://newsroom.paypal-corp.com/"
   }
  ],
  "searches": [
   "PayPal AI fraud machine learning agentic commerce",
   "Braintree AI payments machine learning"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Block (Square)",
  "tier": "fintech",
  "watch": "AI in payments, risk and engineering",
  "links": [
   {
    "label": "Engineering",
    "url": "https://developer.squareup.com/blog"
   }
  ],
  "searches": [
   "Block Square engineering AI machine learning payments"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Worldpay",
  "tier": "fintech",
  "watch": "AI fraud, authorisation and payment operations",
  "links": [
   {
    "label": "Insights",
    "url": "https://www.worldpay.com/insights"
   }
  ],
  "searches": [
   "Worldpay AI fraud machine learning payments"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Airwallex",
  "tier": "fintech",
  "watch": "AI in financial operations and payments",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.airwallex.com/blog"
   }
  ],
  "searches": [
   "Airwallex AI agents machine learning payments"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "dLocal",
  "tier": "fintech",
  "watch": "AI fraud, risk and payment optimisation",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.dlocal.com/blog/"
   }
  ],
  "searches": [
   "dLocal AI fraud machine learning payments"
  ],
  "segment": "Global payment companies"
 },
 {
  "name": "Harrison Chase",
  "tier": "person",
  "watch": "In the Loop essays, talks and agent architecture",
  "links": [
   {
    "label": "In the Loop",
    "url": "https://blog.langchain.com/tag/in-the-loop/"
   }
  ],
  "searches": [
   "Harrison Chase In the Loop LangChain agents",
   "Harrison Chase podcast AI agents"
  ]
 },
 {
  "name": "Walden Yan",
  "tier": "person",
  "watch": "Cognition essays, agent architecture and context",
  "links": [
   {
    "label": "Cognition",
    "url": "https://www.cognition.ai/blog"
   }
  ],
  "searches": [
   "Walden Yan Cognition agent architecture context"
  ]
 },
 {
  "name": "Simon Willison",
  "tier": "person",
  "watch": "Practical AI, LLM tooling and experiments",
  "links": [
   {
    "label": "Blog",
    "url": "https://simonwillison.net/"
   }
  ],
  "feed": "https://simonwillison.net/atom/everything/"
 },
 {
  "name": "swyx / Latent Space",
  "tier": "person",
  "watch": "AI engineering, agents and practitioner interviews",
  "links": [
   {
    "label": "Latent Space",
    "url": "https://www.latent.space/"
   }
  ],
  "searches": [
   "Latent Space AI engineering agents recent"
  ]
 },
 {
  "name": "Ethan Mollick",
  "tier": "person",
  "watch": "AI adoption, work and practical experiments",
  "links": [
   {
    "label": "One Useful Thing",
    "url": "https://www.oneusefulthing.org/"
   }
  ],
  "feed": "https://www.oneusefulthing.org/feed"
 },
 {
  "name": "Andrej Karpathy",
  "tier": "person",
  "watch": "Model architecture, coding and AI learning",
  "links": [
   {
    "label": "GitHub",
    "url": "https://github.com/karpathy"
   }
  ],
  "searches": [
   "Andrej Karpathy AI blog YouTube GitHub recent"
  ]
 },
 {
  "name": "Patrick McKenzie",
  "tier": "person",
  "watch": "AI, software businesses and financial infrastructure",
  "links": [
   {
    "label": "Bits about Money",
    "url": "https://www.bitsaboutmoney.com/"
   }
  ],
  "searches": [
   "Patrick McKenzie AI software engineering recent",
   "Patrick McKenzie Complex Systems podcast AI"
  ]
 },
 {
  "name": "Riley Goodside",
  "tier": "person",
  "watch": "Prompting, model behaviour and evaluations",
  "links": [
   {
    "label": "X profile",
    "url": "https://x.com/goodside"
   }
  ],
  "searches": [
   "Riley Goodside prompt engineering AI recent"
  ]
 },
 {
  "name": "Deedy Das",
  "tier": "person",
  "watch": "AI engineering, startups and industry analysis",
  "links": [
   {
    "label": "X profile",
    "url": "https://x.com/deedydas"
   }
  ],
  "searches": [
   "Deedy Das AI agents engineering recent"
  ]
 },
 {
  "name": "Hugging Face Daily Papers",
  "tier": "community",
  "watch": "Only notable agent, memory and evaluation papers",
  "links": [
   {
    "label": "Daily Papers",
    "url": "https://huggingface.co/papers"
   }
  ],
  "searches": [
   "site:huggingface.co/papers agents memory evaluation"
  ]
 },
 {
  "name": "arXiv",
  "tier": "community",
  "watch": "Trending papers on agents, memory, reasoning and evaluation",
  "links": [
   {
    "label": "AI papers",
    "url": "https://arxiv.org/list/cs.AI/recent"
   }
  ],
  "feed": "https://export.arxiv.org/api/query?search_query=all:%28agent%20OR%20LLM%20OR%20tool-use%20OR%20reasoning%20OR%20memory%29&start=0&max_results=50&sortBy=submittedDate&sortOrder=descending"
 },
 {
  "name": "Hacker News",
  "tier": "community",
  "watch": "Front-page AI engineering and research discussions",
  "links": [
   {
    "label": "Front page",
    "url": "https://news.ycombinator.com/"
   }
  ],
  "searches": [
   "Hacker News AI agents LLM research discussion"
  ]
 },
 {
  "name": "Interconnects",
  "tier": "community",
  "watch": "Model development, post-training and AI research analysis",
  "links": [
   {
    "label": "Blog",
    "url": "https://www.interconnects.ai/"
   }
  ],
  "feed": "https://www.interconnects.ai/feed"
 },
 {
  "name": "Paytm",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, machine learning, fraud detection, payments and merchant technology",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://paytm.com/blog/"
   }
  ],
  "searches": [
   "site:paytm.com/blog AI OR machine learning OR fraud OR payments"
  ]
 },
 {
  "name": "PhonePe",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, machine learning, fraud prevention, UPI and payment infrastructure",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.phonepe.com/blog/"
   }
  ],
  "searches": [
   "site:phonepe.com/blog AI OR machine learning OR fraud OR payments"
  ]
 },
 {
  "name": "Cashfree Payments",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, fraud and risk, payment orchestration, identity and developer infrastructure",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.cashfree.com/blog/"
   }
  ],
  "searches": [
   "site:cashfree.com/blog AI OR machine learning OR fraud OR payments"
  ]
 },
 {
  "name": "Juspay",
  "tier": "fintech",
  "segment": "India",
  "watch": "Payment infrastructure, orchestration, ML, intelligent routing and engineering",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://juspay.io/blog"
   }
  ],
  "searches": [
   "site:juspay.io/blog AI OR machine learning OR payments OR engineering"
  ]
 },
 {
  "name": "Pine Labs",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, merchant technology, payment infrastructure and agentic commerce",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.pinelabs.com/blog/"
   }
  ],
  "searches": [
   "site:pinelabs.com/blog AI OR machine learning OR payments"
  ]
 },
 {
  "name": "PayU India",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, fraud, risk, payment technology and checkout",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.payu.in/blog"
   }
  ],
  "searches": [
   "site:payu.in/blog AI OR machine learning OR fraud"
  ]
 },
 {
  "name": "CRED",
  "tier": "fintech",
  "segment": "India",
  "watch": "AI, credit, risk, payments and product engineering",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://cred.club/blog"
   }
  ],
  "searches": [
   "site:cred.club/blog AI OR machine learning OR payments"
  ]
 },
 {
  "name": "Mastercard",
  "tier": "fintech",
  "segment": "Global payment companies",
  "watch": "AI, decision intelligence, fraud, cybersecurity and payment networks",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.mastercard.com/news/"
   }
  ],
  "searches": [
   "site:mastercard.com/news AI OR generative AI OR fraud OR machine learning"
  ]
 },
 {
  "name": "Visa",
  "tier": "fintech",
  "segment": "Global payment companies",
  "watch": "AI, intelligent commerce, fraud, risk and payment networks",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://usa.visa.com/about-visa/newsroom.html"
   }
  ],
  "searches": [
   "site:visa.com AI agentic commerce fraud machine learning"
  ]
 },
 {
  "name": "Fiserv",
  "tier": "fintech",
  "segment": "Global payment companies",
  "watch": "AI, fraud, risk, payments and financial technology infrastructure",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.fiserv.com/en/insights.html"
   }
  ],
  "searches": [
   "site:fiserv.com AI fraud machine learning payments"
  ]
 },
 {
  "name": "Sardine",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "AI-native fraud, identity, risk decisioning and financial crime",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.sardine.ai/blog"
   }
  ],
  "searches": [
   "site:sardine.ai/blog AI fraud risk"
  ]
 },
 {
  "name": "Feedzai",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "AI, machine learning, fraud prevention and financial crime",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.feedzai.com/blog/"
   }
  ],
  "searches": [
   "site:feedzai.com/blog AI machine learning fraud"
  ]
 },
 {
  "name": "Sift",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "ML-powered fraud prevention, trust, safety and risk operations",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://sift.com/blog"
   }
  ],
  "searches": [
   "site:sift.com/blog AI machine learning fraud"
  ]
 },
 {
  "name": "Featurespace",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "Adaptive behavioural analytics, AI fraud detection and financial crime",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.featurespace.com/newsroom/"
   }
  ],
  "searches": [
   "site:featurespace.com AI fraud machine learning"
  ]
 },
 {
  "name": "Riskified",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "AI commerce protection, fraud prevention and chargeback intelligence",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.riskified.com/blog/"
   }
  ],
  "searches": [
   "site:riskified.com/blog AI machine learning fraud"
  ]
 },
 {
  "name": "Forter",
  "tier": "fintech",
  "segment": "AI-led fraud and risk intelligence",
  "watch": "AI identity intelligence, fraud prevention and commerce trust",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.forter.com/blog/"
   }
  ],
  "searches": [
   "site:forter.com/blog AI machine learning fraud"
  ]
 },
 {
  "name": "Plaid",
  "tier": "fintech",
  "segment": "Fintech infrastructure",
  "watch": "AI, financial data infrastructure, identity, risk and developer tools",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://plaid.com/blog/"
   }
  ],
  "searches": [
   "site:plaid.com/blog AI machine learning fraud"
  ]
 },
 {
  "name": "Marqeta",
  "tier": "fintech",
  "segment": "Fintech infrastructure",
  "watch": "AI, card issuing, payment infrastructure, risk and developer technology",
  "links": [
   {
    "label": "Blog / newsroom",
    "url": "https://www.marqeta.com/blog"
   }
  ],
  "searches": [
   "site:marqeta.com/blog AI machine learning payments"
  ]
 }
]

def parse_date(e):
    for k in ("published_parsed","updated_parsed"):
        if e.get(k):
            import calendar
            return datetime.fromtimestamp(calendar.timegm(e[k]),timezone.utc)
    for k in ("published","updated"):
        if e.get(k):
            try:
                d=parsedate_to_datetime(e[k])
                return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)
            except Exception: pass
    return None

def norm_url(url):
    p=urlsplit((url or "").strip())
    return urlunsplit((p.scheme,p.netloc,p.path.rstrip("/"),"", ""))

def clean_text(v):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",v or "")).strip()

def google_news_url(q):
    return "https://news.google.com/rss/search?q="+quote(q)+"&hl=en-IN&gl=IN&ceid=IN:en"

def collect(last_run,known_urls):
    found=[]; seen=set(known_urls)
    cutoff=last_run or (NOW-timedelta(days=3))
    for source in SOURCES:
        targets=[]
        if source.get("feed"): targets.append((source["feed"],source["name"]))
        for q in source.get("searches",[]):
            targets.append((google_news_url(q),source["name"]))
        for feed_url,source_name in targets:
            try:
                parsed=feedparser.parse(feed_url)
                for e in parsed.entries[:35]:
                    link=e.get("link","")
                    if not link.startswith("http"): continue
                    dt=parse_date(e)
                    if not dt or dt<cutoff-timedelta(hours=1): continue
                    key=norm_url(link)
                    if key in seen: continue
                    title=clean_text(e.get("title",""))
                    summary=clean_text(e.get("summary",""))[:1800]
                    if not title: continue
                    seen.add(key)
                    found.append({"source":source_name,"tier":source["tier"],"author":clean_text(e.get("author","")),"title":title,"url":link,"published_at":dt.isoformat(),"published":dt.astimezone(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d"),"raw_summary":summary})
            except Exception as ex:
                print(f"Source check skipped: {source_name}: {ex}")
    found.sort(key=lambda x:x["published_at"],reverse=True)
    return found[:160]

def editor(candidates,archive):
    key=os.environ.get("ANTHROPIC_API_KEY")
    if not key: raise RuntimeError("Missing ANTHROPIC_API_KEY secret")
    model=os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-5-5"
    prompt="""You are an exacting editor of an independent AI research tracker. The reader wants to understand how AI is built, evaluated, deployed and debated, with special attention to agents, context engineering, coding tools and AI in payments.
Use only the supplied candidate records and archive. Never invent an event, claim, author, date or URL. Every URL must be copied exactly from a supplied record. Return valid JSON only:
{
 "updates":[{"url":"exact candidate URL","what_happened":"2-4 plain sentences explaining the actual item","why_it_matters":"1-2 specific sentences","connection":"how it relates to another tracked development, debate or larger shift","themes":["one or more exact allowed theme labels"]}],
 "bigger_picture":{"headline":"specific editorial headline","summary":"4-7 sentence synthesis of what the new items collectively indicate, what changed, why it matters and what remains uncertain","themes":[{"title":"theme","analysis":"evidence-led explanation naming the relevant items or sources"}],"connections":[{"title":"connection or contradiction","explanation":"connect at least two concrete developments"}],"watchlist":["specific signal or question to monitor"]},
 "debates":[{"id":"existing-or-new-kebab-id","question":"substantive AI debate","sides":[{"name":"position name","case":"strongest evidence-backed argument","reading":[{"title":"exact source title","source":"publisher or author","type":"paper, report or engineering case study","note":"what this source contributes","url":"exact supporting URL"}]}],"synthesis":"fair account of the competing positions and what evidence would resolve the question","context":"why the debate matters"}]
}
Editorial rules:
- Include substantive developments only: research, launches, engineering, evaluations, agent architectures, context, memory, coding agents, prompting, model releases, adoption evidence, AI in payments/fraud/risk/agentic commerce. Skip ordinary product marketing, funding and non-AI payment news.
- Give Razorpay items priority when substantive. Include 5-15 updates when candidates support that; include fewer rather than padding.
- For each update, explain what was actually published, why it deserves reading, and how it connects. Distinguish source claims from your interpretation.
- The Bigger Picture must synthesize across the whole candidate set and the archive, not just repeat the headlines. Identify agreements, disagreements, blind spots and open questions. Use 3-5 themes, 2-4 connections and 3-6 watchlist items.
- The debate library is a curated, persistent research resource, not merely a summary of today's news. Preserve every existing debate id and its existing reading material. Add new prominent debates when candidate/archive evidence supports them; do not delete a debate because it is not in today's news.
- For every debate you update, represent both sides fairly. Include the strongest evidence-backed argument for each side, and add reading_material to each side where a supplied candidate/archive URL supports it. Do not invent URLs, papers, authors or positions. Do not treat company marketing as independent evidence.
- Keep debates distinct from daily updates. If there is not enough source material to substantiate both sides of a new debate, do not add it yet. Existing curated debates must remain intact.
- A debate should explain what evidence would change the conclusion and distinguish empirical findings, practitioner experience and normative arguments.
- Theme labels must be selected only from: """+", ".join(THEMES)+"""
- No date restriction. Use the current date only for the run metadata; preserve actual publication dates.
"""
    payload={"today":TODAY,"new_candidates":candidates,"recent_archive":archive[-80:],"existing_debates":DB.get("debates",[])}
    r=requests.post("https://api.anthropic.com/v1/messages",headers={"x-api-key":key,"anthropic-version":"2023-06-01","content-type":"application/json"},json={"model":model,"max_tokens":24000,"temperature":0.2,"system":prompt,"messages":[{"role":"user","content":json.dumps(payload,ensure_ascii=False)}]},timeout=240)
    if not r.ok: raise RuntimeError(f"Anthropic API error {r.status_code}: {r.text[:1200]}")
    blocks=[x.get("text","") for x in r.json().get("content",[]) if x.get("type")=="text"]
    response_text=chr(10).join(blocks).strip()
    if response_text.startswith("```"): response_text=chr(10).join(response_text.splitlines()[1:-1])
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as ex:
        raise RuntimeError(f"Claude returned invalid JSON: {ex}; response starts: {response_text[:500]}")

def slug(s):
    s=re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
    return s[:70] or hashlib.sha1(s.encode()).hexdigest()[:10]

def main():
    global DB
    os.makedirs(DATA_DIR,exist_ok=True)
    if os.path.exists(DB_FILE):
        with open(DB_FILE,encoding="utf-8") as f: DB=json.load(f)
    else:
        DB={"sources":SOURCES,"items":[],"debates":[],"runs":[],"briefing":{"current":{}}}
    DB["sources"]=SOURCES
    # Carry forward the previous edition when upgrading from the original tracker format.
    if not DB.get("items") and os.path.exists(TRACKER):
        try:
            with open(TRACKER,encoding="utf-8") as old_file: old_data=json.load(old_file)
            for story in old_data.get("stories",[]):
                if story.get("url"):
                    DB["items"].append({"id":slug(story.get("source","source")+" "+story.get("title","item")),"tier":"community","priority":False,"source":story.get("source",""),"author":"","published":story.get("date",""),"added":TODAY,"title":story.get("title",""),"url":story["url"],"summary":story.get("summary",""),"sowhat":story.get("why",""),"connection":story.get("watch",""),"themes":[]})
        except Exception as ex:
            print(f"Previous edition migration skipped: {ex}")
    known={norm_url(x.get("url","")) for x in DB.get("items",[])} | {norm_url(u) for u in DB.get("seen_urls",[])}
    last_run=None
    if DB.get("runs"):
        try: last_run=datetime.fromisoformat(DB["runs"][-1]["completed_at"])
        except Exception: last_run=NOW-timedelta(days=3)
    candidates=collect(last_run,known)
    DB.setdefault("seen_urls",[])
    DB["seen_urls"].extend(x["url"] for x in candidates if x["url"] not in DB["seen_urls"])
    print(f"Checked {len(SOURCES)} source records; found {len(candidates)} unseen items.")
    recent=DB.get("items",[])
    # Still refresh the sense-making layer when a day has no new publications.
    if not candidates and not recent: raise RuntimeError("No new source material or archive available; preserving the existing edition.")
    result=editor(candidates,recent)
    candidate_by_url={x["url"]:x for x in candidates}
    new_items=[]
    for u in result.get("updates",[]):
        original=candidate_by_url.get(u.get("url"))
        if not original: continue
        themes=[t for t in u.get("themes",[]) if t in THEMES]
        item={"id":slug(original["source"]+" "+original["title"]),"tier":original["tier"],"priority":original["tier"]=="razorpay","source":original["source"],"author":original.get("author",""),"published":original["published"],"added":TODAY,"title":original["title"],"url":original["url"],"summary":str(u.get("what_happened","")).strip(),"sowhat":str(u.get("why_it_matters","")).strip(),"connection":str(u.get("connection","")).strip(),"themes":themes}
        if item["summary"] and item["sowhat"]: new_items.append(item)
    # Persist all newly verified URLs even if the editor omits low-value candidates, to prevent repeat review.
    DB["items"].extend(new_items)
    DB["items"].sort(key=lambda x:x.get("published",""),reverse=True)
    for d in result.get("debates",[]):
        did=slug(d.get("id") or d.get("question","debate"))
        existing=next((x for x in DB["debates"] if x.get("id")==did),None)
        positions=d.get("positions") or ([d.get("position")] if d.get("position") else [])
        if existing is None:
            existing={"id":did,"title":d.get("question",""),"question":d.get("question",""),"positions":[],"synthesis":d.get("synthesis",""),"context":d.get("context","")}
            DB["debates"].append(existing)
        for pos in positions:
            if pos and pos.get("url") and not any(p.get("url")==pos.get("url") for p in existing["positions"]):
                existing["positions"].append({"who":pos.get("who","Source"),"date":TODAY,"stance":pos.get("stance",""),"url":pos["url"]})
        for side in d.get("sides",[]):
            if not side: continue
            current_side=next((x for x in existing.setdefault("sides",[]) if x.get("name")==side.get("name")),None)
            if current_side is None:
                current_side={"name":side.get("name","Position"),"case":side.get("case",""),"reading":[]}
                existing["sides"].append(current_side)
            if side.get("case"): current_side["case"]=side["case"]
            for reading in side.get("reading",[]):
                if reading and reading.get("url") and not any(x.get("url")==reading.get("url") for x in current_side.setdefault("reading",[])):
                    current_side["reading"].append({k:reading.get(k,"") for k in ("title","source","type","note","url")})
        if d.get("synthesis"): existing["synthesis"]=d["synthesis"]
        if d.get("context"): existing["context"]=d["context"]
    big=result.get("bigger_picture",{})
    big["headline"]="Bigger picture"
    DB["briefing"]={"current":{"date":TODAY,**big}}
    DB.setdefault("runs",[]).append({"date":TODAY,"started_at":NOW.isoformat(),"completed_at":datetime.now(timezone.utc).isoformat(),"candidates_found":len(candidates),"items_added":len(new_items)})
    DB["runs"]=DB["runs"][-500:]
    with open(DB_FILE,"w",encoding="utf-8") as f: json.dump(DB,f,ensure_ascii=False,indent=2); f.write("\n")
    updates=[]
    for x in new_items:
        updates.append({"source":x["source"],"category":x["themes"][0] if x["themes"] else x["tier"],"title":x["title"],"published":x["published"],"what_happened":x["summary"],"why_it_matters":x["sowhat"],"connection":x["connection"],"url":x["url"]})
    tracker={"edition":LOCAL_NOW.strftime("%d %B %Y"),"status":"Daily research edition","sources_checked":f"{len(SOURCES)} configured sources","updates":updates,"bigger_picture":big,"debates":DB["debates"]}
    with open(TRACKER,"w",encoding="utf-8") as f: json.dump(tracker,f,ensure_ascii=False,indent=2); f.write("\n")
    print(f"Published {len(new_items)} new items; archive now contains {len(DB['items'])} records.")
if __name__=="__main__": main()
