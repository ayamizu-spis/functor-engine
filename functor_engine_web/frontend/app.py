import streamlit as st
from utils.api_client import APIClient
from utils.viz_helper import render_graph

# Page Config
st.set_page_config(
    page_title="Functor Engine",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API Client
# Assuming backend is running on localhost:8000
api = APIClient(base_url="http://localhost:8000")

# --- Sidebar: World Management ---
st.sidebar.title("🔮 Functor Engine")
st.sidebar.markdown("---")

st.sidebar.header("1. World Initialization")
world_def_input = st.sidebar.text_area(
    "Define your World (Text/Markdown)",
    height=200,
    placeholder="Example:\nIn the Kingdom of Aethelgard, magic flows from the Crystal Spire. The King rules with an iron fist, but the Rebellion of the Red Rose is growing..."
)

if st.sidebar.button("Initialize World"):
    if not world_def_input.strip():
        st.sidebar.error("Please enter a world description.")
    else:
        with st.sidebar.status("Initializing World..."):
            result = api.initialize_world(world_def_input)
            if "error" in result:
                st.sidebar.error(f"Failed: {result['error']}")
            else:
                st.sidebar.success(f"World Initialized! ({result.get('nodes', 0)} concepts found)")

st.sidebar.markdown("---")
st.sidebar.info("Backend Status: " + ("Online" if "error" not in api.get_graph_data() else "Offline"))

# --- Main Area ---
st.title("World Translator")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("2. Reality Input")
    input_text = st.text_area("Enter text to translate:", height=150, placeholder="I went to the convenience store to buy some rice balls.")
    
    if st.button("Translate to World"):
        if not input_text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Consulting the Laws of the World..."):
                result = api.translate(input_text)
                
                if "error" in result:
                    st.error(f"Translation Failed: {result['error']}")
                else:
                    st.success("Translation Complete!")
                    st.markdown("### Result")
                    st.markdown(f"> {result['translated_text']}")
                    
                    with st.expander("See Applied Laws"):
                        for law in result.get('applied_laws', []):
                            st.text(law)

with col2:
    st.subheader("3. World Visualization")
    if st.button("Refresh Graph"):
        st.rerun()
        
    graph_data = api.get_graph_data()
    error_msg = render_graph(graph_data)
    if error_msg:
        st.error(error_msg)
