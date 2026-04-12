import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
from datetime import datetime

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

KEYWORDS_MAP = {
    "インプラント": ["implant", "abutment", "osseointegration"],
    "歯科": ["dental", "periodontal", "tooth", "oral", "gingival", "stomatology"],
    "医科": ["medical", "clinical", "hospital", "patient", "therapy"],
    "再生医療": ["regenerative", "regeneration", "tissue engineering", "stem cell"],
    "骨再生": ["bone", "osteo", "bone formation"],
    "ミトコンドリア": ["mitochondria", "atp", "metabolism", "energy"],
    "炎症": ["inflammation", "inflammatory", "cytokine"],
    "感染": ["infection", "bacteria", "microbial"],
}

def search_pubmed(query, max_results=100):
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"{EUTILS_BASE}/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax={max_results}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data['esearchresult'].get('idlist', [])
    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return []

def fetch_details(pmids):
    if not pmids: return []
    try:
        url = f"{EUTILS_BASE}/efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml"
        papers = []
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for article in root.findall('.//PubmedArticle'):
                pmid = article.findtext('.//PMID')
                title = article.findtext('.//ArticleTitle') or ""
                abstract = article.findtext('.//AbstractText') or ""
                
                pub_date = article.find('.//PubDate')
                year = pub_date.findtext('Year') if pub_date is not None else ""
                
                papers.append({
                    "id": pmid,
                    "title": str(title),
                    "abstract": str(abstract),
                    "date": year,
                    "source": "PubMed",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        return papers
    except Exception as e:
        print(f"⚠️ Fetch error: {e}")
        return []

def auto_tag(paper):
    tags = set(paper.get("tags", []))
    
    # 確実に文字列として取得（エラー回避）
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    
    # 辞書型などが入っている場合に備えて強制変換
    t_str = str(title) if title is not None else ""
    a_str = str(abstract) if abstract is not None else ""
    
    content = (t_str + " " + a_str).lower()
    
    for jp_tag, keywords in KEYWORDS_MAP.items():
        if any(kw in content for kw in keywords):
            tags.add(jp_tag)
    return sorted(list(tags))

def run_update():
    json_path = "data/latest_papers.json"
    if not os.path.exists(json_path):
        print(f"❌ {json_path} が見つかりません。")
        return

    # 1. Search for specifically requested "implant" papers
    print("🔍 Searching PubMed for Polyphosphate + Implant...")
    implant_pmids = search_pubmed("polyphosphate dental implant", max_results=50)
    new_papers = fetch_details(implant_pmids)
    
    # 2. Load existing data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_pmids = {str(p.get('id', '')) for p in data['papers']}
    
    # 3. Add new papers if not exists
    added_count = 0
    for np in new_papers:
        if str(np['id']) not in existing_pmids:
            np['tags'] = auto_tag(np)
            data['papers'].append(np)
            added_count += 1
    
    print(f"✅ Added {added_count} new papers containing 'implant'.")

    # 4. Re-scan ALL papers for correct tagging
    print("🔄 Re-scanning all papers for accurate keyword counts...")
    for p in data['papers']:
        p['tags'] = auto_tag(p)
    
    # 5. Metadata
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✨ Successfully updated {len(data['papers'])} papers with accurate tags.")

if __name__ == "__main__":
    run_update()
