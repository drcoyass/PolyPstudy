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

# 医学用語補正
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "osseointegration": "オッセオインテグレーション（骨結合）",
    "mitochondria": "ミトコンドリア",
    "atp": "ATP",
    "implant": "インプラント",
}

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
                abstract = article.findtext('.//AbstractText') or ""
                
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

def run_ultimate_sync():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. 全件PMIDの収集（年ごとに分割）
    all_pmids = []
    # 1950年から現在までの5年ごとにスキャン
    for year in range(1950, 2030, 5):
        all_pmids.extend(search_pubmed_by_year(QUERY, year, year+4))
    
    all_pmids = list(set(all_pmids))
    print(f"✅ 合計 {len(all_pmids)} 件のPMIDを特定しました。")

    # 2. 既存データ読み込み
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"papers": []}

    existing_ids = {str(p['id']) for p in data['papers']}
    new_pmids = [pid for pid in all_pmids if str(pid) not in existing_ids]
    
    print(f"🆕 新着/未取得: {len(new_pmids)} 件")

    # 3. 取得と翻訳（新着分のみ）
    for i in range(0, len(new_pmids), MAX_BATCH):
        batch = new_pmids[i:i+MAX_BATCH]
        print(f"📥 取得中 ({i+1}/{len(new_pmids)})...")
        papers = fetch_batch_details(batch)
        
        # 新着分の翻訳（直近100件程度を優先して日本語化。多すぎると時間がかかるため）
        for j, p in enumerate(papers):
            if i + j < 100: # 最新100件を優先
                print(f"   🇯🇵 翻訳中: {p['id']}")
                p['summary_jp'] = auto_translate(p['abstract'])
                p['jp_title'] = auto_translate(p['title'])
        
        data['papers'].extend(papers)
        
        # 保存
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        time.sleep(1)

    data['total_pubmed_count'] = len(data['papers'])
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✨ 全件同期完了！")

if __name__ == "__main__":
    run_ultimate_sync()
