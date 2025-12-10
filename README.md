# Functor Engine

**「現実の事象を、任意の異世界の法則・文化・価値観に合わせて再定義（翻訳）するシステム」**

Google翻訳が「日本語を英語に」変換するように、Functor Engineは「現実の風景や文章を、ファンタジーやSFの世界観（ロア）に」変換します。

## 🎯 コアバリュー

創作活動において、特定の世界観に沿ったアセットやテキストを大量に用意することは困難です。

Functor Engineは、**「たった一つの世界観資料」**さえあれば、手元のあらゆる写真やメモをその世界の一部として自動的に書き換えることで、クリエイターの世界構築（World Building）を強力に支援します。

## ✨ 主要機能

### 1. 世界観の構造化（World Modeling）
- ユーザーが用意したテキスト（設定資料、プロット、メモ）を読み込み
- その世界の「物理法則」「社会構造」「人間関係」「固有名詞」を構造データとして抽出・学習
- **論理的な関係性（ルール）**をグラフ構造として理解

### 2. 意味的翻訳（Semantic Translation）
- 入力された現実のデータ（テキスト・画像）を、学習した世界観のルールに従って変換
- 表面的な言葉の置換ではなく、**概念レベルでの変換**を実現

**例:**
- _入力:_ 「コンビニでおにぎりを買った」（現実）
- _世界観:_ ディストピアSF
- _出力:_ 「配給所で合成炭水化物バーの割り当てを受領した」

### 3. インタラクティブな世界観可視化
- NetworkXとPyVisによる世界観のグラフ構造の可視化
- 概念間の関係性を物理演算付きで動的に表示

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────┐
│  Frontend (Streamlit)           │
│  - UI/UX                        │
│  - PyVis Visualization          │
└────────────┬────────────────────┘
             │ HTTP/REST
┌────────────▼────────────────────┐
│  Backend (FastAPI)              │
│  - Functor Engine (Graph RAG)   │
│  - CategoryGraph (NetworkX)     │
│  - LLM Integration (LangChain)  │
└─────────────────────────────────┘
```

### 技術スタック
- **Language:** Python 3.11+
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Graph:** NetworkX
- **Visualization:** PyVis
- **AI:** LangChain + Google Gemini
- **Data:** Pydantic

## 🚀 セットアップ

### 前提条件
- Python 3.11以上
- Google Gemini API Key

### 1. リポジトリをクローン
```bash
git clone <repository-url>
cd FunctorEngine
```

### 2. 環境変数の設定
プロジェクトルートに `Gemini.env` を作成:
```env
GEMINI_API_KEY=your_api_key_here
```

### 3. バックエンドのセットアップ
```bash
cd functor_engine_web/backend
pip install -r requirements.txt
```

### 4. フロントエンドのセットアップ
```bash
cd ../frontend
pip install -r requirements.txt
```

## 📦 起動方法

### バックエンドを起動
```bash
cd functor_engine_web/backend
uvicorn main:app --reload
```
→ http://localhost:8000 でAPIが起動

### フロントエンドを起動
```bash
cd functor_engine_web/frontend
streamlit run app.py
```
→ http://localhost:8501 でUIが起動

## 📖 使い方

1. **Define (定義):**
   - サイドバーから世界観のテキストを入力
   - 「Initialize World」ボタンをクリック

2. **Input (入力):**
   - 変換したい現実のテキストを入力

3. **Generate (生成):**
   - 「Translate to World」ボタンで変換実行
   - 右側で世界観グラフを可視化

## 🎮 ユースケース

- **VRChat / メタバース:** 現実の写真を、アバターが住む世界の風景に変換
- **ゲーム開発:** 現代劇のシナリオをファンタジー/SF版に翻訳
- **TRPG:** プレイヤーの行動を世界観に沿った描写に即座に変換

## 📁 プロジェクト構成

```
FunctorEngine/
├── functor_engine_web/
│   ├── backend/
│   │   ├── core/
│   │   │   ├── models.py           # Pydanticモデル
│   │   │   ├── graph_logic.py      # NetworkXグラフ管理
│   │   │   └── llm_service.py      # Functor Engine本体
│   │   ├── main.py                 # FastAPI エントリーポイント
│   │   └── requirements.txt
│   └── frontend/
│       ├── utils/
│       │   ├── api_client.py       # Backend API クライアント
│       │   └── viz_helper.py       # PyVis可視化ヘルパー
│       ├── app.py                  # Streamlit UI
│       └── requirements.txt
├── Functor Engine 概要説明書.md
├── Functor Engine 実装仕様書.md
└── README.md
```

## 🔬 技術的背景

本システムは**圏論（Category Theory）**の概念に基づいています:
- **対象（Object）**: 世界を構成する概念・実体
- **射（Morphism）**: 概念間の関係性・法則
- **関手（Functor）**: 現実世界から並行世界への構造保存写像

詳細は [Functor Engine 実装仕様書.md](Functor%20Engine%20実装仕様書.md) を参照してください。

## 📝 ライセンス

MIT License
