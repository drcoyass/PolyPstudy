import json
import os

def finalize_intelligence_analysis():
    json_path = '/Users/coyass/kaihatsu/Poly-Pstudy/data/latest_papers.json'
    
    if not os.path.exists(json_path):
        print("❌ データベースが見つかりません。")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    papers = data.get('papers', [])
    print(f"🧠 {len(papers)}件の全論文を詳細インテリジェンス分析中...")

    # 「1クリックで知りたい情報にたどり着く」ための極細カテゴリー定義
    categories = {
        "ホワイトニング": ["whitening", "bleaching", "discoloration", "stain", "color", "白", "漂白"],
        "ミトコンドリア": ["mitochondria", "mtpyp", "atp", "metabolism", "energy production", "energy metabolism"],
        "インプラント": ["implant", "osseointegration", "abutment", "implantology"],
        "歯周組織再生": ["periodontal", "periodontitis", "pdl", "gingiva", "alveolar bone", "歯周", "歯肉"],
        "骨代謝・再生": ["regeneration", "bone morphogenetic", "osteoblast", "osteoclast", "mineralization", "scaffold", "骨"],
        "創傷治癒": ["wound healing", "angiogenesis", "epithelial", "cell migration", "repair", "傷"],
        "抗労働・長寿": ["longevity", "anti-aging", "senescence", "life span", "stress resistance", "長寿", "老化"],
        "細胞増殖": ["proliferation", "differentiation", "stem cell", "growth factor", "分化"],
        "感染・炎症性": ["inflammation", "infection", "cytokine", "immune response", "bacterial", "炎症"],
        "歯科一般": ["dental", "dentist", "caries", "orthodontic", "endodontic", "pulp", "歯科", "歯筋"],
        "基礎医学": ["cancer", "tumor", "drug delivery", "protein", "enzyme", "mapping", "signaling"]
    }

    topic_counts = {cat: 0 for cat in categories}
    
    for p in papers:
        # タイトル、抄録、既存タグ、日本語要約をすべてスキャン
        text = f"{p.get('title','')} {p.get('jp_title','')} {p.get('abstract','')} {p.get('summary_jp','')}".lower()
        
        p_tags = []
        found_any = False
        
        for cat, keywords in categories.items():
            if any(kw in text for kw in keywords):
                p_tags.append(cat)
                topic_counts[cat] += 1
                found_any = True
        
        if not found_any:
            p_tags.append("その他")
        
        p['tags'] = list(set(p_tags)) # 重複排除

    # グローバル統計を更新
    data['global_topic_stats'] = topic_counts
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ 分析完了。")
    for cat, count in topic_counts.items():
        print(f"  🔹 {cat}: {count} 件")

if __name__ == "__main__":
    finalize_intelligence_analysis()
