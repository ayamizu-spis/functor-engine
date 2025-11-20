import streamlit as st
from utils.api_client import APIClient
from utils.viz_helper import render_graph
import io

# Page Config
st.set_page_config(
    page_title="Functor Engine",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main background and text color */
    .stApp {
        background: radial-gradient(circle, #1c1a47 0%, #0f0e26 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f0e26;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #514fd3;
        color: white;
        border: none;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #8e3cd8;
    }
    
    /* Text Areas and Inputs */
    .stTextArea textarea {
        background-color: #2a2859;
        color: white;
        border: 1px solid #514fd3;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: #2a2859;
        color: #c0c0e0;
        border-radius: 8px 8px 0 0;
        padding: 0 24px;
        font-weight: 600;
        border: 1px solid #514fd3;
        border-bottom: none;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #514fd3;
        color: white;
        border-color: #8e3cd8;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3a3869;
        color: white;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Initialize API Client
# Assuming backend is running on localhost:8000
api = APIClient(base_url="http://localhost:8000")

# --- Sidebar: World Management ---
st.sidebar.title("🔮 Functor Engine Info")

st.sidebar.markdown("---")
st.sidebar.subheader("初期情報")
if st.sidebar.button("初期化"):
    # Reset logic if needed, for now just a placeholder or re-init graph
    st.sidebar.info("Initialization requested...")
st.sidebar.info("Initialized Status: " + ("Ready" if "error" not in api.get_graph_data() else "Not Ready"))

st.sidebar.markdown("---")
st.sidebar.subheader("疎通確認")
if st.sidebar.button("実行"):
    graph_data = api.get_graph_data()
    if "error" in graph_data:
        st.sidebar.error("Connection Failed")
        st.sidebar.info(f"Categorize Test: Failed")
        st.sidebar.info(f"Generated Test: Failed")
    else:
        st.sidebar.success("Connection OK")
        st.sidebar.info(f"Categorize Test: OK ({len(graph_data.get('nodes', []))} nodes)")
        st.sidebar.info(f"Generated Test: OK")

st.sidebar.markdown("---")
st.sidebar.subheader("Github Repository")
st.sidebar.link_button("Link", "https://github.com/ayamizu-spis/functor-engine") # Placeholder link

# --- Main Area ---
st.title("🔮 Functor Engine")
st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

# --- Column 1: World Definition ---
with col1:
    st.subheader("１．世界観を定義")
    
    col1tab1, col1tab2 = st.tabs(["文章" ,"ファイル"])
    with col1tab1:
        world_def_input = st.text_area(
            "Worldを定義する文章を入力してください",
            height=300,
            placeholder="例:\nエーテルランド王国では魔法はクリスタルスパイアから流れています。国王は鉄腕で統治していますが、赤のバラの反乱は成長しています..."
        )
        if st.button("Worldを初期化"):
            if not world_def_input.strip():
                st.warning("Worldを定義する文章を入力してください。")
            else:
                with st.spinner("Worldを初期化中..."):
                    result = api.initialize_world(world_def_input)
                    if "error" in result:
                        st.error(f"失敗: {result['error']}")
                    else:
                        st.success(f"Worldを初期化しました! ({result.get('nodes', 0)}概念を生成しました)")

    with col1tab2:
        uploaded_files = st.file_uploader("Markdownファイルをアップロード", type="md", accept_multiple_files=True, key="world_files")
        if uploaded_files:
            combined_text = ""
            for uploaded_file in uploaded_files:
                stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                combined_text += f"\n\n# File: {uploaded_file.name}\n{file_content}"
            
            st.text_area("Preview (Combined)", combined_text, height=150, disabled=True)
            
            if st.button("Worldを初期化"):
                with st.spinner("Worldを初期化中..."):
                    result = api.initialize_world(combined_text)
                    if "error" in result:
                        st.error(f"失敗: {result['error']}")
                    else:
                        st.success(f"Worldを初期化しました! ({result.get('nodes', 0)}概念を生成しました)")

    st.info("File Status: " + ("Loaded" if "error" not in api.get_graph_data() else "Empty"))

# --- Column 2: Transformation Target ---
with col2:
    st.subheader("２．変換対象")
    col2tab1, col2tab2, col2tab3 = st.tabs(["文章" ,"ファイル" ,"画像"])
    
    target_text = ""
    
    with col2tab1:
        input_text_area = st.text_area("文章を入力してください:", height=150, placeholder="例:\nご飯を買いにコンビニへ行った。")
        if input_text_area:
            target_text = input_text_area

    with col2tab2:
        input_files = st.file_uploader("Markdownファイルをアップロード", type="md", accept_multiple_files=True, key="target_files")
        if input_files:
            for input_file in input_files:
                stringio = io.StringIO(input_file.getvalue().decode("utf-8"))
                target_text += stringio.read() + "\n\n"
            st.text_area("Preview", target_text, height=100, disabled=True)
        st.info("File Status: " + ("Ready" if target_text else "Waiting"))

    with col2tab3:
        st.warning("実装予定 (Image Input)")

    st.markdown("---")
    on = st.toggle("拡張機能", False, key="expand")
    if on:
        st.slider("世界観の影響度", 1, 100, 100, key="effort")
        st.slider("時系列の進行度", 1, 100, 1, key="timeline")

# --- Column 3: Generation Result ---
with col3:
    st.subheader("３．生成結果")
    
    if st.button("文章を生成", type="primary"):
        if not target_text.strip():
            st.warning("文章を入力してください。または、ファイルをアップロードしてください。")
        else:
            with st.spinner("文章を生成中..."):
                result = api.translate(target_text)
                
                if "error" in result:
                    st.error(f"文章生成に失敗しました: {result['error']}")
                else:
                    st.success("文章生成に成功しました!")
                    st.markdown("### 生成結果")
                    st.markdown(f"> {result['translated_text']}")
                    
                    with st.expander("適用された法則を表示"):
                        for law in result.get('applied_laws', []):
                            st.text(law)
                            
    st.markdown("---")
    st.subheader("World Graph")
    if st.button("Refresh Graph"):
        st.rerun()
        
    graph_data = api.get_graph_data()
    error_msg = render_graph(graph_data)
    if error_msg:
        st.error(error_msg)
