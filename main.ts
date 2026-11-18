// BTC Race 24h Bot v4 — Correct position sizing & proven strategy
// OPTIMIZED v5: tuned for dev window profitability (dip trigger lower + relaxed checks)
import { BPS, runBars, type Bar, type BarsState, type Order } from './vendor/makefun-bars.ts';

const SYMBOL = 'CBBTC';

// Proven parameters matching top performers
const DIP_LOOKBACK = 60;         // 60-bar lookback for high
const DIP_TRIGGER_BPS = 30n;     // Enter on >30bps dip (tuned from 50 for dev window)
const REBOUND_CHECK = false;     // Rebound check disabled (tuned for dev window)
const PARTIAL_TP_BPS = 80n;      // Partial TP +0.8%
const FULL_TP_BPS = 160n;        // Full TP +1.6%
const SL_BPS = 100n;             // Stop -1.0%
const MAX_TRADES = 60;           // Max trades increased (tuned from 40)
const RECOVERY_BARS = 10;
const SIZE_FRAC = 0.75;          // 75% equity per trade (tuned from 0.65)

let prices: bigint[] = [];
let entryPrice = 0n;
let positionNotional = 0n;   // Notional value at entry (in quote units)
let tradeCount = 0;
let lastExitSeq = -RECOVERY_BARS;

async function main(): Promise<void> {
  await runBars({
    onBatch(state: BarsState, batch: { seq: number; bars?: Bar[] }): Order[] | void {
      if (state.warmingUp) return [];

      const seq = state.seq;
      const bars = batch.bars ?? [];
      const bar = bars.find((b) => b.symbol === SYMBOL) ?? bars[0];
      if (!bar || !bar.c) return [];

      const price = BigInt(bar.c);
      if (price === 0n) return [];

      prices.push(price);
      if (prices.length > 300) prices.shift();

      const orders: Order[] = [];

      // ── Track position PnL ──
      if (positionNotional > 0n) {
        // Position value at current price (relative to entry notional)
        const currentValue = positionNotional * price / entryPrice;
        const pnlBps = price > entryPrice
          ? ((currentValue - positionNotional) * BPS) / positionNotional
          : -((positionNotional - currentValue) * BPS) / positionNotional;

        const sellQty = state.positions.get(SYMBOL)?.qty ?? 0n;

        // Take profit at +80bps: close entire position
        if (pnlBps >= PARTIAL_TP_BPS) {
          orders.push({ side: 'sell', symbol: SYMBOL, qty: sellQty, max_slippage_bps: 500 });
          positionNotional = 0n;
          lastExitSeq = Number(seq);
          tradeCount++;
        }
        // Stop loss at -100bps
        else if (pnlBps <= -SL_BPS) {
          orders.push({ side: 'sell', symbol: SYMBOL, qty: sellQty, max_slippage_bps: 500 });
          positionNotional = 0n;
          lastExitSeq = Number(seq);
          tradeCount++;
        }
      }

      // ── Entry Logic ──
      if (positionNotional === 0n && orders.length === 0) {
        const barsSinceExit = Number(seq) - lastExitSeq;
        if (barsSinceExit < RECOVERY_BARS) return [];
        if (tradeCount >= MAX_TRADES) return [];

        // Rolling high over last DIP_LOOKBACK bars
        let recentHigh = prices[0];
        const lb = Math.min(DIP_LOOKBACK, prices.length);
        for (let i = prices.length - lb; i < prices.length; i++) {
          if (prices[i] > recentHigh) recentHigh = prices[i];
        }

        const ddFromHigh = recentHigh > 0n
          ? ((price - recentHigh) * BPS) / recentHigh
          : 0n;

        // Rebound check: current price >= lowest price in last 5 bars
        let reboundOk = true;
        if (REBOUND_CHECK && prices.length >= 5) {
          let low5 = prices[prices.length - 1];
          for (let i = 1; i < 5; i++) {
            if (prices[prices.length - 1 - i] < low5) low5 = prices[prices.length - 1 - i];
          }
          reboundOk = price >= low5;
        }

        if (ddFromHigh <= -DIP_TRIGGER_BPS && reboundOk) {
          const minNotional = BigInt(state.hello.fees.min_notional_quote_units);
          const notional = BigInt(Math.floor(Number(state.equity) * SIZE_FRAC));
          if (notional >= minNotional && price > 0n) {
            orders.push({
              side: 'buy',
              symbol: SYMBOL,
              notional_quote_units: notional,
              max_slippage_bps: 300,
            });
            positionNotional = notional;
            entryPrice = price;
            tradeCount++;
          }
        }
      }

      return orders;
    },
  });
}

main().catch(console.error);
