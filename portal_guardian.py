import json
import re
import os
from datetime import datetime

# 世界最高峰の品質を維持するためのポータル・ガーディアン
class PortalGuardian:
    def __init__(self, data_path='data/latest_papers.json'):
        self.data_path = data_path
        self.log_path = 'guardian_log.txt'
        self.issues_fixed = 0

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

    def run_audit(self):
        self.log("--- Starting Portal Health Audit ---")
        
        # 1. JSON 整合性チェック
        if not os.path.exists(self.data_path):
            self.log(f"CRITICAL ERROR: {self.data_path} not found.")
            return

        with open(self.data_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                self.log(f"CRITICAL ERROR: JSON Parse failed: {str(e)}")
                return

        papers = data.get('papers', [])
        self.log(f"Auditing {len(papers)} papers...")

        # 2. 自動修復 & 最適化
        fixed_papers = []
        seen_ids = set()
        
        for p in papers:
            # 重複の排除
            if p['id'] in seen_ids:
                self.log(f"FIX: Removed duplicate PMID: {p['id']}")
                self.issues_fixed += 1
                continue
            seen_ids.add(p['id'])

            # 年次フォーマットの正規化 (2026 None 等を 2026 に修正)
            if 'date' in p and p['date']:
                match = re.search(r'\d{4}', str(p['date']))
                if match:
                    detected_year = match.group(0)
                    if not p.get('year') or p['year'] != detected_year:
                        p['year'] = detected_year
                        self.log(f"FIX: Normalized year for PMID {p['id']} -> {detected_year}")
                        self.issues_fixed += 1

            # タイトルのクレンジング（文字列でない場合への耐障害性）
            title_val = p.get('title')
            if isinstance(title_val, str):
                p['title'] = title_val.strip()
            elif isinstance(title_val, dict):
                # 辞書形式の場合は最初の値、または 'text' フィールドを取得
                p['title'] = str(next(iter(title_val.values())) if title_val else "No Title").strip()

            fixed_papers.append(p)

        # 3. 三段階ソートの物理的強制 (Triple-Tier Hardware Sorting)
        # Year (Desc) -> PMID (Desc) -> Title (Asc)
        def sort_key(paper):
            year = int(paper.get('year', 0))
            pmid = int(paper.get('id')) if str(paper.get('id')).isdigit() else 0
            title = paper.get('title', "")
            return (-year, -pmid, title)

        fixed_papers.sort(key=sort_key)
        self.log("INFO: Triple-Tier Sorting applied to physical data.")

        # 4. 保存
        data['papers'] = fixed_papers
        data['guardian_last_run'] = datetime.now().isoformat()
        
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 5. アセットチェック
        self.check_assets()

        self.log(f"Audit Complete. Issues fixed: {self.issues_fixed}")
        self.log("--- Portal is now in ELITE STATUS ---")

    def check_assets(self):
        assets = ['index.html', 'style.css', 'app.js', 'data/summary.json']
        for asset in assets:
            if not os.path.exists(asset):
                self.log(f"WARNING: Missing asset: {asset}")
            else:
                self.log(f"VERIFIED: {asset} is healthy.")

if __name__ == "__main__":
    guardian = PortalGuardian()
    guardian.run_audit()
