#!/usr/bin/env python3
"""Collect India-focused RSS stories and publish short, source-linked summaries."""
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "sources.json"
OUTPUT = ROOT / "data" / "insights.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self, data):
        if data.strip(): self.parts.append(data.strip())

def clean(value):
    parser=TextExtractor()
    try: parser.feed(html.unescape(value or ""))
    except Exception: return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",value or "")).strip()
    return re.sub(r"\s+"," "," ".join(parser.parts)).strip()

def local(tag):
    return tag.rsplit("}",1)[-1].lower()

def child_text(node, names):
    for child in list(node):
        if local(child.tag) in names:
            if local(child.tag)=="link":
                href=child.attrib.get("href")
                if href: return href
            text="".join(child.itertext()).strip()
            if text: return text
    return ""

def parse_date(value):
    if not value: return None
    try:
        parsed=email.utils.parsedate_to_datetime(value)
        if parsed.tzinfo is None: parsed=parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(IST)
    except Exception:
        try:
            parsed=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
            if parsed.tzinfo is None: parsed=parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(IST)
        except Exception: return None

def get_entries(xml_text):
    root=ET.fromstring(xml_text)
    entries=[]
    for node in root.iter():
        if local(node.tag) not in ("item","entry"): continue
        title=clean(child_text(node,{"title"}))
        link=child_text(node,{"link"})
        if not link:
            for c in list(node):
                if local(c.tag)=="link" and c.attrib.get("href"):
                    link=c.attrib["href"]; break
        description=clean(child_text(node,{"description","summary","encoded","content"}))
        published=child_text(node,{"pubdate","published","updated","date"})
        entries.append({"title":title,"url":link.strip(),"description":description[:5000],"date":parse_date(published)})
    return entries

def category_for(title, description, default):
    text=(title+" "+description).lower()
    if any(x in text for x in ["andhra pradesh","visakhapatnam","vizag","amaravati","tirupati","vijayawada"]):
        return "Andhra Pradesh"
    rules=[
      ("EV & mobility",["electric vehicle"," ev ","evs","battery","charging station","automotive","mobility","siam","fame","electric bus"]),
      ("Skills & livelihoods",["skill development","skilling","vocational","employability","apprentice","workforce","iti ","training","livelihood","education","nsdc","employment"]),
      ("Technology",["artificial intelligence"," ai ","digital india","cyber","semiconductor","data centre","technology","software","digital public","startup","innovation"]),
      ("Policy & research",["niti aayog","policy","government","ministry","scheme","report","research","survey","data.gov","pib"]),
      ("Industry & economy",["manufacturing","industry","industrial","msme","economy","infrastructure","investment","logistics","exports","gdp"])
    ]
    for category,words in rules:
        if any(w in text for w in words): return category
    return default if default in [x[0] for x in rules] else "Industry & economy"

def ai_summary(title, description, source):
    key=os.environ.get("OPENAI_API_KEY")
    excerpt=description[:1800].strip()
    fallback=excerpt if len(excerpt)>70 else "This update from "+source+" highlights a development relevant to India's technology, skills, industry or policy landscape. Read the original report for full details."
    if not key: return fallback[:520]
    prompt=("Write a factual 2-sentence summary (35–55 words) for a professional India-focused knowledge hub. "
      "Use only facts in the supplied title and excerpt. Do not add facts, numbers, causes, predictions or claims not present. "
      "Do not present a proposal as an approved policy or a target as an achieved result. "
      "If the excerpt is thin, write a cautious description of the topic and direct readers to the source. "
      "Return JSON only: {\"summary\":\"...\"}.\n"
      "Publisher: "+source+"\nHeadline: "+title+"\nSource excerpt: "+excerpt)
    payload={"model":"gpt-4.1-mini","messages":[{"role":"system","content":"You are a careful Indian business and public-policy editor. Accuracy and attribution matter more than novelty."},{"role":"user","content":prompt}],"response_format":{"type":"json_object"},"temperature":0.2}
    req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=45) as response: result=json.loads(response.read().decode())
        content=result["choices"][0]["message"]["content"]
        summary=json.loads(content).get("summary","").strip()
        return summary[:650] if len(summary)>35 else fallback[:520]
    except Exception as exc:
        print("AI summary fallback:",str(exc)[:180],file=sys.stderr)
        return fallback[:520]

def main():
    config=json.loads(CONFIG.read_text(encoding="utf-8"))
    now=dt.datetime.now(IST)
    cutoff=now-dt.timedelta(days=int(config.get("max_age_days",21)))
    try: old=json.loads(OUTPUT.read_text(encoding="utf-8"))
    except Exception: old={"articles":[]}
    existing={a.get("id"):a for a in old.get("articles",[]) if a.get("id")}
    seen_urls={a.get("url") for a in existing.values()}
    candidates=[]
    for source in config["feeds"]:
        req=urllib.request.Request(source["url"],headers={"User-Agent":"HillGreenInsightsBot/1.0 (+https://hillgreentechno.com)"})
        try:
            with urllib.request.urlopen(req,timeout=25) as response: raw=response.read()
            text=raw.decode("utf-8",errors="replace")
            entries=get_entries(text)
            print("Fetched",len(entries),"items from",source["name"])
        except Exception as exc:
            print("Feed failed:",source["name"],str(exc)[:180],file=sys.stderr); continue
        for item in entries:
            if not item["title"] or not item["url"] or not item["url"].startswith("http"): continue
            published=item["date"] or now
            if published<cutoff or item["url"] in seen_urls: continue
            domain=urlparse(item["url"]).netloc.lower().removeprefix("www.")
            if not domain: continue
            candidates.append((published,source,item))
    candidates.sort(key=lambda x:x[0],reverse=True)
    added=0
    for published,source,item in candidates:
        if len(existing)>=int(config.get("max_articles",60)): break
        ident=hashlib.sha256(item["url"].encode()).hexdigest()[:16]
        if ident in existing: continue
        summary=ai_summary(item["title"],item["description"],source["name"])
        existing[ident]={
          "id":ident,"title":item["title"][:240],"summary":summary,
          "url":item["url"],"source":source["name"],
          "category":category_for(item["title"],item["description"],source.get("category","Industry & economy")),
          "published_at":published.isoformat(),"collected_at":now.isoformat()
        }
        added+=1
        time.sleep(0.15)
        if added>=18: break
    articles=sorted(existing.values(),key=lambda a:a.get("published_at",""),reverse=True)[:int(config.get("max_articles",60))]
    payload={"updated_at":now.isoformat(),"region":"India","articles":articles}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Published dataset:",len(articles),"articles; new:",added)
    if not articles: print("Warning: no articles collected. Check source feeds.",file=sys.stderr)

if __name__=="__main__": main()
