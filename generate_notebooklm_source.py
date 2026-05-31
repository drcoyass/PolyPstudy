import json
import os

JSON_PATH = "data/latest_papers.json"
OUTPUT_PATH = "notebooklm_source.txt"

def generate_notebooklm_source():
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    
    # Sort papers: dental-related first, then by year (newest first)
    def sort_key(p):
        is_dental = 1 if ('歯科' in p.get('tags', []) or 'インプラント' in p.get('tags', []) or p.get('is_dental_top_100')) else 0
        year = str(p.get('date', '1900'))
        year_num = int(year) if year.isdigit() else 1900
        return (is_dental, year_num)
        
    papers.sort(key=sort_key, reverse=True)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        out.write("【ポリリン酸 総合論文データベース】\n")
        out.write("このドキュメントは、ポリリン酸に関する世界中の論文データ（PubMed, Europe PMC, Crossref等）を統合・網羅したものです。\n")
        out.write("特に歯科領域（インプラント、歯周病、ホワイトニング、骨再生等）に関連する研究データを多く含んでいます。\n\n")
        out.write("=" * 50 + "\n\n")
        
        for p in papers:
            # Skip hidden/noise papers
            if p.get('is_hidden'):
                continue
                
            title = p.get('jp_title') or p.get('title', '')
            original_title = p.get('title', '')
            abstract_jp = p.get('summary_html') or p.get('summary_jp') or ''
            import re
            abstract_jp = re.sub(r'<[^>]+>', '', abstract_jp)
            abstract_en = p.get('abstract', '')
            
            authors = p.get('jp_authors') or p.get('authors', '')
            date = p.get('date', '')
            source = p.get('source', '')
            url = p.get('url', '')
            if not url and p.get('id'):
                url = f"https://pubmed.ncbi.nlm.nih.gov/{p.get('id')}/"
            
            tags = ", ".join(p.get('tags', []))
            
            out.write(f"■ 日本語タイトル: {title}\n")
            out.write(f"■ Original Title: {original_title}\n")
            if tags:
                out.write(f"■ 関連タグ: {tags}\n")
            out.write(f"■ 著者: {authors}\n")
            out.write(f"■ 発行年: {date} (Source: {source})\n")
            out.write(f"■ 原著論文リンク(PDF/記事): {url}\n\n")
            out.write(f"■ 日本語要約:\n{abstract_jp or '(日本語要約なし)'}\n\n")
            out.write(f"■ Original English Abstract:\n{abstract_en or '(No abstract available)'}\n\n")
            out.write("-" * 50 + "\n\n")
            
    print(f"✅ Generated {OUTPUT_PATH} with {len(papers)} papers for NotebookLM.")

if __name__ == "__main__":
    generate_notebooklm_source()
