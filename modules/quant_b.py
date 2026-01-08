import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def run():
    # 1. TITRE
    st.markdown('<div class="main-title">PORTFOLIO MANAGER</div>', unsafe_allow_html=True)

    # 2. SÉLECTION
    st.sidebar.header("🛠 Configuration")
    tickers = st.multiselect(
        "1️⃣ Choisir les actifs (Min. 2)",
        ["BTC-USD", "ETH-USD", "SOL-USD", "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "GC=F", "EURUSD=X"], 
        default=["BTC-USD", "AAPL", "GC=F"] 
    )

    if len(tickers) < 2:
        st.warning("⚠️ Sélectionne au moins 2 actifs.")
        return

    # 3. DONNÉES
    try:
        data = yf.download(tickers, period="2y", interval="1d", progress=False)['Close']
    except Exception as e:
        st.error(f"Erreur téléchargement : {e}")
        return

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.ffill().dropna()

    if data.empty:
        st.error("Pas de données.")
        return

    # ---------------------------------------------------------
    # 4. ALLOCATION INTELLIGENTE 
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("⚖️ Allocation du Portefeuille")

    # Conteneur pour les sliders et le camembert
    col_sliders, col_pie = st.columns([2, 1])

    with col_sliders:
        st.write("Définis l'importance de chaque actif :")
        weights_input = {}
        
        # On crée les sliders
        for ticker in tickers:
            weights_input[ticker] = st.slider(f"Poids {ticker}", 0, 100, 100 // len(tickers), key=ticker)

        # Calcul du total saisi par l'utilisateur
        total_input = sum(weights_input.values())

        # Gestion du Total (Barre de progression & Alertes)
        if total_input == 0:
            st.error("Le total ne peut pas être 0%.")
            normalized_weights = {k: 1/len(tickers) for k in tickers} # Fallback équitable
        else:
            # Calcul des VRAIS pourcentages (Normalisation)
            normalized_weights = {k: v / total_input for k, v in weights_input.items()}
            
            # Barre de progression visuelle
            bar_val = min(total_input / 100, 1.0) # Bloque la barre à 100% visuellement
            bar_color = "red" if total_input != 100 else "green"
            
            st.markdown(f"""
                <style>
                    .stProgress > div > div > div > div {{ background-color: {bar_color}; }}
                </style>""", unsafe_allow_html=True)
            
            st.progress(bar_val)
            
            # Message d'état
            if total_input == 100:
                st.success(f"✅ Total parfait : {total_input}%")
            elif total_input < 100:
                st.warning(f"⚠️ Total : {total_input}% (Il reste {100-total_input}% non alloués)")
            else:
                st.error(f"⚠️ Total : {total_input}% (Dépassement de {total_input-100}%)")
                st.caption(f"👉 Pas de panique : Le système a automatiquement rééquilibré vos choix à 100% (voir camembert).")

    # Affichage du Camembert (Répartition RÉELLE)
    with col_pie:
        st.markdown("**Répartition Réelle**")
        df_pie = pd.DataFrame({
            'Actif': list(normalized_weights.keys()),
            'Poids Réel': list(normalized_weights.values())
        })
        # On formate pour l'affichage (ex: 0.33 -> 33%)
        fig_pie = px.pie(df_pie, values='Poids Réel', names='Actif', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=200, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------------------------------------------------
    # 5. CALCULS & GRAPHIQUES
    # ---------------------------------------------------------
    
    # Rendements
    returns = data.pct_change().dropna()
    portfolio_returns = returns.dot(pd.Series(normalized_weights))
    
    initial_capital = 10000
    portfolio_cumulative = (1 + portfolio_returns).cumprod() * initial_capital
    assets_cumulative = (1 + returns).cumprod() * initial_capital

    # Graphique Performance
    st.markdown("---")
    st.subheader("📈 Simulation de Performance")
    
    fig_perf = go.Figure()
    # Actifs individuels
    for ticker in tickers:
        fig_perf.add_trace(go.Scatter(
            x=assets_cumulative.index, y=assets_cumulative[ticker], 
            name=ticker, line=dict(width=1, dash='dot'), opacity=0.5
        ))
    # Portefeuille Global
    fig_perf.add_trace(go.Scatter(
        x=portfolio_cumulative.index, y=portfolio_cumulative, 
        name='MON PORTEFEUILLE', line=dict(color='#00d2ff', width=4)
    ))

    fig_perf.update_layout(title=f"Capital (Base {initial_capital}$)", template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_perf, use_container_width=True)

    # ---------------------------------------------------------
    # 6. ANALYSE RISQUE
    # ---------------------------------------------------------
    st.subheader("📊 Métriques de Risque")
    
    total_return = (portfolio_cumulative.iloc[-1] / initial_capital) - 1
    annual_vol = portfolio_returns.std() * np.sqrt(252)
    sharpe = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() != 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Rendement Global", f"{total_return*100:.2f} %")
    c2.metric("Volatilité", f"{annual_vol*100:.2f} %", delta_color="inverse")
    c3.metric("Sharpe Ratio", f"{sharpe:.2f}")

    # Matrice Corrélation
    st.write("Matrice de Corrélation des actifs :")
    corr_matrix = returns.corr()
    fig_corr = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', zmin=-1, zmax=1, aspect="auto")
    fig_corr.update_layout(template="plotly_dark", height=350, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_corr, use_container_width=True)