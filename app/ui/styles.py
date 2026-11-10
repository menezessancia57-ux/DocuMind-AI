import streamlit as st


def load_styles():
    st.markdown("""
    <style>
      .stApp { background: #f7f9fc; color: #243044; }
      [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5eaf1; }
      .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
      h1, h2, h3 { color: #172033; letter-spacing: 0; }
      .app-header { border-bottom: 1px solid #dde3ec; padding-bottom: 1rem; margin-bottom: 1rem; }
      .subtitle { color: #64748b; margin-top: -0.4rem; }
      .metric-card { background: white; border: 1px solid #e1e7ef; border-radius: 8px; padding: 18px; min-height: 112px; }
      .metric-card strong { color: #1d4ed8; font-size: 1.65rem; display:block; }
      .source-card { background:white; border:1px solid #dde5ef; border-left:3px solid #2563eb; border-radius:8px; padding:16px; margin-bottom:12px; }
      .status-badge { background:#eaf2ff; color:#1e40af; border-radius:999px; padding:5px 10px; font-size:0.82rem; font-weight:600; }
      .answer-box { background:white; border:1px solid #dfe6ef; border-radius:8px; padding:20px; line-height:1.65; }
      .workflow { color:#475569; background:white; border:1px solid #e1e7ef; border-radius:8px; padding:14px 18px; }
      div[data-testid="stMetric"] { background:white; border:1px solid #e1e7ef; border-radius:8px; padding:14px; }
      button[kind="primary"] { background:#2563eb; border-color:#2563eb; }
      .stTabs [data-baseweb="tab-list"] { gap:12px; }
    </style>
    """, unsafe_allow_html=True)
