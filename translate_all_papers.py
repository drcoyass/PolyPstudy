import json
import os
import time
from deep_translator import GoogleTranslator
from datetime import datetime

# 医学専門用語の補正マップ（科学的に正しい表現へ強制変換）
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "polyphosphates": "ポリリン酸塩",
    "inorganic polyphosphate": "無機ポリリン酸",
    "long-chain": "長鎖",
    "short-chain": "短鎖",
    "osseointegration": "オッセオインテグレーション（骨結合）",
    "bone regeneration": "骨再生",
    "mitochondria": "ミトコンドリア",
    "adenosine triphosphate": "アデノシン三リン酸（ATP）",
    "angiogenesis": "血管新生",
    "alkaline phosphatase": "アルカリフォスファターゼ（ALP）",
    "periodontal": "歯周組織の",
    "osteoblast": "骨芽細胞",
    "biomaterial": "バイオマテリアル（生体材料）",
    "regenerative medicine": "再生医療",
}

def medical_polish(text):
    """
    自動翻訳後のテキストを医学・科学用語集に基づいて補正する
    """
    if not text: return ""
    for en, jp in GLOSSARY.items():
        # 大文字小文字を区別せず、自然な日本語に補正
        text = text.replace(en.capitalize(), jp)
        text = text.replace(en, jp)
    return text

def translate_all_papers():
    json_path = "data/latest_papers.json"
    if not os.path.exists(json_path):
        print("❌ JSON file not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    translator = GoogleTranslator(source='auto', target='ja')
    
    total = len(data['papers'])
    print(f"🚀 全 {total} 件の論文を医学的日本語へ自動翻訳中...")
    
    # 翻訳済みのものをスキップするか、全件上書きするか
    # 今回は効率のため「まだ翻訳されていないもの」または「英語のもの」を対象にします
    updated_count = 0
    
    # 時間がかかるため、まずは重要論文（先頭100件やインプラント、TOP100等）を優先することも可能です
    # ここでは全体の流れを示し、まずは直近の重要論文を優先処理します
    for i, p in enumerate(data['papers']):
        # すべてやると数時間かかるため、まずは上位500件を優先的に高品質化
        if i >= 500: break 
        
        # 既に高品質な日本語がある場合はスキップ（手動修正分を保護）
        if p.get('summary_jp') and len(p['summary_jp']) > 50:
            continue
            
        abstract = p.get('abstract', "")
        if abstract and len(abstract) > 10:
            try:
                # 翻訳実行
                translated = translator.translate(abstract)
                # 医学用語補正
                p['summary_jp'] = medical_polish(translated)
                p['jp_title'] = medical_polish(translator.translate(p.get('title', '')))
                
                # ポータル表示用
                p['summary_html'] = f"<b>【AI専門翻訳】</b><br>{p['summary_jp'][:250]}..."
                
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"📦 {i+1}/{total} 件完了...")
                    # API制限回避のための微小待機
                    time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ {p['id']} の翻訳中にエラー: {e}")
                continue

    # 最終的な保存
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✨ 合計 {updated_count} 件の論文が医学的日本語へアップデートされました！")

if __name__ == "__main__":
    translate_all_papers()
