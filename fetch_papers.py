#!/usr/bin/env python3
"""
PubMedから「Polyphosphate」の最新論文データを取得し、NotebookLMや動画作成の
台本用リファレンスとして最適な形式（Markdown/JSON）で出力する自動化スクリプト。
"""

import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# PubMed API Base URLs
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

def search_pubmed(query, max_results=10):
    """
    指定したクエリでPubMedを検索し、PMIDのリストを返す
    """
    print(f"🔍 検索中: {query} (最大 {max_results} 件)")
    
    encoded_query = urllib.parse.quote(query)
    search_url = f"{EUTILS_BASE}/esearch.fcgi?db=pubmed&term={encoded_query}&retmode=json&retmax={max_results}&sort=date"
    
    try:
        req = urllib.request.Request(search_url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pmids = data['esearchresult'].get('idlist', [])
            return pmids
    except Exception as e:
        print(f"❌ 検索エラー: {e}")
        return []

def fetch_paper_details(pmids):
    """
    PMIDのリストから論文の詳細情報（タイトル、アブストラクト、著者、日付）を取得する
    """
    if not pmids:
        return []
        
    print(f"📥 {len(pmids)}件の論文詳細を取得中...")
    
    ids_str = ",".join(pmids)
    fetch_url = f"{EUTILS_BASE}/efetch.fcgi?db=pubmed&id={ids_str}&retmode=xml"
    
    papers = []
    
    try:
        req = urllib.request.Request(fetch_url)
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            for article in root.findall('.//PubmedArticle'):
                pmid = article.findtext('.//PMID')
                title = article.findtext('.//ArticleTitle')
                abstract = article.findtext('.//AbstractText') or "Abstract not available."
                
                # 著者の取得
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.findtext('LastName')
                    fore_name = author.findtext('ForeName')
                    if last_name and fore_name:
                        authors.append(f"{fore_name} {last_name}")
                    elif last_name:
                        authors.append(last_name)
                        
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += " et al."
                
                # 日付の取得
                pub_date = article.find('.//PubDate')
                year = pub_date.findtext('Year') if pub_date is not None else ""
                month = pub_date.findtext('Month') if pub_date is not None else ""
                date_str = f"{year} {month}".strip() if year else "Unknown Date"
                
                papers.append({
                    "pmid": pmid,
                    "title": str(title),
                    "authors": author_str,
                    "abstract": str(abstract),
                    "date": date_str,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
                
        return papers
    except Exception as e:
        print(f"❌ 詳細取得エラー: {e}")
        return []

def generate_notebooklm_markdown(papers, output_file="notebooklm_source.md"):
    """
    取得した論文データをNotebookLMにアップロードするためのMarkdown形式で保存する
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 近日公開: ポリリン酸関連論文レポート ({datetime.now().strftime('%Y-%m-%d')})\n\n")
        f.write("このドキュメントはNotebookLMに読み込ませるためのナレッジベース用テキストです。\n\n")
        f.write("---\n\n")
        
        for idx, paper in enumerate(papers, 1):
            f.write(f"## {idx}. {paper['title']}\n\n")
            f.write(f"**Authors:** {paper['authors']}\n")
            f.write(f"**Date:** {paper['date']}\n")
            f.write(f"**Source URL:** {paper['url']}\n\n")
            f.write("### Abstract\n")
            f.write(f"{paper['abstract']}\n\n")
            f.write("---\n\n")
            
    print(f"✅ NotebookLM用ソーステキストを {output_file} に生成しました。")

if __name__ == "__main__":
    # 検索クエリ: ポリリン酸 (Polyphosphate) に関する最近の論文
    QUERY = "polyphosphate"
    MAX_RESULTS = 5  # 今月のトップ5件を取得するイメージ
    
    os.makedirs("data", exist_ok=True)
    
    pmids = search_pubmed(QUERY, max_results=MAX_RESULTS)
    if pmids:
        papers = fetch_paper_details(pmids)
        
        # UI表示用のJSONとして保存
        json_path = "data/latest_papers.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=4)
        print(f"✅ JSONデータを {json_path} に保存しました。")
        
        # NotebookLM用のMarkdownソースを生成
        md_path = "data/notebooklm_source.md"
        generate_notebooklm_markdown(papers, md_path)
    else:
        print("論文が見つかりませんでした。")
