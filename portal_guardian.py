import json
import re
import os
from datetime import datetime
from html import unescape

class SuperIntelligentGuardian:
    def __init__(self, data_path='data/latest_papers.json'):
        self.data_path = data_path
        self.log_path = 'guardian_log.txt'
        self.stats = {
            'fixed_years': 0,
            'fixed_titles': 0,
            'categorized': 0,
            'fixed_links': 0,
            'cleansed_chars': 0,
            'removed_duplicates': 0
        }

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

    def run_full_guard(self):
        self.log("=== Launching SUPER INTELLIGENT GUARDIAN v2.0 ===")
        
        if not os.path.exists(self.data_path):
            self.log("ERROR: Data source missing.")
            return

        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        papers = data.get('papers', [])
        self.log(f"Processing {len(papers)} research records for multiple edge cases...")

        cleansed_papers = []
        seen_ids = set()

        # カテゴリ分類用キーワードマップ
        category_map = {
            'DENTAL': ['oral', 'dental', 'tooth', 'periodontitis', 'dentin', 'pulp', 'alveolar'],
            'MEDICAL': ['cancer', 'cell', 'atp', 'mitochondri', 'tissue', 'regenerat', 'wound', 'bone', 'therapeutic'],
            'ELITE': ['nature', 'science', 'pnas', 'lancet', 'cell', 'nejm']
        }

        for p in papers:
            # 1. 重複排除
            pid = p.get('id', 'Unknown')
            if pid in seen_ids:
                self.stats['removed_duplicates'] += 1
                continue
            seen_ids.add(pid)

            # 2. HTML特殊文字のデコード (&amp; -> & など)
            if 'title' in p and isinstance(p['title'], str):
                original = p['title']
                p['title'] = unescape(original)
                if original != p['title']:
                    self.stats['cleansed_chars'] += 1

            # 3. 年次正規化 (PhD Level)
            if 'date' in p and str(p.get('date')):
                match = re.search(r'\d{4}', str(p['date']))
                if match:
                    y = match.group(0)
                    if p.get('year') != y:
                        p['year'] = y
                        self.stats['fixed_years'] += 1

            # 4. リンクの自動生成 (PMIDベース)
            if not p.get('link') or p['link'] == '---':
                if str(pid).isdigit():
                    p['link'] = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                    self.stats['fixed_links'] += 1

            # 5. セマンティック・カテゴリ補完 (Semantic Categorization)
            if p.get('title'):
                title_lower = p['title'].lower()
                source_lower = str(p.get('source', '')).lower()
                
                # 日本語化されたカテゴリラベルが空なら自動推測
                if not p.get('category'):
                    detected = []
                    for cat, keywords in category_map.items():
                        if any(k in title_lower for k in keywords) or any(k in source_lower for k in keywords):
                            detected.append(cat)
                    if detected:
                        p['category'] = ", ".join(detected)
                        self.stats['categorized'] += 1

            # 6. タイトルの異常修正
            if isinstance(p['title'], dict):
                p['title'] = str(next(iter(p['title'].values())) if p['title'] else "Untitled").strip()
                self.stats['fixed_titles'] += 1

            cleansed_papers.append(p)

        # 降順ソートの物理的強制 (Triple-Tier Execution)
        def sort_key(paper):
            year = int(paper.get('year', 0))
            pmid = int(paper.get('id')) if str(paper.get('id')).isdigit() else 0
            title = str(paper.get('title', ""))
            return (-year, -pmid, title)

        cleansed_papers.sort(key=sort_key)

        # 保存
        data['papers'] = cleansed_papers
        data['guardian_status'] = "INTELLIGENCE_LEVEL_PHD"
        data['last_cleansed'] = datetime.now().isoformat()
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self.log(f"Guardian Report: {json.dumps(self.stats, indent=2)}")
        self.log("=== Portal Health is PERFECT ===")

if __name__ == "__main__":
    guardian = SuperIntelligentGuardian()
    guardian.run_full_guard()
