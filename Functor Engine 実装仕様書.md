## 1. 基本方針

- **Client-Server分離:** ロジックの中核を**FastAPI**でAPIサーバー化し、UI層（**Streamlit**）と疎結合にする。
    
- **Interactive Visualization:** **PyVis**を用い、ブラウザ上で「世界観の圏構造」を物理演算付きで動的に可視化する。
    
- **Stateless Core:** APIサーバーは原則ステートレス（またはメモリ内キャッシュ）で設計し、リクエストごとに圏論的変換を行う。
    

## 2. 技術スタック

| **レイヤー**     | **技術・ライブラリ**            | **役割**                                  |
| ------------ | ----------------------- | --------------------------------------- |
| **Langage**  | **Python 3.11+**        | 構造的パターンマッチ、型ヒントの簡素化、高速化                 |
| **Frontend** | **Streamlit**           | ユーザーインターフェース。チャット画面、設定パネル。              |
| **Viz**      | **PyVis**               | NetworkXのグラフ構造をHTML/Canvasとしてレンダリング。    |
| **Backend**  | **FastAPI**             | REST APIサーバー。圏論モデルの構築と変換ロジックの提供。        |
| **Logic**    | **NetworkX**            | 圏（Category）のデータ構造管理。                    |
| **AI**       | **LangChain / LiteLLM** | LLMプロバイダ（OpenAI/Anthropic）への統一インターフェース。 |
| **Comm**     | **Requests / Pydantic** | フロント-バック間の通信とデータバリデーション。                |
### 推奨構成

```requirements.txt
fastapi
uvicorn         # FastAPIサーバー起動用
streamlit
networkx
langchain
langchain-openai
langchain-anthropic
pydantic
requests
```
---

## 3. システムアーキテクチャ

v2.0の「Core」部分をFastAPIでラップし、HTTP経由でStreamlitから操作する構成です。

コード スニペット

```
graph LR
    subgraph "Frontend Container (Streamlit)"
        UI[Web UI]
        Viz[PyVis Component]
        API_Client[API Client Wrapper]
    end

    subgraph "Backend Container (FastAPI)"
        Server[API Server]
        WorldMgr[World Manager]
        GraphDB[(NetworkX Graph)]
        RAG[Graph RAG Engine]
    end
    
    User((User)) --> UI
    UI -- "Render" --> Viz
    UI -- "User Input" --> API_Client
    API_Client -- "POST /translate" --> Server
    API_Client -- "POST /world/load" --> Server
    
    Server --> WorldMgr
    WorldMgr --> GraphDB
    Server --> RAG
    RAG -- "Query Context" --> GraphDB
    RAG -- "Generate" --> LLM[External AI API]
```

---

## 4. データモデル設計 (Shared)

FastAPIとStreamlitの両側で共通認識を持つためのデータ定義（Pydanticモデル）です。

Python

```
from pydantic import BaseModel
from typing import List, Dict, Optional

# ノード（概念）
class WorldNode(BaseModel):
    id: str
    label: str
    description: str
    type: str = "concept" # concept, place, person...

# エッジ（射・法則）
class Morphism(BaseModel):
    source: str
    target: str
    label: str # 関係性の名前
    rule: str  # 変換ルール

# APIリクエスト/レスポンス定義
class TranslationRequest(BaseModel):
    text: str
    world_id: str # 複数の世界を切り替える場合用

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    applied_laws: List[str] # 変換に使われた法則のリスト（根拠提示）

class GraphDataResponse(BaseModel):
    nodes: List[Dict]
    edges: List[Dict]
    # PyVis/Vis.js形式のデータ構造
```

---

## 5. APIエンドポイント定義 (FastAPI)

バックエンドが提供すべき主要な機能です。

### A. 世界観管理

- `POST /world/initialize`
    
    - 入力: 世界観の定義テキスト（Markdown/YAML）
        
    - 処理: LLMで解析し、NetworkXグラフを構築してメモリ（またはDB）に保存。
        
    - 出力: `world_id` とノード数などの統計情報。
        
- `GET /world/{world_id}/graph`
    
    - 処理: 現在のNetworkXグラフを、PyVisで描画可能なJSON形式（Nodes/Edgesリスト）に変換して返す。
        
    - 用途: Streamlit側でのグラフ描画用。
        

### B. 変換機能 (Functor Engine)

- `POST /translate`
    
    - 入力: `TranslationRequest` (原文)
        
    - 処理:
        
        1. 原文からキーワード抽出。
            
        2. グラフ内を検索（Graph RAG）。
            
        3. 関連する法則（射）を取得。
            
        4. LLMで書き換え実行。
            
    - 出力: `TranslationResponse`
        

