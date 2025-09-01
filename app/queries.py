BASE_SQL = """
WITH base AS (
  SELECT
    id, ticker, qty, cum_qty, buy_price, buy_datetime,
    sell_price, sell_datetime, stop_price, due_date, profit,
    side, status, positionside, leverage, algorithm, fee, tax,
    trade_mode, n_trade, is_real, created_time, updated_time,
    CASE WHEN buy_price > 0 AND sell_price IS NOT NULL
         THEN (sell_price / buy_price) - 1
         ELSE NULL END AS pct
  FROM trading_history.trade_history
  WHERE buy_datetime >= :start AND buy_datetime < :end
    AND (:all OR ticker = ANY(:tickers))
)
"""
