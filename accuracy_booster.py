import json
import os
import re
from datetime import datetime

# --- 高精度オントロジーの定義 ---
# 単純なキーワードマッチではなく、コンテキスト（文脈）を考慮するための定義
PRECISION_MAP = {
    "ホワイトニング": {
        "positive": ["whitening", "bleaching", "stain", "discoloration", "hydrogen peroxide", "hydroxyl radical"],
        "negative": ["white blood cell", "leukocyte", "white matter", "white adipose", "white shark"] # 誤爆防止
    },
    "ミトコンドリア・代謝": {
        "positive": ["mitochondria", "mtpyp", "atp", "energy metabolism", "oxidative stress", "respiration"],
        "negative": ["wastewater", "sludge"]
    },
    "インプラント": {
        "positive": ["implant", "osseointegration", "peri-implant", "abutment", "fixture"],
        "negative": ["implantable device", "cochlear implant"] # ペースメーカーなどは除外（必要に応じて）
    },
    "歯周病・口腔": {
        "positive": ["periodontal", "periodontitis", "gingiva", "gingivitis", "p. gingivalis", "pocket", "oral biofilm", "stomatology", "pulp", "caries", "tooth", "teeth", "dental", "dentistry", "alveolar", "endodontic", "orthodontic"],
        "negative": []
    },
    "骨再生・硬組織": {
        "positive": ["bone regeneration", "osteogenesis", "bone morphogenetic", "osteoblast", "osteoclast", "alveolar bone", "bone density"],
        "negative": []
    },
    "再生医療": {
        "positive": ["regenerative", "stem cell", "scaffold", "tissue engineering", "differentiation"],
        "negative": []
    },
    "創傷治癒": {
        "positive": ["wound healing", "angiogenesis", "epithelial", "fibroblast", "repair"],
        "negative": []
    },
    "環境・排水処理（ノイズ候補）": {
        "positive": ["wastewater", "sludge", "pollution", "phosphorus removal", "activated sludge", "bioreactor"],
        "positive": ["wastewater", "sludge", "pollution", "phosphorus removal", "activated sludge", "bioreactor", "flame retardancy", "smoke suppression"],
        "negative": ["clinical", "human", "patient", "oral", "tooth"]
    }
}

# 歯科・医学専門用語の補正マップ
DENTAL_TERM_FIX = {
    "キャッピング": "覆髄",
    "パルプ": "歯髄",
    "歯のホワイトニング": "歯冠ホワイトニング",
    "歯科用インプラント": "歯科インプラント",
    "骨の再生": "骨再生",
    "歯の周囲": "歯周",
    "に関連しています": "との関連",
    "明らかになりました": "の解明",
}

def clean_japanese_grammar(text, is_title=False):
    """
    です・ます調をである調に変換し、学術的な響きにする
    """
    if not text: return text
    
    # 1. 代名詞や直訳調の言い回しを学術的表現に変換
    text = text.replace("私たち", "我々")
    text = text.replace("ここで、", "本研究では、")
    text = text.replace("ここでは、", "本研究では、")
    text = text.replace("ここで", "本研究では")
    text = text.replace("そして、", "さらに、")
    
    # 2. 一般的な変換（順序が重要：長いものから先に置換）
    text = re.sub(r"([をがに])明らかになりました", r"\1明らかにした", text)
    text = re.sub(r"([をがに])明らかにしました", r"\1明らかにした", text)
    text = text.replace("に関連しています", "に関連する")
    text = text.replace("に関連があります", "に関連がある")
    text = text.replace("明らかになりました", "明らかになった")
    text = text.replace("明らかにしました", "明らかにした")
    text = text.replace("報告しました", "報告した")
    text = text.replace("特定しました", "特定した")
    text = text.replace("示唆しています", "を示唆している")
    text = text.replace("制御します", "を制御する")
    text = text.replace("促進します", "を促進する")
    text = text.replace("寄与します", "に寄与する")
    text = text.replace("あります。", "ある。")
    text = text.replace("います。", "いる。")
    text = text.replace("しました。", "した。")
    text = text.replace("でした。", "であった。")
    text = text.replace("なります。", "なる。")
    text = text.replace("研究です。", "研究である。")
    
    # 連続する助詞を1つに圧縮（以前のバグで増殖した「ををを」等を一掃）
    text = re.sub(r"を+", "を", text)
    text = re.sub(r"が+", "が", text)
    text = re.sub(r"の+", "の", text)
    text = re.sub(r"て+", "て", text)
    text = re.sub(r"に+", "に", text)
    text = re.sub(r"は+", "は", text)
    text = re.sub(r"で+", "で", text)
    
    # 3. 「を使用して」などの不自然な接続の補正
    # 文頭にある場合は削除（英語タイトルが 'using' 等で途切れている場合の翻訳エラー対策）
    if text.startswith("を使用して"):
        text = text[5:]
    elif text.startswith("を使用し、"):
        text = text[5:]
    elif text.startswith("を用いた"):
        text = text[4:]
    elif text.startswith("を用い、"):
        text = text[4:]
    
    text = text.replace("を使用して", "を用いた")
    text = text.replace("を使用し、", "を用い、")
    text = text.replace("をを用いた", "を用いた")
    text = text.replace("をの調査", "の調査")
    text = text.replace("をの検討", "の検討")
    
    # 助詞の連続や不自然な空白の削除
    text = text.replace(" I​​ ", " ")
    text = text.replace(" 、", "、").replace(" 。", "。")
    
    for en, jp in DENTAL_TERM_FIX.items():
        text = text.replace(en, jp)

    if is_title:
        # タイトル固有の処理（体言止め・学術的語尾）
        text = re.sub(r"の解明$", "に関する研究", text)
        text = re.sub(r"の特定$", "の同定", text)
        text = re.sub(r"を?調査する$", "の調査", text)
        text = re.sub(r"を?検討する$", "の検討", text)
        text = re.sub(r"を?評価する$", "の評価", text)
        text = re.sub(r"を?分析する$", "の分析", text)
        text = re.sub(r"を?開発する$", "の開発", text)
        text = re.sub(r"を?制御する$", "の制御", text)
        text = re.sub(r"を?明らかにする$", "の解明", text)
        text = re.sub(r"を?評価します$", "の評価", text)
        text = re.sub(r"を?分析します$", "の分析", text)
        text = re.sub(r"を?調査します$", "の調査", text)
        text = re.sub(r"を?検討します$", "の検討", text)
        text = re.sub(r"を?報告します$", "の報告", text)
        text = re.sub(r"します$", "する", text)
        text = re.sub(r"れます$", "れる", text)
        text = re.sub(r"います$", "いる", text)
        text = re.sub(r"ります$", "る", text)
        
        # さらに文頭の不自然な助詞の削除
        text = re.sub(r"^[をにがはで]", "", text)
        
        text = text.strip().rstrip("。")
    
    return text

