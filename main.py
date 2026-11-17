import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars


# ─── 策略参数（从Top Entrants分析优化）─────────────────────────────────────────
DIP_BPS = 80          # Dip below EMA fast → entry signal
TP_PARTIAL_BPS = 150  # Partial take profit at +150bps (sell 50%)
TP_FULL_BPS = 300     # Full exit at +300bps  
SL_BPS = 60           # Stop loss at -60bps
EMA_FAST = 21
EMA_SLOW = 60
SIZE_BPS = 95         # Position size: 95% of equity
MAX_TRADES = 40       # Cap trades to avoid overtrading
RECOVERY_BARS = 10    # Bars to wait after exit before re-entry


def calc_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices) if prices else 0
    k = 2.0 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1.0 - k)
    return ema


def main():
    state = {
        "prices": [],
        "ema_fast": 0.0,
        "ema_slow": 0.0,
        "entry_price": 0,
        "position_qty": 0,
        "trade_count": 0,
        "last_exit_seq": -RECOVERY_BARS,
        "highest_equity": 0,
    }

    def on_batch(s):
        # Skip warmup batches
        if s.warming_up:
            return []

        seq = s.seq

        # Get current price
        price = s.close("CBBTC")
        if price is None or price == 0:
            return []

        price_int = int(price)

        # Update price history (keep last 200 bars for EMA calc)
        state["prices"].append(price_int)
        if len(state["prices"]) > 200:
            state["prices"] = state["prices"][-200:]

        # Calculate EMAs
        state["ema_fast"] = calc_ema(state["prices"], EMA_FAST)
        state["ema_slow"] = calc_ema(state["prices"], EMA_SLOW)

        # Track highest equity
        eq_int = int(s.equity)
        if state["highest_equity"] == 0:
            state["highest_equity"] = eq_int
        elif eq_int > state["highest_equity"]:
            state["highest_equity"] = eq_int

        orders = []

        # ── Position management ──────────────────────────────────────────────
        if state["position_qty"] > 0:
            # PnL calculation in bps relative to entry
            if state["entry_price"] > 0:
                pnl_bps = int((price_int - state["entry_price"]) / state["entry_price"] * makefun_bars.BPS)
            else:
                pnl_bps = 0

            # Partial take profit at +150bps (sell 50% of position)
            if pnl_bps >= TP_PARTIAL_BPS:
                sell_qty = state["position_qty"] // 2
                if sell_qty > 0:
                    orders.append({
                        "side": "sell",
                        "symbol": "CBBTC",
                        "qty": sell_qty,
                        "max_slippage_bps": 500
                    })
                    state["position_qty"] -= sell_qty

            # Full take profit at +300bps
            if pnl_bps >= TP_FULL_BPS and state["position_qty"] > 0:
                orders.append({
                    "side": "sell",
                    "symbol": "CBBTC",
                    "qty": state["position_qty"],
                    "max_slippage_bps": 500
                })
                state["position_qty"] = 0
                state["last_exit_seq"] = seq
                state["trade_count"] += 1

            # Stop loss at -60bps
            elif pnl_bps <= -SL_BPS and state["position_qty"] > 0:
                orders.append({
                    "side": "sell",
                    "symbol": "CBBTC",
                    "qty": state["position_qty"],
                    "max_slippage_bps": 500
                })
                state["position_qty"] = 0
                state["last_exit_seq"] = seq
                state["trade_count"] += 1

        # ── Entry logic ─────────────────────────────────────────────────────
        if state["position_qty"] == 0:
            bars_since_exit = seq - state["last_exit_seq"]
            can_reenter = bars_since_exit >= RECOVERY_BARS

            # Trend filter: price above slow EMA (allows slight deviation)
            above_slow = price_int > state["ema_slow"] * 0.999 if state["ema_slow"] > 0 else True

            # Primary signal: dip below fast EMA
            dip_below_fast = price_int < state["ema_fast"] * (1 - DIP_BPS / makefun_bars.BPS) \
                if state["ema_fast"] > 0 else False

            # Secondary signal: deep dip from recent high
            if len(state["prices"]) >= 10:
                recent_high = max(state["prices"][-min(60, len(state["prices"])):])
                drawdown_bps = int((price_int - recent_high) / recent_high * makefun_bars.BPS) \
                    if recent_high > 0 else 0
                deep_dip = drawdown_bps <= -120
            else:
                deep_dip = False

            should_buy = (can_reenter and above_slow and
                         (dip_below_fast or deep_dip) and
                         state["trade_count"] < MAX_TRADES)

            if should_buy:
                # Calculate position size
                notional = int(s.equity * SIZE_BPS / 10000)
                min_notional = s.hello["fees"]["min_notional_quote_units"]
                if notional >= min_notional:
                    orders.append({
                        "side": "buy",
                        "symbol": "CBBTC",
                        "notional_quote_units": notional,
                        "max_slippage_bps": 300
                    })
                    state["position_qty"] = notional * 1_000_000 // price_int if price_int > 0 else 0
                    state["entry_price"] = price_int
                    state["trade_count"] += 1

        return orders

    makefun_bars.run(on_batch)


if __name__ == "__main__":
    main()
