# Poly-Pstudy | ポリリン酸研究会 インテリジェンス・ポータル

![Aesthetic Research Hub](https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&q=80&w=1200)

## 🧬 プロジェクト概要
世界中のポリリン酸（Polyphosphate / Poly-P）に関する学術研究を24時間監視し、AIによって抽出・構造化された知見を提供する次世代の研究知能プラットフォームです。

生命の起源（40億年前）から、現代の歯科臨床における骨再生・抗菌応用まで、人類が蓄積してきたポリリン酸の英知を網羅します。

### 🚀 主な機能
- **Global Archive**: PubMed, J-Stage, CiNiiから4,000件以上の最新論文をインデックス（全2万件まで順次拡張中）。
- **Dental 100**: 歯科臨床に直結する重要論文100選をAIが精密解析し、日本語要約を付与。
- **Intelligence Dashboard**: 世界の研究トレンドとキーワード推移をリアルタイムに可視化。
- **Auto Report Generation**: 毎月、最新研究の要約をPowerPoint形式で自動生成。

## 🛠 テクノロジー
- **Frontend**: HTML5, Vanilla CSS (Premium Glassmorphism Design), JavaScript
- **Backend (Automation)**: Python (PubMed E-Utilities API, OpenAI GPT-4o API)
- **Deployment**: GitHub Pages

## 📦 運用方法
1. 最新データの同期（ローカル）:
```bash
python3 monthly_slide_generator.py
```
2. HPへの反映（公開）:
```bash
git add data/latest_papers.json
git commit -m "Update research database"
git push origin main
```

---
© 2026 分割ポリリン酸 研究会 | Powered by PolyP Intelligence Hub
