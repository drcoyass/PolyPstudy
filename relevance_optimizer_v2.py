import json
import os

DENTAL_ONTOLOGY = {
    "歯周病": ["periodontal", "periodontitis", "gingiva", "gingivitis", "p. gingivalis", "pocket", "alveolar bone"],
    "インプラント": ["implant", "osseointegration", "peri-implant", "abutment"],
    "ホワイトニング": ["whitening", "bleaching", "stain", "discoloration"],
    "骨再生・代謝": ["bone regeneration", "osteogenesis", "osteoblast", "osteoclast", "bone quality"],
    "抗菌・除菌": ["antibacterial", "antimicrobial", "biofilm", "pathogen"],
    "再生医療": ["regenerative", "stem cell", "scaffold", "tissue engineering"],
    "ミトコンドリア": ["mitochondria", "atp", "energy metabolism"],
    "短鎖分割ポリリン酸": ["short-chain", "chain length", "low molecular weight polyphosphate"]
}

JSON_PATH = 'data/latest_papers.json'

def optimize():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    papers = data['papers']
    updated = 0
    
    for p in papers:
        def to_str(v): return str(v).lower() if v else ""
        content = to_str(p.get('title')) + " " + to_str(p.get('abstract')) + " " + to_str(p.get('jp_title'))
        
        tags = set(p.get('tags', []))
        orig_len = len(tags)
        
        for tag, keywords in DENTAL_ONTOLOGY.items():
            if any(k in content for k in keywords):
                tags.add(tag)
        
        if len(tags) > orig_len:
            p['tags'] = list(tags)
            updated += 1
            if updated <= 5:
                print(f"DEBUG: Tagged {p.get('id')} with {p['tags']}")

        # Ensure is_dental flag
        if any(k in content for k in ["dental", "oral", "tooth", "teeth", "periodontal"]):
            p['is_dental'] = True

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Processes {len(papers)} papers, updated {updated} papers with new semantic tags.")

if __name__ == "__main__":
    optimize()
