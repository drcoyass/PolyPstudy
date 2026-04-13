import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import time
from datetime import datetime

# 設定
QUERY = "polyphosphate"
MAX_BATCH = 400  # 高速化のためにバッチサイズを拡大
DATA_DIR = "data"
JSON_PATH = os.path.join(DATA_DIR, "latest_papers.json")
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed_all_pmids(query):
    """
    年度別に分割して全件のPMIDを取得する（1万件制限の回避）
    """
    print(f"🔍 PubMedから '{query}' に関連する全論文をスキャン中（年度分割モード）...")
    all_ids = []
    
    # 歴史を10年〜5年単位で区切って取得
    ranges = [
        (1950, 1980), (1981, 1995), (1996, 2005), 
        (2006, 2010), (2011, 2015), (2016, 2020), 
        (2021, 2026)
    ]
    
    for start, end in ranges:
        term = f"{query} AND ({start}[PDAT] : {end}[PDAT])"
        encoded_query = urllib.parse.quote(term)
        url = f"{EUTILS_BASE}/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax=10000"
        try:
            with urllib.request.urlopen(url) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ids = res_data['esearchresult'].get('idlist', [])
                print(f"  📅 {start}-{end}年: {len(ids)} 件発見")
                all_ids.extend(ids)
        except:
            continue
            
    return list(set(all_ids))

def fetch_details_fast(pmids):
    """
    タイトル、年度、著者を高速に取得する (Abstract翻訳は最小限にし、リスト埋めを優先)
    """
    if not pmids: return []
    url = f"{EUTILS_BASE}/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml"
    papers = []
    try:
        with urllib.request.urlopen(url) as response:
            root = ET.fromstring(response.read())
            for article in root.findall('.//PubmedArticle'):
                pmid = article.findtext('.//PMID')
                title = article.findtext('.//ArticleTitle') or ""
                
                # 年度抽出
                year = article.findtext('.//PubDate/Year')
                if not year:
                    # MedlineDate 形式のケース (例: 2024 May-Jun)
                    medline_date = article.findtext('.//PubDate/MedlineDate')
                    if medline_date:
                        import re
                        m = re.search(r'\d{4}', medline_date)
                        if m: year = m.group(0)
                
                year = year or "Unknown"
                
                # 著者
                authors = []
                for author in article.findall('.//Author'):
                    lastName = author.findtext('LastName') or ""
                    foreName = author.findtext('ForeName') or ""
                    if lastName: authors.append(f"{lastName} {foreName}")
                
                author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")

                papers.append({
                    "id": pmid,
                    "title": title,
                    "year": year,
                    "date": year,
                    "authors": author_str,
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "tags": ["PubMed"],
                    "abstract": article.findtext('.//AbstractText') or "Abstract is available at the source."
                })
        return papers
    except Exception as e:
        print(f"⚠️ 取得エラー: {e}")
        return []

def run_deep_sync():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. 全件PMIDの収集
    all_pmids = search_pubmed_all_pmids(QUERY)
    print(f"✅ 合計 {len(all_pmids)} 件のPMIDを特定しました。")
    
    # 2. 既存データ読み込み
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"papers": [], "official_stats": {}}

    existing_ids = {str(p['id']) for p in data['papers']}
    new_pmids = [pid for pid in all_pmids if str(pid) not in existing_ids]
    
    print(f"🆕 新着/未取得: {len(new_pmids)} 件")

    # 3. 超高速バッチ取得
    for i in range(0, len(new_pmids), MAX_BATCH):
        batch = new_pmids[i:i+MAX_BATCH]
        print(f"📥 抽出中 ({i+1}/{len(new_pmids)})...")
        papers = fetch_details_fast(batch)
        
        data['papers'].extend(papers)
        
        # 進行中のデータベース整合性チェック（年度別統計をリアルタイム更新）
        current_years = [p.get('year') for p in data['papers'] if p.get('year') and p.get('year').isdigit()]
        from collections import Counter
        data['official_stats'] = dict(sorted(Counter(current_years).items()))
        data['total_pubmed_count'] = len(data['papers'])
        data['generated_at'] = datetime.now().strftime("%Y-%m-%d")

        # 随時保存
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        time.sleep(0.5)

    print(f"✨ 同期完了！合計 {len(data['papers'])} 件の『本物の論文』が登録されました。")

if __name__ == "__main__":
    run_deep_sync()
