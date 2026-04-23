import json
import os
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# Path configuration
JSON_PATH = 'data/latest_papers.json'
LIMIT = 5000  # Number of papers to translate in this run

# Medical glossary for consistent translation
GLOSSARY = {
    "polyphosphate": "ポリリン酸",
    "poly-p": "ポリリン酸",
    "osseointegration": "オッセオインテグレーション",
    "bone regeneration": "骨再生",
    "whitening": "ホワイトニング",
    "short-chain": "短鎖",
    "divided polyphosphate": "分割ポリリン酸",
    "periodontal disease": "歯周病",
    "bone quality": "骨質",
}

def apply_glossary(text):
    if not text: return ""
    for en, jp in GLOSSARY.items():
        text = text.replace(en.capitalize(), jp).replace(en, jp)
    return text

def translate_missing():
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: {JSON_PATH} not found.")
        return

    print(f"📖 Loading database...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data.get('papers', [])
    
    # 1. Identify papers missing translation
    # 2. Sort by year desc and PMID desc to ensure "LATEST" are prioritized
    untranslated = []
    for p in papers:
        if not p.get('jp_title') or len(p.get('jp_title', '')) < 3:
            untranslated.append(p)

    def sort_key(p):
        year = p.get('year') or p.get('date', '1900')
        pmid = p.get('id', '0')
        # Extract 4-digit year
        import re
        match = re.search(r'\d{4}', str(year))
        year_num = int(match.group()) if match else 1900
        return (year_num, int(pmid) if pmid.isdigit() else 0)

    untranslated.sort(key=sort_key, reverse=True)

    count = len(untranslated)
    print(f"🔍 Found {count} untranslated papers. Processing up to {LIMIT} latest papers...")

    translator = GoogleTranslator(source='auto', target='ja')
    success_count = 0

    for i, p in enumerate(untranslated[:LIMIT]):
        try:
            title = p.get('title', '')
            abstract = p.get('abstract', '')
            
            print(f"[{i+1}/{LIMIT}] Translating PMID: {p.get('id')} ({p.get('year')})")
            
            # Translate title
            if title:
                p['jp_title'] = apply_glossary(translator.translate(title))
            
            # Translate abstract (summary)
            if abstract:
                # Use part of abstract for summary if too long
                target_abstract = abstract[:500]
                p['summary_jp'] = apply_glossary(translator.translate(target_abstract))
            
            success_count += 1
            
            # Auto-save every 10 papers to prevent data loss
            if success_count % 10 == 0:
                with open(JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"💾 Autosaved ({success_count} translated)")

            time.sleep(0.5) # Avoid hitting API limits
            
        except Exception as e:
            print(f"⚠️ Error translating {p.get('id')}: {e}")
            time.sleep(5) # Wait longer on error
            continue

    # Final save
    data['generated_at'] = datetime.now().strftime("%Y-%m-%d")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✨ Success! Translated {success_count} papers.")

if __name__ == "__main__":
    translate_missing()