def calculate_relevance_score(paper):
    """
    論文の歯科・医科的価値をスコアリングする
    """
    content = f"{paper.get('title','')} {paper.get('abstract','')}".lower()
    score = 0
    
    # 歯科・医科関連キーワードでの加点
    if any(k in content for k in ["dental", "oral", "tooth", "teeth", "periodontal", "gingiva"]):
        score += 50
    if any(k in content for k in ["bone", "regeneration", "stem cell", "clinical", "human", "patient"]):
        score += 30
        
    # 環境・工業系キーワードでの減点（ノイズ除去）
    if any(k in content for k in ["wastewater", "sludge", "detergent", "laundry", "pollution"]):
        score -= 60
        
    # ポリリン酸への言及
    if "polyphosphate" in content or "poly-p" in content:
        score += 20
        
    return score

def boost_accuracy():
    json_path = "data/latest_papers.json"
    if not os.path.exists(json_path):
        print("❌ Error: latest_papers.json not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])
    print(f"🚀 {len(papers)}件のデータを精密分析中...")

    dental_count = 0
    noise_count = 0
    updated_titles = 0

    for p in papers:
        # 1. 日本語タイトルの補正
        orig_title = p.get('jp_title', '')
        if orig_title:
            new_title = clean_japanese_grammar(orig_title, is_title=True)
            if new_title != orig_title:
                p['jp_title'] = new_title
                updated_titles += 1
        
        # 2. 要約文の補正（です・ます調の排除）
        orig_summary = p.get('summary_jp', '')
        if orig_summary:
            p['summary_jp'] = clean_japanese_grammar(orig_summary, is_title=False)
        
        orig_html = p.get('summary_html', '')
        if orig_html:
            p['summary_html'] = clean_japanese_grammar(orig_html, is_title=False)

        # 3. 精密カテゴリ分類
        content = f"{p.get('title','')} {p.get('abstract','')} {p.get('jp_title','')}".lower()
        new_tags = set()
        
        for category, rules in PRECISION_MAP.items():
            # ポジティブキーワードが含まれ、かつネガティブキーワードが含まれない場合のみタグ付け
            if any(pos in content for pos in rules['positive']):
                if not any(neg in content for neg in rules['negative']):
                    new_tags.add(category)
        
        p['tags'] = sorted(list(new_tags))
        
        # 3. スコアリングとフラグ立て
        score = calculate_relevance_score(p)
        p['relevance_score'] = score
        
        # 歯科フラグの厳格化
        is_dental = "歯周病・口腔" in new_tags or "インプラント" in new_tags or "ホワイトニング" in new_tags
        p['is_dental'] = is_dental
        if is_dental: dental_count += 1
        
        # ノイズ（環境系など）を非表示にするフラグ
        if score < 0:
            p['is_hidden'] = True
            noise_count += 1
        else:
            p['is_hidden'] = False

    # 保存
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    data['last_accuracy_boost'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✨ 精度向上プロセス完了:")
    print(f"   - 学術的表現へ補正したタイトル: {updated_titles}件")
    print(f"   - 歯科関連として特定: {dental_count}件")
    print(f"   - ノイズ（工業・環境系）として判定: {noise_count}件")

if __name__ == "__main__":
    boost_accuracy()
