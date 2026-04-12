import json
import os

# 翻訳・修正データ定義
TRANSLATIONS = {
    "41733679": {
        "jp_title": "無機ポリリン酸とアルカリフォスファターゼ/アデニレートキナーゼ：生理的ATP依存性創傷修復の鍵となる構成要素とその作用機序",
        "summary_jp": "本研究は、無機ポリリン酸（polyP）が創傷治癒における生理的エネルギー供給源としての役割を詳述している。具体的には、細胞外ATPの産生に関与するアルカリフォスファターゼ（ALP）およびアデニレートキナーゼ（AK）との相互作用を解明。polyPが単なる保存物質ではなく、細胞の代謝エネルギー（ATP）を直接的に供給し、創傷修復プロセスを加速させる『代謝的プロモーター』であることを証明している。",
        "summary_html": "<b>【代謝的エネルギー供給源としてのポリリン酸】</b><br>ポリリン酸が細胞外バイオエネルギープールとして機能し、ALPおよびAKを介してATPを産生。これにより、エネルギー要求の高い創傷修復プロセスが生理的に強化されるメカニズムを解説している。"
    },
    "41733680": {
        "jp_title": "電離放射線によるDNA損傷と皮膚傷害：創傷治癒への戦略的アプローチ",
        "summary_jp": "電離放射線への曝露が引き起こす深刻な皮膚損傷（放射線皮膚症）のメカニズムと、その修復プロセスに関する包括的レビュー。放射線による活性酸素（ROS）の発生とマクロ分子の損傷を抑制する新素材として、ポリリン酸を中心に解説。ポリリン酸の優れた再生活性バイオポリマーとしての側面を強調し、放射線治療における副作用の軽減や、偶発的曝露からの迅速な創傷治癒の可能性を提示している。",
        "summary_html": "<b>【放射線皮膚損傷に対する再生医療的アプローチ】</b><br>放射線によるDNA二重鎖切断やアポトーシスを抑制するための再生バイオポリマーとしてポリリン酸を紹介。放射線損傷からの組織修復を加速させる分子メカニズムを詳述。"
    },
    "31009177": {
        "jp_title": "ヒト血液白血球のブルシャイト、モネタイト、およびカルシウムポリリン酸バイオマテリアルに対する異なる反応",
        "summary_jp": "歯科インプラントや骨補填材として期待されるカルシウムポリリン酸（CPP）などのバイオマテリアルに対する、ヒト血液白血球の免疫反応を比較・分析した研究。CPPが炎症性サイトカインの放出を制御しつつ、骨形成に有利な環境を構築することを示唆。オッセオインテグレーション（骨結合）の向上における、マテリアル選択のバイオロジカルな重要性を論じている。",
        "summary_html": "<b>【インプラント周囲組織における免疫反応の制御】</b><br>バイオマテリアルに対する白血球の応答を検証。カルシウムポリリン酸が、炎症制御と骨再生のバランスを最適化する次世代のインプラント素材としての有効性を提示している。"
    }
}

def update_json_professional():
    json_path = "data/latest_papers.json"
    if not os.path.exists(json_path):
        print("❌ JSON file not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    for p in data['papers']:
        pid = str(p.get('id'))
        if pid in TRANSLATIONS:
            trans = TRANSLATIONS[pid]
            p['jp_title'] = trans['jp_title']
            p['summary_jp'] = trans['summary_jp']
            p['summary_html'] = trans['summary_html']
            # abstractも日本語に置き換える（ユーザーの要望通り）
            p['abstract'] = trans['summary_jp'] 
            updated_count += 1
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✨ Successfully updated {updated_count} papers with professional medical/scientific Japanese.")

if __name__ == "__main__":
    update_json_professional()
