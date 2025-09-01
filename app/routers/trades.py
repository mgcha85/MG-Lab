from fastapi import APIRouter, Query
from sqlalchemy import text
import pandas as pd
from ..db import engine
from ..utils.dates import default_dates, parse_tickers
from datetime import datetime
from ..queries import BASE_SQL

router = APIRouter(prefix="/api/trades", tags=["trades"])

@router.get("")
def get_trades(
    start: str | None = None,
    end: str | None = None,
    tickers: str | None = None,
    page: int = 1,
    page_size: int = 50,
    sort: str = "buy_datetime.desc",
):
    s_def, e_def = default_dates()
    start_dt = datetime.fromisoformat(start) if start else s_def
    end_dt = datetime.fromisoformat(end) if end else e_def
    all_flag, arr = parse_tickers(tickers)
    order_by = "buy_datetime DESC" if sort.endswith("desc") else "buy_datetime ASC"

    sql = f"""
    {BASE_SQL}
    SELECT * FROM base
    ORDER BY {order_by}
    OFFSET :offset LIMIT :limit
    """
    with engine.begin() as conn:
        df = pd.read_sql(
            text(sql), conn,
            params={"start": start_dt, "end": end_dt, "all": all_flag, "tickers": arr,
                    "offset": (page-1)*page_size, "limit": page_size}
        )
    return {"items": df.to_dict(orient="records"), "page": page, "page_size": page_size}
