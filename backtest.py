import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --- Step 1: get the data ---
data = yf.download("SPY", start="2015-01-01", end="2025-01-01")

# Flatten nested columns from newer yfinance
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# --- Step 2: build the signal ---
N = 20
data["mean"] = data["Close"].rolling(N).mean()
data["std"] = data["Close"].rolling(N).std()
data["zscore"] = (data["Close"] - data["mean"]) / data["std"]

# --- Step 3: turn the signal into positions ---
data["position_raw"] = 0
data.loc[data["zscore"] < -1, "position_raw"] = 1
data.loc[data["zscore"] > 1, "position_raw"] = -1
data["position"] = data["position_raw"].shift(1)  # no look-ahead

# --- Step 4: turn positions into returns ---
data["asset_return"] = data["Close"].pct_change()
data["strategy_return_gross"] = data["position"] * data["asset_return"]

# --- Step 5: transaction costs ---
cost_per_trade = 0.0005
data["trade"] = data["position"].diff().abs()
data["cost"] = data["trade"] * cost_per_trade
data["strategy_return"] = data["strategy_return_gross"] - data["cost"]

# --- equity curves ---
data["strategy_equity"] = (1 + data["strategy_return"].fillna(0)).cumprod()
data["strategy_equity_gross"] = (1 + data["strategy_return_gross"].fillna(0)).cumprod()
data["buyhold_equity"] = (1 + data["asset_return"].fillna(0)).cumprod()

# --- Step 6: proper metrics ---
def metrics(returns, equity):
    returns = returns.fillna(0)
    # Annualized return: geometric, 252 trading days per year
    n_years = len(returns) / 252
    total_growth = equity.iloc[-1]
    annual_return = total_growth ** (1 / n_years) - 1
    # Annualized Sharpe ratio: mean daily return / daily volatility, scaled by sqrt(252)
    if returns.std() != 0:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
    else:
        sharpe = 0.0
    # Max drawdown: worst peak-to-trough drop in the equity curve
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown = drawdown.min()
    return annual_return, sharpe, max_drawdown

strat_ann, strat_sharpe, strat_dd = metrics(data["strategy_return"], data["strategy_equity"])
bh_ann, bh_sharpe, bh_dd = metrics(data["asset_return"], data["buyhold_equity"])

print("\n--- RESULTS ---")
print("Strategy AFTER costs, $1 became:", round(data["strategy_equity"].iloc[-1], 3))
print("Buy & hold,           $1 became:", round(data["buyhold_equity"].iloc[-1], 3))
print("Number of trades:", int(data["trade"].sum()))

print("\n--- METRICS (strategy vs buy & hold) ---")
print(f"Annualized return:  {strat_ann:+.2%}   vs   {bh_ann:+.2%}")
print(f"Sharpe ratio:       {strat_sharpe:+.2f}    vs   {bh_sharpe:+.2f}")
print(f"Max drawdown:       {strat_dd:.2%}   vs   {bh_dd:.2%}")

# --- charts ---
plt.figure(figsize=(10, 6))
plt.plot(data.index, data["strategy_equity"], label="Mean-reversion strategy (after costs)")
plt.plot(data.index, data["strategy_equity_gross"], label="Strategy (before costs)", linestyle="--", alpha=0.6)
plt.plot(data.index, data["buyhold_equity"], label="Buy & hold SPY")
plt.title("Growth of $1: strategy vs. buy-and-hold")
plt.ylabel("Value of $1 invested")
plt.legend()
plt.tight_layout()
plt.savefig("equity_curve.png", dpi=150, bbox_inches="tight")
plt.show()