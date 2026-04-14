import json
import os
from collections import Counter

def generate_summary_accurate():
    data_path = 'data/latest_papers.json'
    summary_path = 'data/summary.json'
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    # 読み込み
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get("papers", [])
    print(f"📊 Analyzing {len(papers):,} papers for maximum accuracy...")
    
    # 全論文から直接年数を集計（公式データの不備を補完）
    years_list = []
    topic_counter = Counter()
    
    for p in papers:
        # yearまたはdateから取得
        y = p.get("year")
        if not y and p.get("date"):
            y = p.get("date")[:4]
        
        if y and y.isdigit() and 1900 < int(y) < 2100:
            years_list.append(y)
        
        # トピックも再集計
        for t in p.get("tags", []):
            topic_counter[t] += 1

    stats_accurate = dict(Counter(years_list))
    
    # ダッシュボード表示に必要な最小データのみを再構成
    summary = {
        "generated_at": "2026.04.14", # 本日の日付を強制反映
        "total_pubmed_count": data.get("total_pubmed_count", 0),
        "official_stats": stats_accurate, # 再集計した正確な統計
        "global_historical_stats": data.get("global_historical_stats", {}),
        "global_topic_stats": dict(topic_counter),
        "elite_count": len(papers)
    }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Accurate summary generated with latest years (Max Year: {max(years_list) if years_list else 'N/A'})")

if __name__ == "__main__":
    generate_summary_accurate()
