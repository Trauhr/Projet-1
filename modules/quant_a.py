import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def run():
    st.markdown('<div class="main-title">MARKET ANALYST</div>', unsafe_allow_html=True)

    # 1. Récupération des données
    ticker = "BTC-USD"
    try:
        data = yf.download(ticker, period="2y", interval="1d", progress=False)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return

    if data.empty:
        st.error("Aucune donnée reçue. Vérifie ta connexion internet.")
        return

    # 2. Nettoyage des données (Le correctif anti-bug)
    # Si 'Close' est un DataFrame (plusieurs colonnes), on le force en Série unique
    if isinstance(data['Close'], pd.DataFrame):
        close_prices = data['Close'].iloc[:, 0]
    else:
        close_prices = data['Close']

    # Calcul des Moyennes Mobiles sur cette série propre
    sma_20 = close_prices.rolling(window=20).mean()
    sma_50 = close_prices.rolling(window=50).mean()

    # 3. Récupération des dernières valeurs (Conversion sécurisée)
    try:
        last_price = float(close_prices.iloc[-1])
        last_sma20 = float(sma_20.iloc[-1])
    except:
        # Fallback au cas où le format est vraiment bizarre
        last_price = float(close_prices.values[-1])
        last_sma20 = float(sma_20.values[-1])

    # 4. Logique de Trading
    if last_price > last_sma20:
        signal = "ACHETER 🟢"
        delta_color = "normal"
    else:
        signal = "VENDRE 🔴"
        delta_color = "off"

    # 5. Affichage Métriques
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Bitcoin", f"{last_price:,.0f} $")
    col2.metric("Signal Stratégie", signal)
    col3.metric("Moyenne 20j", f"{last_sma20:,.0f} $", delta_color=delta_color)

    # 6. Graphique
    st.subheader("Graphique de Stratégie (2 ans)")
    
    fig = go.Figure()

    # Prix
    fig.add_trace(go.Scatter(
        x=data.index, y=close_prices, 
        mode='lines', name='Prix BTC',
        line=dict(color='white', width=1)
    ))

    # Moyenne 20j
    fig.add_trace(go.Scatter(
        x=data.index, y=sma_20, 
        mode='lines', name='Moyenne 20j',
        line=dict(color='#FFD700', width=2)
    ))

    # Moyenne 50j
    fig.add_trace(go.Scatter(
        x=data.index, y=sma_50, 
        mode='lines', name='Moyenne 50j',
        line=dict(color='#00BFFF', width=2, dash='dot')
    ))

    fig.update_layout(
        title="Stratégie Moyennes Mobiles",
        xaxis_title="Date",
        yaxis_title="Prix ($)",
        height=500,
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)