---

## 6. Frontend実装詳細 (Streamlit)

Streamlitは、APIを叩いて結果を表示する「View」に徹します。

### 画面レイアウト案

- **サイドバー:**
    
    - Backend URL設定
        
    - 世界観ファイルアップロード or テキスト入力エリア
        
    - 「世界観ロード」ボタン
        
- **メインエリア (2カラム構成):**
    
    - **Left: Translation (Chat)**
        
        - テキスト入力ボックス
            
        - 変換ボタン
            
        - 結果表示（原文 vs 翻訳文）
            
        - _Accordion:_ 「適用された法則（Show Logic）」
            
    - **Right: World Visualization**
        
        - 世界観ロード直後や、更新ボタン押下時にAPIからグラフデータを取得。
            
        - PyVisで生成したHTMLを `st.components.v1.html()` で埋め込み表示。
            

---
## 7. データ構造設計（Pydantic & NetworkX）

Haskellではなく、PythonのPydanticモデルとNetworkXグラフで定義します。

### 7.1. 圏のオブジェクトと射 (Domain Layer)

Python

```
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 1. 対象（Object）: 世界を構成する概念・実体
class WorldObject(BaseModel):
    id: str
    name: str
    description: str
    meta: Dict[str, str] = Field(default_factory=dict) # 拡張用メタデータ

    def __hash__(self):
        return hash(self.id)

# 2. 射（Morphism）: オブジェクト間の関係性・法則
class Morphism(BaseModel):
    source: str  # WorldObject.id
    target: str  # WorldObject.id
    name: str    # 関係性ラベル (例: "is ruled by")
    rule: str    # 変換ルール・法則記述 (例: "Authority flows strictly top-down")

# 3. 圏（Category）: NetworkXグラフのラッパー
import networkx as nx

class CategoryGraph:
    def __init__(self):
        # 有向多重グラフ（同じノード間に複数の関係性を許容）
        self.graph = nx.MultiDiGraph()

    def add_object(self, obj: WorldObject):
        self.graph.add_node(obj.id, data=obj)

    def add_morphism(self, morph: Morphism):
        self.graph.add_edge(
            morph.source, 
            morph.target, 
            label=morph.name, 
            rule=morph.rule
        )
    
    def get_context(self, obj_id: str) -> str:
        """指定された概念周辺の法則（射）をテキスト化して取得（RAG用）"""
        # NetworkXの近傍探索で関連する法則を取得
        edges = self.graph.out_edges(obj_id, data=True)
        context = []
        for u, v, data in edges:
            context.append(f"- {data['label']}: {data['rule']} (-> {v})")
        return "\n".join(context)
        # core/graph.py (v2.0ベース + v3.0用拡張)
    
    # Web表示用にデータをJSON化するメソッド
    def export_for_vis(self) -> Dict[str, List[Dict[str, Any]]]:
        """PyVis / Vis.js が読み込める形式でノードとエッジを返す"""
        nodes = []
        for n_id, attrs in self.graph.nodes(data=True):
            # data属性に入っている Pydanticモデルを展開
            obj_data = attrs['data'] 
            nodes.append({
                "id": n_id,
                "label": obj_data.name,
                "title": obj_data.description, # マウスオーバーで説明表示
                "group": "object" # 色分け用
            })

        edges = []
        for u, v, key, attrs in self.graph.edges(keys=True, data=True):
            edges.append({
                "from": u,
                "to": v,
                "label": attrs.get('label', ''),
                "title": attrs.get('rule', '') # マウスオーバーで法則表示
            })
            
        return {"nodes": nodes, "edges": edges}
```

---

## 8. 処理フロー設計

### Phase 1: 世界観のロード (World Loading)

1. ユーザーが世界観資料（Markdown/JSON）を指定。
    
2. `WorldLoader` がLLMを使用して、テキストから `WorldObject` と `Morphism` を抽出。
    
3. 抽出データを `CategoryGraph` (NetworkX) に構築。これを「並行世界圏（Target World）」とする。
    

### Phase 2: 変換実行 (Functor Execution)

構築したグラフが消えないようにFastAPI の `Lifespan` (起動時イベント) やグローバル変数で管理する。

