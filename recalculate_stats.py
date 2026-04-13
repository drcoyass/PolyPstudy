import json
from collections import Counter

def recalculate_stats():
    json_path = '/Users/coyass/kaihatsu/Poly-Pstudy/data/latest_papers.json'
    
    print(f"📖 {json_path} を読み込み中...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    print(f"✅ {len(papers)} 件の論文データをスキャン中...")
    
    # 年度ごとの統計を全件から再集計
    years = []
    for p in papers:
        year = p.get('year')
        if year and str(year).isdigit():
            years.append(str(year))
    
    new_stats = dict(sorted(Counter(years).items()))
    
    # 統計データを更新
    data['official_stats'] = new_stats
    # UI表示用の総数も念のため更新
    data['total_pubmed_count'] = max(data.get('total_pubmed_count', 0), len(papers))
    
    # 保存
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✨ 統計データを再計算し、全年度分（2011年以前を含む）に対応しました。")
    print(f"📊 集計された年度範囲: {list(new_stats.keys())[0]} - {list(new_stats.keys())[-1]}")
    print(f"📈 統計に含まれる総論文数: {sum(new_stats.values())}")

if __name__ == "__main__":
    recalculate_stats()
