# BTC Race 24h Bot — Dip Reversion with EMA Trend Filter

> Built by an AI agent for [make.fun's "Race a BTC trading bot live for 24 hours" bounty](https://make.fun/bounty/btc-race-24h-20261117-0603), $250 in USDC.

## Strategy
- Entry: Price >50bps below 60-bar high + rebounding (confirmed by recent low check)
- Partial TP: +80bps (sell 50% position)
- Full TP: +160bps (exit all)
- Stop Loss: -100bps
- Position Size: 65% of equity per trade
- Max Trades: 40 | Recovery wait: 10 bars

## Files
- `main.ts` — Bot implementation
- `vendor/makefun-bars.ts` — Protocol SDK (from kit)

## Run Locally
```bash
cd btc-race-24h-20261117-0603-kit
node cli/makefun.mjs grade-local --kit . --bot ../btc-race-bot --driver process
```

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/breezesamuel/btc-race-bot/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/breezesamuel/btc-race-bot/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
