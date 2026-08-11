import os
import streamlit as st
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Gemini Creative Studio",
    page_icon="🧠",
    layout="wide"
)

# 2. Safe API Key Retrieval
api_key = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    st.error("⚠️ API Key missing! Add `GEMINI_API_KEY` to `.streamlit/secrets.toml` or enter it in the sidebar.")
    st.stop()

# 3. Initialize Google GenAI Client
@st.cache_resource
def get_client(key: str):
    return genai.Client(api_key=key)

client = get_client(api_key)

if "generated_text" not in st.session_state:
    st.session_state.generated_text = None

# 4. Styling
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0b0d19, #1a163a, #071c35, #0a0f1d) !important;
    background-size: 400% 400% !important;
    animation: gradientMotion 12s ease infinite !important;
    font-family: 'Inter', sans-serif;
}

@keyframes gradientMotion {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.hero {
    text-align: center;
    padding: 2.5rem 2rem;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
}

.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.hero p {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-top: 0.5rem;
}

.stButton > button {
    width: 100%;
    border: none !important;
    border-radius: 12px !important;
    height: 50px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease-in-out !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(168, 85, 247, 0.6) !important;
}
</style>
""", unsafe_allow_html=True)

# 5. Hero Banner
st.markdown("""
<div class="hero">
    <h1>🧠 Gemini Creative Studio</h1>
    <p>Deploy cutting-edge AI engine modeling to generate modern web copy and articles instantly.</p>
</div>
""", unsafe_allow_html=True)

# 6. Stream Content Generator with Active Model Endpoint Fallbacks
def stream_content(prompt: str, content_type: str, tone: str, length: str):
    prompts = {
        "Blog": (
            f"Write a complete, comprehensive, and highly detailed {length.lower()} blog post in a {tone.lower()} tone "
            f"about the topic: {prompt}.\n\n"
            f"Structure your entire output strictly as follows:\n"
            f"Title\n\nIntroduction\n\nSection 1 (with heading)\n\nSection 2 (with heading)\n\n"
            f"Section 3 (with heading)\n\nConclusion\n\n"
            f"Do not use raw markdown markup elements like hashes (#) or asterisks (*). Make the article rich and completely structured."
        ),
        "Instagram Caption": f"Write an engaging {tone.lower()} Instagram caption containing native expressive emojis and hashtags for the topic: {prompt}",
        "Product Description": f"Write a {length.lower()} high-converting product description in a {tone.lower()} tone highlighting advanced features, values, and key consumer benefits for: {prompt}",
        "Email": f"Write a complete {length.lower()} professional email sequence in a {tone.lower()} tone with a clear subject line, structured email body, and call-to-action block for: {prompt}"
    }

    # List of active endpoints to try sequentially
    candidate_models = ["gemini-3.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
    
    response = None
    last_error = None

    for model_name in candidate_models:
        try:
            response = client.models.generate_content_stream(
                model=model_name,
                contents=prompts[content_type],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1500
                )
            )
            break
        except Exception as e:
            last_error = e
            continue

    if response is not None:
        try:
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"❌ Error: {str(e)}"
    else:
        yield f"❌ Error initializing model: {str(last_error)}"

# 7. Dashboard Layout
layout_left, layout_right = st.columns([1.1, 1.4], gap="large")

with layout_left:
    st.markdown("### 🎛️ Engine Workspace")
    
    prompt = st.text_area(
        "Context Input & Core Topic",
        placeholder="Describe what you want to create (e.g., The future of quantum computing in web design)...",
        height=150
    )
    
    c1, c2 = st.columns(2)
    with c1:
        content_type = st.selectbox("Format Style", ["Blog", "Instagram Caption", "Product Description", "Email"])
        length = st.selectbox("Length Scale", ["Short", "Medium", "Long"])
    with c2:
        tone = st.selectbox("Voice Tone", ["Professional", "Friendly", "Creative", "Formal"])
        
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Execute Architecture", use_container_width=True)

# 8. Output Display Terminal
with layout_right:
    st.markdown("### 🖥️ Display Terminal")
    
    if generate_btn:
        if prompt.strip():
            with st.spinner("Compiling structural content parameters..."):
                full_response = st.write_stream(stream_content(prompt, content_type, tone, length))
                st.session_state.generated_text = full_response
        else:
            st.warning("⚠️ Terminal requires an active topic footprint input.")

    elif st.session_state.generated_text:
        st.markdown(st.session_state.generated_text)

    if st.session_state.generated_text and not st.session_state.generated_text.startswith("❌"):
        result = st.session_state.generated_text
        st.markdown("<br>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Words Created", len(result.split()))
        m2.metric("Characters", len(result))
        m3.metric("Asset Classification", content_type)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Export Text Asset",
            data=result,
            file_name=f"asset_{content_type.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

st.markdown("""
---
<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>Powered by Streamlit Framework & Google Gemini Engine Workspace</p>
""", unsafe_allow_html=True)