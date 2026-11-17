# BTC Race 24h Bot — Dip Reversion with EMA Trend Filter
## Strategy
- Entry: Price >50bps below 60-bar high + rebounding (confirmed by recent low check)
- Partial TP: +80bps (sell half position)  
- Full TP: +160bps (exit all)
- Stop Loss: -100bps
- Position Size: 65% of equity per trade
- Max Trades: 40 | Recovery wait: 10 bars

## Files
- `main.ts` — Bot implementation
- `vendor/makefun-bars.ts` — Protocol SDK (from kit)