```python
# backend/main.py のイメージ

from fastapi import FastAPI
from core.graph import CategoryGraph
from core.functor import FunctorEngine

app = FastAPI()

# グローバルな状態として保持（簡易実装版）
# 本番運用ではデータベースなどを使いますが、個人ツールならメモリ保持で十分です
STATE = {
    "graph": CategoryGraph(),
    "engine": None
}

@app.post("/world/initialize")
async def initialize_world(config: str):
    # 1. グラフ構築 (v2.0のロジック)
    STATE["graph"] = build_graph_from_text(config)
    
    # 2. エンジン初期化 (v2.0のロジック)
    STATE["engine"] = FunctorEngine(STATE["graph"], llm_client)
    
    return {"status": "initialized", "nodes": len(STATE["graph"].nodes)}

@app.post("/translate")
async def translate(request: TranslationRequest):
    if not STATE["engine"]:
        return {"error": "World not loaded"}
    
    # v2.0のGraph RAGロジックを呼び出す
    result = await STATE["engine"].translate_text(request.text)
    return {"result": result}
```

ここが「Graph RAG」の本質部分。

```python
class FunctorEngine:
    def __init__(self, category: CategoryGraph, llm_client):
        self.category = category
        self.llm = llm_client

    async def translate_text(self, input_text: str) -> str:
        # 1. 入力文から概念抽出 (Entity Extraction)
        #    例: "A cat is sleeping on the sofa." -> ["cat", "sofa", "sleeping"]
        entities = await self._extract_entities(input_text)
        
        # 2. 概念マッピング (Structure Mapping)
        #    入力概念に最も近い「並行世界の概念」をグラフから検索
        #    例: "cat" -> "Bio-Construct (Pet)"
        mapped_infos = []
        for entity in entities:
            target_node_id = self._find_nearest_node(entity)
            if target_node_id:
                # 3. 文脈取得 (Context Retrieval)
                #    その概念に適用される「法則（射）」を取得
                laws = self.category.get_context(target_node_id)
                mapped_infos.append(f"Concept '{entity}' maps to '{target_node_id}' under laws:\n{laws}")
        
        # 4. 生成 (Generation)
        #    集めた法則コンテキストをもとにリライト
        prompt = f"""
        Original Text: {input_text}
        
        Apply the following World Laws to rewrite the text:
        {mapped_infos}
        
        Output in the style of the target world.
        """
        return await self.llm.generate(prompt)

```

---

## 9. ディレクトリ構成案

フロントエンドとバックエンドを明確に分けます。

Plaintext

```
functor_engine_web/
├── docker-compose.yml         # (Option) 一括起動用
├── backend/                   # FastAPI
│   ├── main.py                # アプリ起動・ルーティング
│   ├── requirements.txt
│   ├── core/
│   │   ├── graph_logic.py     # NetworkX操作
│   │   ├── llm_service.py     # LangChain連携
│   │   └── models.py          # Pydanticモデル
│   └── routers/
│       └── api.py             # エンドポイント実装
│
└── frontend/                  # Streamlit
    ├── app.py                 # UIメインロジック
    ├── requirements.txt
    └── utils/
        ├── api_client.py      # backendへのリクエスト処理
        └── viz_helper.py      # PyVis設定・HTML生成ヘルパー
```

---

## 10. 実装ロードマップ（推奨手順）

この構成であれば、以下の順序で開発するとスムーズです。

1. **Backend Core (Logic):**
    
    - `backend/core/` を作成。
        
    - Markdownを読み込んでNetworkXグラフを作る部分だけ実装し、printデバッグで確認。
        
2. **Backend API (FastAPI):**
    
    - `backend/main.py` を作成し、CoreロジックをAPI経由で呼べるようにする。
        
    - Swagger UI (`http://localhost:8000/docs`) でAPIの動作確認をする。
        
3. **Frontend Viz (PyVis):**
    
    - Streamlitで、適当なダミーデータをPyVisで表示できるか試す。
        
4. **Frontend Integration:**
    
    - StreamlitからFastAPIへ `requests.post` を投げ、帰ってきたデータを表示するように繋ぎこむ。
        

### 開発者へのメモ：PyVisとStreamlitの連携のコツ

PyVisはデフォルトでHTMLファイルをディスクに書き出します。Streamlitで表示する際は、以下のようなヘルパー関数を作ると便利です。

Python

```
# frontend/utils/viz_helper.py
from pyvis.network import Network
import streamlit.components.v1 as components

def render_graph(nodes, edges):
    net = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
    # データ追加処理...
    
    # ファイルに書き出さず、HTML文字列として取得して埋め込むトリック
    try:
        # PyVisのバージョンによって書き方が異なる場合がありますが、
        # 一旦tmpファイルに保存して読み込むのが一番確実です
        net.save_graph("temp_graph.html") 
        with open("temp_graph.html", 'r', encoding='utf-8') as f:
            source_code = f.read()
        components.html(source_code, height=510)
    except Exception as e:
        st.error(f"Graph rendering failed: {e}")
```


