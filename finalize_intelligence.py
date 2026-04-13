import json

def finalize_intelligence_analysis():
    json_path = '/Users/coyass/kaihatsu/Poly-Pstudy/data/latest_papers.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    print(f"🧠 19,018件の全論文をインテリジェンス分析中...")

    # 分類キーワード定義
    categories = {
        "歯科": ["dental", "dentist", "periodontal", "periodontitis", "orthodontic", "caries", "enamel", "dentin", "pulp", "gingiva", "oral"],
        "インプラント": ["implant", "osseointegration", "abutment"],
        "再生医療": ["regeneration", "regenerative", "scaffold", "stem cell", "tissue engineering", "bone morphogenetic"],
        "ミトコンドリア": ["mitochondria", "atp", "metabolism", "energy production"],
        "医科（一般）": ["cancer", "tumor", "blood", "coagulation", "platelet", "bone", "osteoblast", "infection", "immune"],
        "ホワイトニング": ["whitening", "bleaching", "stain", "color"]
    }

    topic_counts = {cat: 0 for cat in categories}
    
    for p in papers:
        # 辞書形式などが混ざっていても確実に文字列として処理
        title_raw = p.get('title') or ""
        abstract_raw = p.get('abstract') or ""
        
        title = str(title_raw).lower()
        abstract = str(abstract_raw).lower()
        content = title + " " + abstract
        
        p_tags = p.get('tags', [])
        if not isinstance(p_tags, list): p_tags = []
        if "PubMed" in p_tags: p_tags.remove("PubMed")
        
        found_any = False
        for cat, keywords in categories.items():
            if any(kw in content for kw in keywords):
                if cat not in p_tags: p_tags.append(cat)
                topic_counts[cat] += 1
                found_any = True
        
        if not found_any:
            if "基礎研究" not in p_tags: p_tags.append("基礎研究")
        
        p['tags'] = p_tags

    # トピック統計を更新
    data['global_topic_stats'] = topic_counts
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 分析完了。")
    for cat, count in topic_counts.items():
        print(f"  🔹 {cat}: {count} 件")

if __name__ == "__main__":
    finalize_intelligence_analysis()
