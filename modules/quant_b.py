import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

def run():

    st.markdown('<div class="main-title">PORTFOLIO MANAGER</div>', unsafe_allow_html=True)

    # 1. Sélecteur d'actifs (L'utilisateur choisit son équipe)
    st.info("Sélectionne les actifs pour composer ton portefeuille.")
    
    tickers = st.multiselect(
        "Choix des actifs :",
        ["BTC-USD", "ETH-USD", "AAPL", "MSFT", "GOOGL", "TSLA", "GC=F", "EURUSD=X"], 
        default=["BTC-USD", "AAPL", "GC=F"] # Par défaut : Crypto, Tech, Or (GC=F)
    )

    if len(tickers) < 2:
        st.warning("⚠️ Sélectionne au moins 2 actifs pour comparer.")
        return

    # 2. Récupération des données
    try:
        # On télécharge tout d'un coup
        data = yf.download(tickers, period="2y", interval="1d")['Close']
    except Exception as e:
        st.error(f"Erreur de téléchargement : {e}")
        return

    if data.empty:
        st.error("Aucune donnée disponible.")
        return

    # 3. Normalisation (Base 100)
    # Formule : (Prix / Prix Initial) * 100
    # Cela permet de comparer des pommes (Apple) et des oranges (Bitcoin)
    normalized_data = data / data.iloc[0] * 100

    st.subheader("Performance Comparée (Base 100)")
    st.line_chart(normalized_data)

    # 4. Analyse des Risques (Matrice de Corrélation)
    st.subheader("🕵️‍♂️ Analyse des Risques : Corrélation")
    st.markdown("""
    - **Rouge (1.0)** : Les actifs bougent ensemble (Risqué, pas de diversification).
    - **Bleu (-1.0)** : Les actifs bougent à l'inverse (Bonne protection).
    """)
    
    # Calcul de la corrélation
    corr_matrix = data.corr()

    # Belle heatmap interactive
    fig_corr = px.imshow(
        corr_matrix, 
        text_auto=True, 
        color_continuous_scale='RdBu_r', 
        zmin=-1, zmax=1,
        title="Matrice de Corrélation"
    )
    st.plotly_chart(fig_corr, use_container_width=True)