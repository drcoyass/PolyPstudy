import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# 設定
QUERY = "polyphosphate"
MAX_BATCH = 200
DATA_DIR = "data"
JSON_PATH = os.path.join(DATA_DIR, "latest_papers.json")
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CROSSREF_API = "https://api.crossref.org/works"

# 医学用語補正
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "osseointegration": "オッセオインテグレーション（骨結合）",
    "mitochondria": "ミトコンドリア",
    "atp": "ATP",
    "implant": "インプラント",
}

import re

def normalize_title(title):
    if not title: return ""
    return re.sub(r"[^a-z0-9]", "", title.lower())

def search_pubmed_by_year(query, start_year, end_year):
    """
    年ごとに分割して検索することで10,000件の制限を回避する
    """
    print(f"🔍 {start_year}年から{end_year}年の論文を検索中...")
    term = f"{query} AND ({start_year}[PDAT] : {end_year}[PDAT])"
    encoded_query = urllib.parse.quote(term)
    url = f"{EUTILS_BASE}/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax=10000"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
        return data['esearchresult'].get('idlist', [])

def auto_translate(text):
    if not text or len(text) < 10: return text
    try:
        # 簡易的な高速翻訳（全件一括の際はGoogleTranslatorを使用）
        translator = GoogleTranslator(source='en', target='ja')
        translated = translator.translate(text)
        for en, jp in GLOSSARY.items():
            translated = translated.replace(en.capitalize(), jp).replace(en, jp)
        return translated
    except:
        return text

