import yfinance as yf
from datetime import datetime

def generate_report():
    ticker = "BTC-USD"
    data = yf.Ticker(ticker)
    hist = data.history(period="1d")
    
    if not hist.empty:
        open_price = hist['Open'].iloc[0]
        close_price = hist['Close'].iloc[0]
        # Calcul de la volatilité simple (High - Low)
        volatility = hist['High'].iloc[0] - hist['Low'].iloc[0]
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"rapport_{date_str}.txt"
        
        content = f"""RAPPORT QUOTIDIEN - {date_str}
-------------------------------
Actif         : {ticker}
Ouverture     : {open_price:.2f} $
Clôture       : {close_price:.2f} $
Volatilité    : {volatility:.2f} $
-------------------------------
Généré automatiquement par Cron.
"""
        with open(filename, "w") as f:
            f.write(content)
        print(f"✅ Rapport généré : {filename}")
    else:
        print("❌ Erreur : Impossible de récupérer les données.")

if __name__ == "__main__":
    generate_report()