from fastapi import APIRouter, Query
from sqlalchemy import text
import pandas as pd
from ..db import engine
from ..utils.dates import default_dates, parse_tickers
from ..config import TIMEZONE
from ..queries import BASE_SQL
from datetime import datetime

router = APIRouter(prefix="/api/agg", tags=["agg"])

@router.get("/pct")
def agg_pct(
    interval: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    start: str | None = None,
    end: str | None = None,
    tickers: str | None = None,
    group_by_ticker: bool = False,
    tz: str = TIMEZONE,
):
    s_def, e_def = default_dates()
    start_dt = datetime.fromisoformat(start) if start else s_def
    end_dt = datetime.fromisoformat(end) if end else e_def
    all_flag, arr = parse_tickers(tickers)
    iv = {"daily":"day","weekly":"week","monthly":"month"}[interval]

    sql = BASE_SQL + f"""
    SELECT
      date_trunc(:iv, (buy_datetime AT TIME ZONE :tz)) AS bucket
      {', ticker' if group_by_ticker else ''},
      AVG(pct) AS pct_avg,
      COUNT(*) AS trade_count
    FROM base
    GROUP BY 1{', 2' if group_by_ticker else ''}
    ORDER BY 1{', 2' if group_by_ticker else ''}
    """
    with engine.begin() as conn:
        df = pd.read_sql(text(sql), conn,
                         params={"iv": iv, "tz": tz, "start": start_dt, "end": end_dt, "all": all_flag, "tickers": arr})
    df["bucket"] = pd.to_datetime(df["bucket"]).dt.strftime("%Y-%m-%d")
    return df.to_dict(orient="records")

@router.get("/by-ticker-month")
def agg_by_ticker_month(start: str | None = None, end: str | None = None,
                        tickers: str | None = None, tz: str = TIMEZONE):
    s_def, e_def = default_dates()
    start_dt = datetime.fromisoformat(start) if start else s_def
    end_dt = datetime.fromisoformat(end) if end else e_def
    all_flag, arr = parse_tickers(tickers)

    sql = BASE_SQL + """
    SELECT
      to_char(date_trunc('month', buy_datetime AT TIME ZONE :tz), 'YYYY-MM') AS ym,
      ticker,
      AVG(pct) AS pct_avg
    FROM base
    GROUP BY 1, 2
    ORDER BY 1, 2
    """
    with engine.begin() as conn:
        df = pd.read_sql(text(sql), conn,
                         params={"tz": tz, "start": start_dt, "end": end_dt, "all": all_flag, "tickers": arr})
    return df.to_dict(orient="records")
