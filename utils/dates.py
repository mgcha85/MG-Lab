from datetime import datetime, timedelta, timezone

def default_dates():
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=365)
    return start, end

def parse_tickers(tickers: str | None):
    if not tickers:
        return True, []
    return False, [t.strip() for t in tickers.split(",") if t.strip()]
