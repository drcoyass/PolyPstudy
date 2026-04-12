import json
import os
import time
from deep_translator import GoogleTranslator
from datetime import datetime

# 医学専門用語の補正マップ
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "polyphosphates": "ポリリン酸塩",
    "inorganic polyphosphate": "無機ポリリン酸",
    "osseointegration": "オッセオインテグレーション（骨結合）",
    "bone regeneration": "骨再生",
    "adenosine triphosphate": "アデノシン三リン酸（ATP）",
    "periodontal": "歯周組織の",
    "osteoblast": "骨芽細胞",
}

def medical_polish(text):
    if not text: return ""
    for en, jp in GLOSSARY.items():
        text = text.replace(en.capitalize(), jp)
        text = text.replace(en, jp)
    return text

def translate_intelligent():
    json_path = "data/latest_papers.json"
    if not os.path.exists(json_path):
        print("❌ JSON file not found at data/latest_papers.json")
        return

    print("📖 データを読み込み中...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])
    total = len(papers)
    print(f"🚀 高精度・優先翻訳エンジン起動: 全 {total} 件をスキャン中...")

    # 1. 優先順位付け（インプラント・歯科・最新順）
    def priority_score(p):
        score = 0
        tags = p.get('tags', [])
        if "インプラント" in tags: score += 100
        if "歯科・口腔" in tags: score += 50
        year = p.get('year', '1900')
        try: score += (int(year) - 1900) * 0.1
        except: pass
        return score

    # 優先順位でソート
    papers.sort(key=priority_score, reverse=True)

    translator = GoogleTranslator(source='auto', target='ja')
    updated_count = 0
    limit = 1000 # 1回の実行でまずは1000件を優先翻訳

    for i, p in enumerate(papers):
        if updated_count >= limit: break
        
        # 既に高品質な翻訳がある（日本語タイトルがある）場合はスキップ
        if p.get('jp_title') and len(p['jp_title']) > 5:
            continue
            
        abstract = p.get('abstract', "")
        if abstract and len(abstract) > 10:
            try:
                # 抄録とタイトルの翻訳
                p['summary_jp'] = medical_polish(translator.translate(abstract))
                p['jp_title'] = medical_polish(translator.translate(p.get('title', '')))
                p['summary_html'] = f"<b>【プレミアム翻訳】</b><br>{p['summary_jp'][:300]}..."
                
                updated_count += 1
                if updated_count % 5 == 0:
                    print(f"✅ [{p.get('year')}] {p.get('id')} ({p.get('tags', [''])[0]}) を翻訳完了... ({updated_count}/{limit})")
                    # 保存（こまめに保存して事故を防ぐ）
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                
                time.sleep(0.3)
            except Exception as e:
                print(f"⚠️ {p.get('id')} でエラー: {e}")
                time.sleep(2) # 制限時は長めに待機
                continue

    # 最終保存
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 優先翻訳完了！ 合計 {updated_count} 件の重要論文が日本語化されました。")

if __name__ == "__main__":
    translate_intelligent()
