import streamlit as st
from .styles import load_styles


def render_header(mode: str):
    st.markdown("<div class='app-header'><h1>DocuMind AI</h1><div class='subtitle'>Intelligent Document Search and Question Answering</div></div>", unsafe_allow_html=True)
    st.markdown(f"<span class='status-badge'>● {mode} mode</span>", unsafe_allow_html=True)


def render_result(result: dict):
    score = result.get("score", 0.0)
    st.markdown(f"""
    <div class='source-card'>
      <strong>{result.get('filename', 'Unknown')} · Page {result.get('page_number', '?')}</strong>
      <div style='color:#64748b;font-size:0.85rem;margin:5px 0;'>Similarity: {score:.3f}</div>
      <div>{result.get('text', '')[:320]}{'...' if len(result.get('text', '')) > 320 else ''}</div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("View complete chunk"):
        st.write(result.get("text", ""))
