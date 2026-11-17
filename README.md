# BTC Race 24h Bot — Dip Reversion with EMA Trend Filter

> make.fun btc-race-24h-20261117-0603 entry by breezesamuel
> Strategy: Buy dips below EMA(21), take profit at +150bps partial / +300bps full, stop loss at -60bps

## Strategy

- **Entry**: Price dips >80bps below EMA(21) AND price > EMA(60) * 0.999 (trend filter)
- **Partial TP**: Sell 50% position at +150bps PnL
- **Full TP**: Exit all at +300bps PnL
- **Stop Loss**: Exit all at -60bps PnL
- **Position Size**: 95% of equity per trade
- **Max Trades**: 40 per window
- **Recovery Wait**: 10 bars after exit before re-entry

## Files

- `main.py` — Bot implementation
- `vendor/makefun_bars.py` — Protocol SDK (from kit)
- `LICENSE` — MIT

## Run Locally

```bash
cd btc-race-24h-20261117-0603-kit
node cli/makefun.mjs grade-local --kit . --bot ../btc-race-bot --driver docker
```

## Submit

```bash
git add -A
git commit -m "v1: dip reversion bot"
git push origin main
node cli/makefun.mjs submit --competition btc-race-24h-20261117-0603 --repo-url https://github.com/breezesamuel/btc-race-bot.git --commit $(git rev-parse HEAD) --title "BTC Race Bot v1"
```
