import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from datetime import datetime

try:
    from openai import OpenAI
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
except ImportError:
    print("❌ 必要なライブラリがインストールされていません。")
    exit(1)

# API Keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
JSTAGE_API_BASE = "https://api.jstage.jst.go.jp/searchapi/do"
CINII_API_BASE = "https://cir.nii.ac.jp/opensearch/all"

CACHE_FILE = "data/papers_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_cache(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)

def search_pubmed(query, max_results=3, sort="date"):
    encoded_query = urllib.parse.quote(query)
    url = f"{EUTILS_BASE}/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax={max_results}&sort={sort}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            id_list = data['esearchresult'].get('idlist', [])
            total_count = int(data['esearchresult'].get('count', 0))
            return id_list, total_count
    except: return [], 0

def fetch_paper_details(pmids):
    if not pmids: return []
    print(f"📥 膨大な論文データを取得中... 合計 {len(pmids)} 件")
    papers = []
    chunk_size = 200 # 大量取得用にサイズアップ
    for i in range(0, len(pmids), chunk_size):
        chunk = pmids[i:i+chunk_size]
        url = f"{EUTILS_BASE}/efetch.fcgi?db=pubmed&id={','.join(chunk)}&retmode=xml"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as res:
                root = ET.fromstring(res.read())
                for art in root.findall('.//PubmedArticle'):
                    pmid = art.findtext('.//PMID')
                    title = art.findtext('.//ArticleTitle')
                    abstract = art.findtext('.//AbstractText') or ""
                    authors = []
                    for au in art.findall('.//Author'):
                        ln, fn = au.findtext('LastName'), au.findtext('ForeName')
                        if ln and fn: authors.append(f"{fn} {ln}")
                    author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
                    year = art.findtext('.//PubDate/Year') or ""
                    papers.append({
                        "id": str(pmid), "title": title, "authors": author_str, "abstract": abstract,
                        "date": year, "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", "source": "PubMed"
                    })
            if i % 1000 == 0 and i > 0: print(f"  > {i}件 完了...")
        except: continue
    return papers

def summarize_for_slide(paper):
    if not client: return {"summary_html": "API Key missing", "categories": ["その他"], "is_noise": False}
    prompt = f"要約対象:\nTitle: {paper['title']}\nAbstract: {paper['abstract']}\nAuthors: {paper['authors']}\n\n歯科医師向けに日本語で要約し、カテゴリから選択してください。JSON出力:\n{{\"summary_html\": \"...\", \"categories\": [\"歯科\"], \"jp_authors\": \"...\", \"hashtags\": [], \"is_noise\": false}}"
    try:
        res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        return json.loads(res.choices[0].message.content)
    except: return {"summary_html": "AI Error", "categories": ["その他"], "is_noise": False}

def update_database_json(all_papers, pptx_path, total_count=0, stats=None, top_ids=[], dental_ids=[]):
    json_path = "data/latest_papers.json"
    existing = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing = {str(p['id']): p for p in data.get("papers", [])}
        except: pass
    
    for p in all_papers:
        pid = str(p['id'])
        # 既存にAI要約があれば優先、なければ現在のデータ
        is_elite = (pid in top_ids or pid in dental_ids or p.get('source') != "PubMed")
        
        # 精鋭でない場合は、要約なしのメタデータのみで軽量化
        summary_data = p.get('summary')
        if not summary_data and pid in existing:
            summary_data = existing[pid].get('summary_data') or {"summary_html": existing[pid].get('summary_html')}

        entry = {
            "id": pid, "title": p['title'], "jp_title": p.get('jp_title', p['title']),
            "authors": p['authors'], "jp_authors": p.get('jp_authors', p['authors']),
            "date": p['date'], "url": p['url'], "source": p.get('source', "PubMed"),
            "tags": summary_data.get('categories', []) if summary_data else [],
            "hashtags": p.get('hashtags', []),
            "summary_html": summary_data.get('summary_html', "") if summary_data else "",
            "abstract": p.get('abstract', "")[:500] + ("..." if len(p.get('abstract', "")) > 500 else ""),
            "is_top_100": (pid in top_ids),
            "is_dental_top_100": (pid in dental_ids),
            "is_hidden": summary_data.get('is_noise', False) if summary_data else False
        }
        existing[pid] = entry
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "pptx_path": pptx_path,
            "total_pubmed_count": total_count,
            "official_stats": stats,
            "papers": list(existing.values())
        }, f, ensure_ascii=False, indent=2)
    print(f"✨ 全論文データベース同期完了: 全 {len(existing)} 件")

def main():
    base_query = '(polyphosphate OR "inorganic polyphosphate" OR "poly-P")'
    refined = f'{base_query} NOT (detergent OR laundry OR wastewater OR "scale inhibitor")'
    dental_q = f'({base_query}) AND (dental OR dentistry OR tooth OR periodontal OR caries OR implant OR oral)'
    
    # 全件ID取得 (PubMed制限により100,000まで可能だが、実用上20,000程度に設定)
    print("🌍 PubMedから全ポリリン酸論文のIDを取得中...")
    all_ids, total = search_pubmed(base_query, max_results=20000, sort="date")
    stats = {str(y): search_pubmed(f"{base_query} AND {y}[Date - Publication]", max_results=0)[1] for y in range(datetime.now().year-15, datetime.now().year+1)}
    
    # 精鋭の選出
    top_ids, _ = search_pubmed(refined, max_results=100, sort="relevance")
    dental_ids, _ = search_pubmed(dental_q, max_results=100, sort="relevance")
    
    # 既存データの読み込み (不要なフェッチを避ける)
    json_path = "data/latest_papers.json"
    existing_ids = set()
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            d = json.load(f)
            existing_ids = {str(p['id']) for p in d.get("papers", [])}
    
    # 新規分のみ詳細フェッチ (ただし精鋭は必ずフェッチしてAI処理を試みる)
    ids_to_fetch = [pid for pid in all_ids if pid not in existing_ids]
    # 精鋭は常に最新情報を追う
    elite_ids = list(set(top_ids + dental_ids))
    ids_to_fetch = elite_ids + ids_to_fetch[:3000] # 一回の実行で最大3000件ずつ追加(負荷調整)
    
    papers = fetch_paper_details(list(dict.fromkeys(ids_to_fetch)))
    
    # 精緻解析
    cache = load_cache()
    for i, p in enumerate(papers):
        pid = str(p['id'])
        if pid in elite_ids:
            if pid in cache: p.update(cache[pid])
            else:
                print(f"🧠 重要論文の解析中 ({i+1}/{len(elite_ids)})...")
                p['summary'] = summarize_for_slide(p)
                cache[pid] = p
                save_cache(cache)
    
    update_database_json(papers, "output/Monthly_Report.pptx", total_count=total, stats=stats, top_ids=top_ids, dental_ids=dental_ids)

if __name__ == "__main__":
    main()
