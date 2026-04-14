import json
import os

def generate_summary():
    data_path = 'data/latest_papers.json'
    summary_path = 'data/summary.json'
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # ダッシュボード表示に必要な最小データのみを抽出
    summary = {
        "generated_at": data.get("generated_at", ""),
        "total_pubmed_count": data.get("total_pubmed_count", 0),
        "official_stats": data.get("official_stats", {}),
        "global_historical_stats": data.get("global_historical_stats", {}),
        "global_topic_stats": data.get("global_topic_stats", {}),
        "elite_count": len(data.get("papers", []))
    }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Summary data ( {os.path.getsize(summary_path) / 1024:.2f} KB ) generated.")

if __name__ == "__main__":
    generate_summary()
