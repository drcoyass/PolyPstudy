import json

def check_discrepancy():
    json_path = '/Users/coyass/kaihatsu/Poly-Pstudy/data/latest_papers.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    stats = data.get('official_stats', {})
    papers = data.get('papers', [])
    
    print("📊 年度別のデータ充足度チェック (統計 vs 実績)")
    print("-" * 50)
    
    for year, target in sorted(stats.items()):
        if "-" in year: continue
        actual = len([p for p in papers if str(p.get('year')) == str(year)])
        shortage = target - actual
        if shortage > 0:
            status = "❌ 不足"
            print(f"📅 {year}年: 目標 {target:4d} 件 | 実績 {actual:4d} 件 | {status} (+{shortage:4d}回抽出必要)")
        else:
            status = "✅ 充足"
            print(f"📅 {year}年: 目標 {target:4d} 件 | 実績 {actual:4d} 件 | {status}")

if __name__ == "__main__":
    check_discrepancy()
