import json
import os
import re
from datetime import datetime

def repair_json(path):
    print(f"🛠 {path} の解析と修復を開始します...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ ファイルの読み込みに失敗しました: {e}")
        return False

    # 1. 隣接するオブジェクト間のカンマ漏れを修正 ( } {  ->  }, { )
    content = re.sub(r'}\s*\n\s*{', '},\n {', content)
    
    # 2. 配列の閉じ忘れや不要なカンマの修正（簡易的な試み）
    try:
        data = json.loads(content)
        print("✅ JSONは正常な構造に復元されました。")
    except json.JSONDecodeError as e:
        print(f"⚠️ まだエラーが残っています（{e}）。強制的な末尾補正を試みます...")
        # エラー箇所の手前までで有効なJSONとして切り出す（荒療治）
        try:
            # line 233832 column 56 のような形式から位置を特定する
            # 今回は単純に、最後の正常な } ] } を探して補完します
            if '"papers": [' in content:
                parts = content.split('"papers": [')
                header = parts[0] + '"papers": ['
                papers_content = parts[1]
                # 最後の } で終わる部分までを抽出
                last_valid_paper = papers_content.rfind('}')
                fixed_papers = papers_content[:last_valid_paper+1]
                content = header + fixed_papers + "\n  ]\n}"
                data = json.loads(content)
                print("✨ データの末尾を補正し、正常なJSONとして復元しました。")
            else:
                raise Exception("JSONの基本構造が見つかりません。")
        except Exception as e2:
            print(f"❌ 致命的なエラー: 修復できませんでした。再同期が必要です。 ({e2})")
            return False

    # 保存
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

def run_all():
    json_path = "data/latest_papers.json"
    
    # 手順1: 修復
    if repair_json(json_path):
        print("🚀 修復完了。続いて月次レポートの生成を開始します...")
        # 手順2: レポート生成スクリプトを呼び出す
        try:
            import generate_monthly_report
            generate_monthly_report.create_monthly_report()
            print("🏆 すべての工程が正常に完了しました！")
        except Exception as e:
            print(f"❌ レポート生成中にエラーが発生しました: {e}")
    else:
        print("❌ 修復に失敗したため、処理を中断しました。")

if __name__ == "__main__":
    run_all()
