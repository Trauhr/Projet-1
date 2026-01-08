import streamlit as st
# On importe nos modules
import modules.quant_a as quant_a
import modules.quant_b as quant_b

# Configuration de la page
st.set_page_config(page_title="Finance Dashboard", layout="wide")

# Sidebar (Menu)
st.sidebar.title("Navigation")
option = st.sidebar.radio("Aller vers :", ["Accueil", "Quant A (Crypto)", "Quant B (Portfolio)"])

# Logique de navigation
if option == "Accueil":
    st.title("🚀 Dashboard Finance & Linux")
    st.markdown("""
    Bienvenue sur le projet de **Finance de Marché**.
    
    Ce dashboard permet de :
    - Suivre des actifs en temps réel.
    - Tester des stratégies de trading.
    - Simuler un portefeuille.
    
    *Sélectionne un module dans le menu à gauche.*
    """)

elif option == "Quant A (Crypto)":
    # On lance la fonction run() du fichier quant_a.py
    quant_a.run()

elif option == "Quant B (Portfolio)":
    # On lance la fonction run() du fichier quant_b.py
    # (Pour l'instant c'est vide, on le fera après)
    st.warning("🚧 Module Portefeuille en construction...")