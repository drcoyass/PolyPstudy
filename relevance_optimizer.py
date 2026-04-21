import json
import os

# 19,000件の論文データに対して、歯科・医学的な整合性を高めるためのオントロジー定義
DENTAL_ONTOLOGY = {
    "歯周病": ["periodontal", "periodontitis", "gingiva", "gingivitis", "p. gingivalis", "pocket"],
    "インプラント": ["implant", "osseointegration", "peri-implant", "abutment"],
    "ホワイトニング": ["whitening", "bleaching", "stain", "discoloration", "hydrogen peroxide"],
    "骨再生・代謝": ["bone regeneration", "osteogenesis", "bone morphogenetic", "osteoblast", "osteoclast", "alveolar bone", "bone density", "bone quality"],
    "抗菌・除菌": ["antibacterial", "antimicrobial", "bactericidal", "biofilm", "pathogen", "infection"],
    "再生医療": ["regenerative", "stem cell", "scaffold", "tissue engineering"],
    "ミトコンドリア": ["mitochondria", "atp", "energy metabolism", "oxidative stress"],
    "創傷治癒": ["wound healing", "epithelial", "fibroblast"],
    "短鎖分割ポリリン酸": ["short-chain", "chain length", "low molecular weight polyphosphate"]
}

CATEGORY_MAP = {
    "DENTAL": ["periodontal", "implant", "dental", "tooth", "teeth", "oral", "gingiva", "bleaching", "whitening", "caries", "orthodontic"],
    "MEDICAL": ["cancer", "tumor", "heart", "brain", "bone", "kidney", "liver", "mitochondria", "blood", "vessel"]
}

JSON_PATH = 'data/latest_papers.json'

def optimize_relevance():
    if not os.path.exists(JSON_PATH):
        print("❌ Error: latest_papers.json not found.")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])
    print(f"🚀 {len(papers)}件の論文を徹底リサーチ中...")

    dental_count = 0
    updated_tags_count = 0

    for p in papers:
        def to_str(val):
            if isinstance(val, str): return val
            if isinstance(val, dict): return json.dumps(val, ensure_ascii=False)
            return str(val) if val is not None else ""

        title = (to_str(p.get('title', '')) + " " + to_str(p.get('jp_title', ''))).lower()
        abstract = to_str(p.get('abstract', '')).lower()
        content = title + " " + abstract

        # 1. 歯科・医科のカテゴリ自動分類の強化
        is_dental = any(word in content for word in CATEGORY_MAP["DENTAL"])
        if is_dental:
            p['is_dental'] = True
            dental_count += 1
        
        # 2. 日本語タグの自動付与（マッピングによる生合成向上）
        new_tags = set(p.get('tags', []))
        for tag, keywords in DENTAL_ONTOLOGY.items():
            if any(k in content for k in keywords):
                new_tags.add(tag)
        
        if len(new_tags) > len(p.get('tags', [])):
            p['tags'] = list(new_tags)
            updated_tags_count += 1

        # 3. 歯科重要100選（DENTAL 100）の自動抽出ロジック（暫定）
        if is_dental and ("polyphosphate" in content) and ("regeneration" in content or "whitening" in content or "periodontal" in content):
            p['is_dental_top_100'] = True

    # 保存
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✨ 整合性向上プロセス完了:")
    print(f"   - 歯科関連として特定: {dental_count}件")
    print(f"   - 日本語タグ付与/更新: {updated_tags_count}件")

if __name__ == "__main__":
    optimize_relevance()
