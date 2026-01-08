import streamlit as st
import modules.quant_a as quant_a
import modules.quant_b as quant_b
import yfinance as yf
import os
import glob

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QuantDashboard", 
    layout="wide", 
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. DESIGN TECH / DARK (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* FOND GENERAL */
    .stApp {
        background: radial-gradient(circle at center, #1b202c 0%, #0e1117 100%);
    }

    /* --- CORRECTION BANDE NOIRE & MARGES --- */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        margin-top: 0 !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    .main-title {
        font-size: 80px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: -2px;
        line-height: 1.2;
    }

    .sub-title {
        text-align: center;
        font-size: 24px;
        color: #a0aec0;
        margin-bottom: 50px;
    }

    .ticker-box {
        background-color: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 0 auto 40px auto;
        width: 60%; 
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.1); 
    }

    .ticker-price {
        font-size: 40px;
        font-weight: bold;
        color: #FAFAFA;
        font-family: 'Courier New', monospace; 
    }

    .module-card {
        background: linear-gradient(145deg, #1A202C, #171923);
        border-radius: 20px;
        padding: 40px;
        border: 1px solid #2D3748;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }

    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border-color: #3a7bd5;
    }

    .card-icon { font-size: 60px; margin-bottom: 20px; }
    .card-title { font-size: 30px; font-weight: bold; color: white; margin-bottom: 15px; }
    .card-desc { font-size: 16px; color: #A0AEC0; margin-bottom: 30px; }

    div.stButton > button {
        background: linear-gradient(90deg, #3a7bd5 0%, #00d2ff 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
        width: 100%;
        transition: transform 0.1s, box-shadow 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        color: white;
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
    }
    
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. LOGIQUE & FONCTIONS
# -----------------------------------------------------------------------------
if 'page' not in st.session_state: st.session_state.page = 'home'
def go_home(): st.session_state.page = 'home'
def go_quant_a(): st.session_state.page = 'quant_a'
def go_quant_b(): st.session_state.page = 'quant_b'

@st.cache_data(ttl=30)
def get_btc_data():
    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="2d")
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        delta = ((current - prev) / prev) * 100
        return current, delta
    except:
        return 0.0, 0.0

# -----------------------------------------------------------------------------
# 4. AFFICHAGE
# -----------------------------------------------------------------------------

# --- ACCUEIL ---
if st.session_state.page == 'home':
    
    st.markdown('<div class="main-title">QUANT TERMINAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Advanced Analytics & Portfolio Management</div>', unsafe_allow_html=True)

    price, delta = get_btc_data()
    color = "#48BB78" if delta >= 0 else "#F56565"
    sign = "+" if delta >= 0 else ""

    st.markdown(f"""
    <div class="ticker-box">
        <span style="color: #A0AEC0; font-size: 18px; margin-right: 15px;">BITCOIN LIVE FEED</span>
        <br>
        <span class="ticker-price">{price:,.2f} $</span>
        <span style="color: {color}; font-size: 22px; font-weight: bold; margin-left: 15px;">
            {sign}{delta:.2f}%
        </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="module-card">
            <div class="card-icon">📈</div>
            <div class="card-title">Market Analyst</div>
            <div class="card-desc">
                Analyse technique approfondie du Bitcoin.<br>
                Détection de tendances & Moyennes Mobiles.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("OUVRIR ANALYSE", on_click=go_quant_a, key="btn_a")

    with col2:
        st.markdown("""
        <div class="module-card">
            <div class="card-icon">🏦</div>
            <div class="card-title">Portfolio Manager</div>
            <div class="card-desc">
                Stratégie multi-actifs (Crypto, Actions, Or).<br>
                Matrice de corrélation & Gestion des risques.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.button("OUVRIR PORTEFEUILLE", on_click=go_quant_b, key="btn_b")

    # --- RAPPORTS AUTOMATIQUES ---
    st.markdown("---")
    st.header("📊 Daily Automation Reports")
    
    # Chercher les fichiers générés par cron sur la VM
    report_files = glob.glob("rapport_*.txt")
    report_files.sort(reverse=True) # Les plus récents en premier

    if report_files:
        selected_report = st.selectbox("Consulter l'historique des rapports :", report_files)
        with open(selected_report, "r") as f:
            st.code(f.read(), language="text")
    else:
        st.info("ℹ️ Les rapports automatisés apparaîtront ici après l'exécution de la tâche cron (20h00).")


# --- MODULES ---
elif st.session_state.page == 'quant_a':
    col_nav, _ = st.columns([1, 8])
    with col_nav: st.button("⬅ RETOUR", on_click=go_home)
    st.markdown("---")
    quant_a.run()

elif st.session_state.page == 'quant_b':
    col_nav, _ = st.columns([1, 8])
    with col_nav: st.button("⬅ RETOUR", on_click=go_home)
    st.markdown("---")
    quant_b.run()