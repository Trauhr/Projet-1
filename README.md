#  Quant Terminal - Financial Dashboard

A quantitative trading and portfolio management application developed in Python using Streamlit.
This dashboard allows for the analysis of financial assets, strategy backtesting, and portfolio allocation optimization.

## 🚀 Features

### 1. 📈 Market Analyst (Module A)
Technical analysis and backtesting tool for a single asset (e.g., Bitcoin, Apple).
* **Multiple Strategies:**
    * Golden Cross (Moving Averages).
    * RSI (Overbought/Oversold Detection).
    * Bollinger Bands (Volatility).
    * Buy & Hold (Benchmark).
* **Advanced Backtest:** Simulation with adjustable capital.
* **Risk Management:** Automatic calculation of **Sharpe Ratio** and **Max Drawdown**.
* **🤖 AI Bonus:** Future price prediction via Machine Learning (Linear Regression).

### 2. 🏦 Portfolio Manager (Module B)
Simulation and asset allocation tool.
* **Multi-Asset Comparison:** Crypto, Stocks, Forex, Commodities.
* **Dynamic Allocation:** Smart sliders to weight the portfolio.
* **Correlation Matrix:** Diversification analysis.
* **Global Performance:** Calculation of combined portfolio volatility and return.

## 🛠 Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Trauhr/Projet_Python_Git_Linux_Arthur_JUNG.git
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    streamlit run app.py
    ```

## 📦 Technologies
* **Python**
* **Streamlit** (Web Interface)
* **YFinance** (Real-time market data)
* **Plotly** (Interactive charts)
* **Pandas & NumPy** (Financial calculations)
* **Scikit-Learn** (Machine Learning)

---
*Project created as part of a Quantitative Finance exercise.*
