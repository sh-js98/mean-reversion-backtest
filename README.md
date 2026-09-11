\# Mean-Reversion Backtest (SPY, 2015–2025)



A simple, honest backtest of a z-score mean-reversion strategy on SPY, built to

practise the full research loop end to end: data → signal → positions →

returns → costs → evaluation. \*\*The goal was never a profitable strategy — it

was a backtest I can defend, and an honest account of why I don't trust the

result.\*\*



Spoiler: the strategy loses. That's the interesting part.



\## Hypothesis



When a liquid asset moves unusually far from its own recent average, it tends to

revert back toward it. If true, buying when price is "unusually low" and

selling/shorting when "unusually high" should extract a return.



\## Method



\- \*\*Data:\*\* daily SPY closes, Jan 2015 – Jan 2025 (via `yfinance`).

\- \*\*Signal:\*\* 20-day rolling z-score,

&#x20; `z = (price − rolling\_mean) / rolling\_std`.

\- \*\*Rule:\*\* go long when `z < −1`, go short/flat when `z > +1`, else hold.

\- \*\*No look-ahead:\*\* positions are shifted forward one day

&#x20; (`position.shift(1)`), so each day trades only on information available at the

&#x20; prior close.

\- \*\*Costs:\*\* 5 bps charged on every position change.

\- \*\*Benchmark:\*\* buy-and-hold SPY over the same window.



\## Results



| Metric | Strategy (after costs) | Buy \& hold SPY |

|---|---|---|

| Growth of $1 | \*\*$0.64\*\* | $3.40 |

| Annualized return | \*\*−4.40%\*\* | +13.03% |

| Sharpe ratio | \*\*−0.26\*\* | +0.78 |

| Max drawdown | \*\*−53.0%\*\* | −33.7% |

| Number of trades | 619 | 1 |



The strategy underperformed on every axis: negative return, negative Sharpe,

and a \*\*deeper\*\* drawdown than the index itself. It took more risk than simply

holding the market and was paid less than nothing for it.



!\[Equity curve](equity\_curve.png)



\## Why it fails (and why that's the point)



Two clear, explainable reasons — both visible in the equity curve:



1\. \*\*It fights trends.\*\* From 2015–2018 (a choppy, sideways market) the strategy

&#x20;  actually beat buy-and-hold — mean reversion profits when price overshoots and

&#x20;  snaps back. But from 2020 onward, SPY entered a strong sustained uptrend. The

&#x20;  strategy repeatedly shorted the market for being "too high" and was run over

&#x20;  as it kept climbing. Mean reversion is a bet on range-bound markets, not

&#x20;  trending ones.



2\. \*\*It overtrades.\*\* 619 trades over ten years, each paying 5 bps. Before costs

&#x20;  the strategy ended at $0.87; after costs, $0.64. That \~23% gap is pure

&#x20;  trading friction, compounded. A strategy that trades this often has to clear

&#x20;  a high bar just to break even.



\## Why I don't fully trust even this result



Even though the verdict (the strategy is bad) is robust, I'd treat the specifics

with caution:



\- \*\*Single asset, single period.\*\* One instrument over one decade is one draw

&#x20; from history. The 2020–2025 bull run dominates the outcome; a different window

&#x20; could look meaningfully different.

\- \*\*Arbitrary parameters.\*\* The 20-day window and ±1 thresholds were chosen by

&#x20; convention, not optimized — and I deliberately did \*not\* optimize them, to

&#x20; avoid fooling myself with overfit results.

\- \*\*Cost model is a simplification.\*\* A flat 5 bps ignores slippage, the

&#x20; bid-ask spread, and market impact, all of which would likely make real results

&#x20; worse, not better.

\- \*\*Shorting assumed frictionless.\*\* Borrow costs and short constraints are

&#x20; ignored.



\## What I'd do next



\- Test across many assets and rolling sub-periods to see whether \*any\* regime

&#x20; favours the signal, instead of trusting one backtest.

\- Separate the long and short legs — the short leg is likely responsible for most

&#x20; of the trend-fighting losses.

\- Add a proper time-series cross-validation scheme (e.g. purged/embargoed splits,

&#x20; per López de Prado) rather than eyeballing one equity curve.

\- Reduce turnover (e.g. wider thresholds, a hold band) and measure the

&#x20; cost/return trade-off directly.



\## Repo contents



\- `backtest.py` — the full backtest: data, signal, positions, costs, metrics

\- `equity\_curve.png` — strategy vs. buy-and-hold equity curve

\- `README.md` — this file



\## Run it



Built and tested with \*\*Python 3.11\*\*.



```bash

pip install yfinance pandas numpy matplotlib

python backtest.py

```



Running the script prints the results and metrics and saves the equity-curve

plot as `equity\_curve.png`.



\## A note on reproducing the numbers



Results were generated in September 2026. `yfinance` price data can be revised

over time (dividend/split adjustments, vendor corrections), so someone running

this later may see figures that drift slightly from those reported above. The

verdict — the strategy loses to buy-and-hold — is robust to that drift; the

exact decimals are not.



\## What this project is really about



Not finding alpha. Building the discipline: avoiding look-ahead bias, charging

realistic costs, measuring risk-adjusted performance, and reporting an

unflattering result honestly instead of hunting for a version that "wins." A

strategy I can explain the failure of is worth more than one that succeeds for

reasons I can't.