def fetch_batch_details(pmids):
    if not pmids: return []
    url = f"{EUTILS_BASE}/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml"
    papers = []
    try:
        with urllib.request.urlopen(url) as response:
            root = ET.fromstring(response.read())
            for article in root.findall('.//PubmedArticle'):
                pmid = article.findtext('.//PMID')
                title = article.findtext('.//ArticleTitle') or ""
                
                # Fetch all AbstractText nodes to support structured abstracts
                abstract_nodes = article.findall('.//AbstractText')
                abstract = " ".join([node.text for node in abstract_nodes if node.text])
                
                tags = []
                content = (title + " " + abstract).lower()
                if "implant" in content: tags.append("インプラント")
                if "dental" in content: tags.append("歯科")
                if "mitochondria" in content: tags.append("ミトコンドリア")
                if "regenerative" in content: tags.append("再生医療")
                
                papers.append({
                    "id": pmid,
                    "title": title,
                    "abstract": abstract,
                    "tags": tags,
                    "date": article.findtext('.//PubDate/Year') or "Unknown",
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        return papers
    except:
        return []

def fetch_europe_pmc(query):
    print("🌍 Europe PMCからプレプリントや特許などの論文を検索中...")
    papers = []
    # ページネーション（今回は最大1000件程度を取得）
    try:
        url = f"{EUROPE_PMC_API}?query={urllib.parse.quote(query)}&format=json&resultType=core&pageSize=1000"
        req = urllib.request.Request(url, headers={'User-Agent': 'PolyPstudy/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('resultList', {}).get('result', [])
            for res in results:
                title = res.get('title', '')
                if not title: continue
                # Skip if already identified as MED (PubMed), because we get that from PubMed directly
                if res.get('source') == 'MED': continue
                
                abstract = res.get('abstractText', '')
                year = str(res.get('pubYear', 'Unknown'))
                ext_id = res.get('pmid') or res.get('doi') or res.get('id', '')
                url_link = f"https://europepmc.org/article/{res.get('source', 'MED')}/{res.get('id', '')}"
                if res.get('doi'):
                    url_link = f"https://doi.org/{res.get('doi')}"
                
                tags = []
                content = (title + " " + abstract).lower()
                if "implant" in content: tags.append("インプラント")
                if "dental" in content: tags.append("歯科")
                
                papers.append({
                    "id": ext_id,
                    "title": title,
                    "abstract": abstract,
                    "tags": tags,
                    "date": year,
                    "source": res.get('source', 'Europe PMC'),
                    "url": url_link
                })
    except Exception as e:
        print(f"Europe PMC API Error: {e}")
    print(f"✅ Europe PMCから {len(papers)} 件の追加論文候補を取得しました。")
    return papers

def fetch_crossref(query):
    print("🌍 Crossrefから医学以外の学術誌（材料・化学など）の論文を検索中...")
    papers = []
    try:
        url = f"{CROSSREF_API}?query={urllib.parse.quote(query)}&select=DOI,title,abstract,author,published-print,URL&rows=1000"
        req = urllib.request.Request(url, headers={'User-Agent': 'mailto:info@poly-pstudy.vercel.app'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('message', {}).get('items', [])
            for item in items:
                title_list = item.get('title', [])
                title = title_list[0] if title_list else ''
                if not title: continue
                
                doi = item.get('DOI', '')
                abstract = item.get('abstract', '')
                # Remove JATS XML tags often found in Crossref abstracts
                abstract = re.sub(r'<[^>]+>', '', abstract)
                
                pub_print = item.get('published-print', {}).get('date-parts', [[]])
                year = str(pub_print[0][0]) if pub_print and pub_print[0] else 'Unknown'
                url_link = item.get('URL', '') or f"https://doi.org/{doi}"
                
                tags = []
                content = (title + " " + abstract).lower()
                if "implant" in content: tags.append("インプラント")
                if "dental" in content: tags.append("歯科")
                
                papers.append({
                    "id": doi,
                    "title": title,
                    "abstract": abstract,
                    "tags": tags,
                    "date": year,
                    "source": "Crossref",
                    "url": url_link
                })
    except Exception as e:
        print(f"Crossref API Error: {e}")
    print(f"✅ Crossrefから {len(papers)} 件の追加論文候補を取得しました。")
    return papers

def run_ultimate_sync():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. 全件PMIDの収集（PubMed）
    all_pmids = []
    for year in range(1950, 2030, 5):
        all_pmids.extend(search_pubmed_by_year(QUERY, year, year+4))
        time.sleep(1)  
    
    all_pmids = list(set(all_pmids))
    print(f"✅ 合計 {len(all_pmids)} 件のPubMed PMIDを特定しました。")

    # 2. 既存データ読み込み
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"papers": []}

    existing_ids = {str(p['id']) for p in data['papers']}
    
    # 【重複排除用】既存論文の正規化タイトルセットを作成
    existing_titles = {normalize_title(p.get('title', '')) for p in data['papers']}
    existing_titles.discard("") # 空文字列は除外

    new_pmids = [pid for pid in all_pmids if str(pid) not in existing_ids]
    print(f"🆕 新着/未取得 (PubMed): {len(new_pmids)} 件")

    # 3. PubMed新着分の取得
    new_pmids.sort(key=lambda x: int(x) if str(x).isdigit() else 0, reverse=True)
    
    new_papers = []
    for i in range(0, len(new_pmids), MAX_BATCH):
        batch = new_pmids[i:i+MAX_BATCH]
        print(f"📥 PubMed取得中 ({i+1}/{len(new_pmids)})...")
        fetched = fetch_batch_details(batch)
        new_papers.extend(fetched)
        time.sleep(1)
        
    # 4. 外部サイトからの追加取得 (Europe PMC & Crossref)
    external_papers = []
    external_papers.extend(fetch_europe_pmc(QUERY))
    external_papers.extend(fetch_crossref(QUERY))
    
    # 5. 重複排除ロジックの適用
    added_count = 0
    for p in new_papers + external_papers:
        pid = str(p['id'])
        norm_title = normalize_title(p.get('title', ''))
        
        # IDが重複している、または正規化タイトルが既存データと一致する場合はスキップ
        if pid in existing_ids or norm_title in existing_titles:
            continue
            
        # 新着リストに追加し、セットも更新（同じ実行内で重複するのを防ぐ）
        existing_ids.add(pid)
        existing_titles.add(norm_title)
        
        # 直近100件程度は自動翻訳する（新着として目立たせるため）
        if added_count < 100:
            print(f"   🇯🇵 翻訳中: {pid}")
            p['summary_jp'] = auto_translate(p['abstract'])
            p['jp_title'] = auto_translate(p['title'])
            
        data['papers'].append(p)
        added_count += 1

    print(f"✨ 最終的に {added_count} 件の新規・外部論文がデータベースに追加されました。")
    
    data['total_pubmed_count'] = len([p for p in data['papers'] if p.get('source') == 'PubMed'])
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✨ 全件同期完了！")

if __name__ == "__main__":
    run_ultimate_sync()
