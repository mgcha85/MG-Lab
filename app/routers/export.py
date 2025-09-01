from fastapi import APIRouter, Response
from sqlalchemy import text
import pandas as pd, io
from ..db import engine
from ..utils.dates import default_dates, parse_tickers
from ..config import TIMEZONE
from ..queries import BASE_SQL
from datetime import datetime

router = APIRouter(prefix="/api/export", tags=["export"])

@router.get("/excel")
def export_excel(interval: str = "monthly",
                 start: str | None = None, end: str | None = None,
                 tickers: str | None = None, tz: str = TIMEZONE):
    s_def, e_def = default_dates()
    start_dt = datetime.fromisoformat(start) if start else s_def
    end_dt = datetime.fromisoformat(end) if end else e_def
    all_flag, arr = parse_tickers(tickers)
    iv = {"daily":"day","weekly":"week","monthly":"month"}.get(interval, "month")

    with engine.begin() as conn:
        raw = pd.read_sql(text(BASE_SQL + "SELECT * FROM base ORDER BY buy_datetime ASC"),
                          conn, params={"start": start_dt, "end": end_dt, "all": all_flag, "tickers": arr})
        agg = pd.read_sql(text(BASE_SQL + """
              SELECT date_trunc(:iv, (buy_datetime AT TIME ZONE :tz)) AS bucket,
                     AVG(pct) AS pct_avg, COUNT(*) AS trade_count
              FROM base GROUP BY 1 ORDER BY 1
            """), conn, params={"iv": iv, "tz": tz, "start": start_dt, "end": end_dt, "all": all_flag, "tickers": arr})

    agg["bucket"] = pd.to_datetime(agg["bucket"]).dt.strftime("%Y-%m-%d")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        raw.to_excel(w, index=False, sheet_name="trades")
        agg.to_excel(w, index=False, sheet_name=f"agg_{interval}")
    buf.seek(0)
    return Response(buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="trade_report.xlsx"'})
