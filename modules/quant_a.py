import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import timedelta

# --- FONCTIONS UTILITAIRES (MATHS QUANT) ---
def calculate_metrics(daily_returns):
    """Calcule le Sharpe Ratio et le Max Drawdown"""
    # Sharpe (Hypothèse: 252 jours de trading, taux sans risque ~0 pour simplifier)
    if daily_returns.std() == 0:
        sharpe = 0
    else:
        sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
    
    # Max Drawdown
    cumulative = (1 + daily_returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min() * 100 # En pourcentage
    
    return sharpe, max_drawdown

def run():
    # 1. TITRE
    st.markdown('<div class="main-title">MARKET ANALYST</div>', unsafe_allow_html=True)

    # 2. INPUTS
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        ticker = st.text_input("Symbole", "BTC-USD")
    with col2:
        period = st.selectbox("Période", ["1y", "2y", "5y", "max"], index=1)
    with col3:
        strategy_type = st.selectbox(
            "💎 Choisir une Stratégie",
            ["Moyennes Mobiles (Golden Cross)", "RSI (Surachat/Survente)", "Bandes de Bollinger", "Buy & Hold"]
        )

    # 3. DONNÉES
    try:
        data = yf.download(ticker, period=period, progress=False)
    except:
        st.error("Erreur de connexion.")
        return

    if data.empty:
        st.error("Aucune donnée.")
        return

    # Nettoyage
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    df = data.copy()
    if isinstance(df['Close'], pd.DataFrame):
        df['Close'] = df['Close'].iloc[:, 0]
    
    # Initialisation Signal
    df['Signal'] = 0 

    # ---------------------------------------------------------
    # 4. STRATÉGIES & SIGNAUX
    # ---------------------------------------------------------
    st.markdown("---")
    
    # --- LOGIQUE ---
    if strategy_type == "Moyennes Mobiles (Golden Cross)":
        st.info("ℹ️ Tendance : ACHAT si Moyenne Courte > Moyenne Longue.")
        c1, c2 = st.columns(2)
        short_window = c1.slider("Moyenne Courte", 5, 50, 20)
        long_window = c2.slider("Moyenne Longue", 50, 200, 50)
        
        df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
        df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()
        df['Signal'] = np.where(df['SMA_Short'] > df['SMA_Long'], 1, 0)

        # Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color='white', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_Short'], name='MA Court', line=dict(color='#00d2ff', width=1)))
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_Long'], name='MA Long', line=dict(color='#e056fd', width=1)))

    elif strategy_type == "RSI (Surachat/Survente)":
        st.info("ℹ️ RSI : Achat si < Seuil Bas, Vente si > Seuil Haut.")
        c1, c2, c3 = st.columns(3)
        rsi_period = c1.slider("Période", 5, 30, 14)
        overbought = c2.slider("Vente (>)", 50, 90, 70)
        oversold = c3.slider("Achat (<)", 10, 50, 30)

        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        df['Signal'] = np.where(df['RSI'] < overbought, 1, 0) # Simplifié

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color='white')))

    elif strategy_type == "Bandes de Bollinger":
        st.info("ℹ️ Volatilité : Achat bas du range, Vente haut du range.")
        c1, c2 = st.columns(2)
        window = c1.slider("Période", 10, 50, 20)
        std_dev = c2.slider("Écart-Type", 1.0, 3.0, 2.0)

        rolling_mean = df['Close'].rolling(window=window).mean()
        rolling_std = df['Close'].rolling(window=window).std()
        df['Upper'] = rolling_mean + (rolling_std * std_dev)
        df['Lower'] = rolling_mean - (rolling_std * std_dev)
        df['Signal'] = np.where(df['Close'] > df['Lower'], 1, 0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color='white')))
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], name='Haut', line=dict(color='rgba(255,100,100,0.3)')))
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], name='Bas', line=dict(color='rgba(100,255,100,0.3)'), fill='tonexty'))

    else: # Buy & Hold
        df['Signal'] = 1
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Prix', line=dict(color='#00d2ff')))

    # Ajout des marqueurs Achat/Vente sur le graphe (Visualisation "Superposée")
    # On détecte les changements de signal (0 -> 1 ou 1 -> 0)
    df['Position_Change'] = df['Signal'].diff()
    buys = df[df['Position_Change'] == 1]
    sells = df[df['Position_Change'] == -1]

    fig.add_trace(go.Scatter(
        x=buys.index, y=buys['Close'], mode='markers', name='Achat 🟢',
        marker=dict(symbol='triangle-up', color='#00ff00', size=12)
    ))
    fig.add_trace(go.Scatter(
        x=sells.index, y=sells['Close'], mode='markers', name='Vente 🔴',
        marker=dict(symbol='triangle-down', color='#ff0000', size=12)
    ))

    fig.update_layout(title="Analyse & Signaux", template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------------------------------------
    # 5. BACKTEST COMPLET AVEC MÉTRIQUES AVANCÉES
    # ---------------------------------------------------------
    st.subheader(" Résultats Backtest & Métriques ")
    
    col_cap, col_btn = st.columns([1, 3])
    with col_cap:
        capital = st.number_input("Capital ($)", value=10000, step=1000)
    with col_btn:
        st.write("")
        st.write("")
        run_test = st.button("LANCER SIMULATION")

    if run_test:
        # Calculs Rendements
        df['Market_Return'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)
        
        df['Portfolio_Value'] = capital * (1 + df['Strategy_Return']).cumprod()
        df['Buy_Hold_Value'] = capital * (1 + df['Market_Return']).cumprod()
        
        # --- CALCUL DES MÉTRIQUES (Sharpe & Drawdown) ---
        sharpe_strat, dd_strat = calculate_metrics(df['Strategy_Return'])
        sharpe_bh, dd_bh = calculate_metrics(df['Market_Return'])
        
        # Performance Finale
        perf_strat = ((df['Portfolio_Value'].iloc[-1] - capital) / capital) * 100
        perf_bh = ((df['Buy_Hold_Value'].iloc[-1] - capital) / capital) * 100
        
        # AFFICHAGE DES RÉSULTATS
        # Ligne 1 : Performance Financière
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Ma Stratégie", f"{df['Portfolio_Value'].iloc[-1]:,.0f} $", f"{perf_strat:.2f} %")
        kpi2.metric("Buy & Hold", f"{df['Buy_Hold_Value'].iloc[-1]:,.0f} $", f"{perf_bh:.2f} %")
        kpi3.metric("Alpha (Diff)", f"{perf_strat - perf_bh:.2f} %", delta_color="normal")

        st.markdown("---")
        
        # Ligne 2 : Risque (Sharpe & Drawdown)
        st.caption("📊 Analyse du Risque (Plus le Sharpe est haut, mieux c'est. Plus le Drawdown est bas, mieux c'est)")
        risk1, risk2, risk3, risk4 = st.columns(4)
        risk1.metric("Sharpe Stratégie", f"{sharpe_strat:.2f}")
        risk2.metric("Max Drawdown Strat", f"{dd_strat:.2f} %", delta_color="inverse") # Inverse car rouge si grand
        risk3.metric("Sharpe Marché", f"{sharpe_bh:.2f}")
        risk4.metric("Max Drawdown Marché", f"{dd_bh:.2f} %", delta_color="inverse")

        # Graphique Comparatif
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Scatter(x=df.index, y=df['Portfolio_Value'], name='Stratégie', line=dict(color='#00d2ff', width=2)))
        fig_perf.add_trace(go.Scatter(x=df.index, y=df['Buy_Hold_Value'], name='Buy & Hold', line=dict(color='gray', dash='dot')))
        fig_perf.update_layout(title="Croissance du Capital", template="plotly_dark", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_perf, use_container_width=True)

    # ---------------------------------------------------------
    # 6. MACHINE LEARNING (PRÉDICTION)
    # ---------------------------------------------------------
    st.markdown("---")
    with st.expander(" Prédiction IA (Machine Learning)", expanded=True):
        st.write("Modèle : Régression Linéaire Simple sur les 30 prochains jours.")
        
        # Préparation des données pour scikit-learn
        df_ml = df.reset_index()
        df_ml['Date_Ordinal'] = df_ml['Date'].apply(lambda x: x.toordinal())
        
        X = df_ml[['Date_Ordinal']]
        y = df_ml['Close']
        
        # Entraînement
        model = LinearRegression()
        model.fit(X, y)
        
        # Prédiction Futur
        future_days = 30
        last_date = df_ml['Date'].iloc[-1]
        last_price = df_ml['Close'].iloc[-1] # On garde le dernier vrai prix
        
        future_dates = [last_date + timedelta(days=i) for i in range(1, future_days + 1)]
        future_ordinals = [[d.toordinal()] for d in future_dates]
        
        future_preds = model.predict(future_ordinals)
        
        plot_dates = [last_date] + future_dates
        plot_prices = [last_price] + list(future_preds)
        
        # Graphique de Prédiction
        fig_ai = go.Figure()
        fig_ai.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Historique', line=dict(color='gray')))
        fig_ai.add_trace(go.Scatter(
            x=plot_dates, y=plot_prices, # On utilise les listes fusionnées
            name='Prédiction IA', 
            line=dict(color='#F1C40F', width=3, dash='dash')
        ))
        
        fig_ai.update_layout(title=f"Prédiction du prix : {ticker}", template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ai, use_container_width=True)
        
        next_price = future_preds[-1]
        current_price = df['Close'].iloc[-1]
        trend = "Hausse 🚀" if next_price > current_price else "Baisse 📉"
        st.info(f"D'après l'IA, la tendance est à la {trend}. Prix estimé dans 30 jours : {next_price:,.2f} $")