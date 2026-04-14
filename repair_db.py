import json
import os
import re

DB_PATH = '/Users/coyass/kaihatsu/Poly-Pstudy/data/latest_papers.json'

def repair_json():
    if not os.path.exists(DB_PATH):
        print("❌ データベースが見つかりません。")
        return

    print(f"🔧 データベース {DB_PATH} の構造を検証・修復中...")
    
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except Exception as e:
        print(f"❌ ファイルの読み込みに失敗しました: {e}")
        return

    # 1. 不完全な末尾の修復 (JSONが途中で切れている場合)
    if not raw_content.strip().endswith('}'):
        print("⚠️  不完全なJSON末尾を検出しました。修復を試みます...")
        # 最後の有効な論文オブジェクトを特定し、構造を閉じる
        last_success = raw_content.rfind('},')
        if last_success != -1:
            repaired = raw_content[:last_success+1] + "]\n}"
            raw_content = repaired

    # 2. 構文エラーのチェックと強制デコード
    try:
        # まずは普通に読み込んでみる
        data = json.loads(raw_content)
        print("✅ JSONの構造は正常でした。")
    except json.JSONDecodeError as e:
        print(f"⚠️  エラー箇所を特定しました {e.lineno}行目付近。自動修復を試みます...")
        
        # エラー箇所の前後を直接修復する高度な正規表現（クォートの漏れや無効なエスケープの修正）
        # ※ 1.9万件の巨大ファイルのため、一度文字列レベルでノイズを除去
        lines = raw_content.split('\n')
        err_line_idx = e.lineno - 1
        
        if err_line_idx < len(lines):
            # 前後3行を表示
            print("--- エラー箇所の生データ ---")
            for i in range(max(0, err_line_idx-1), min(len(lines), err_line_idx+2)):
                print(f"{i+1}: {lines[i]}")
            
            # クォートのエスケープミスなどを修正
            lines[err_line_idx] = lines[err_line_idx].replace('\\"', '"').replace('"', '\\"').replace(':\\"', ':"').replace('\\",', '",')
            
            # 再構築して試行
            try:
                data = json.loads('\n'.join(lines))
                print("✅ 自動修復に成功しました！")
            except:
                print("❌ 高度な修復が必要なため、ファイルを一旦バックアップして再構築を検討します。")
                return

    # 正常なデータを書き戻す
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✨ データベースの修復が完了しました。")

if __name__ == "__main__":
    repair_json()
