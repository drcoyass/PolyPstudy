import json
import os
import time
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

# 設定
JSON_PATH = 'data/latest_papers.json'
MAX_WORKERS = 10 # 同時接続数

# 専門用語辞書（翻訳の質を維持）
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "poly-p": "ポリリン酸",
    "osseointegration": "オッセオインテグレーション",
    "mitochondria": "ミトコンドリア",
    "regeneration": "再生",
    "implants": "インプラント",
    "periodontitis": "歯周炎",
    "bleaching": "ホワイトニング",
    "short-chain": "短鎖",
}

def apply_glossary(text):
    if not text: return text
    for en, jp in GLOSSARY.items():
        text = text.replace(en.capitalize(), jp).replace(en, jp)
    return text

def translate_item(item):
    translator = GoogleTranslator(source='en', target='ja')
    changed = False
    
    # タイトルの翻訳
    if not item.get('jp_title'):
        try:
            translated = translator.translate(item.get('title', ''))
            item['jp_title'] = apply_glossary(translated)
            changed = True
        except:
            pass

    # 抄録（要約）の翻訳
    if not item.get('summary_jp'):
        try:
            # 抄録が長すぎる場合は先頭の重要部分のみ要約として翻訳（高速化・品質維持）
            abstract = item.get('abstract', '')
            if len(abstract) > 5:
                # 最初の200文字程度を要約の対象にする
                target_text = abstract[:500]
                translated = translator.translate(target_text)
                item['summary_jp'] = apply_glossary(translated)
                changed = True
        except:
            pass
            
    return changed

def run_mass_translation():
    if not os.path.exists(JSON_PATH):
        print("❌ データベースが見つかりません。")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])
    total = len(papers)
    # 未翻訳分を抽出
    pending = [p for p in papers if not p.get('jp_title') or not p.get('summary_jp')]
    
    print(f"🚀 全 {total} 件中、未翻訳の {len(pending)} 件を処理します...")

    batch_size = 50
    for i in range(0, len(pending), batch_size):
        batch = pending[i:i+batch_size]
        print(f"   📥 バッチ処理中 ({i+1}/{len(pending)})...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(translate_item, batch)
        
        # 50件ごとに保存（安全のため）
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        time.sleep(1) # API制限を考慮

    print("✨ 全件の日本語化・要約が完了しました！")

if __name__ == "__main__":
    run_mass_translation()
