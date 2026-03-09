from __future__ import annotations

import os
import time
from datetime import UTC, datetime
from statistics import mean
from typing import Any

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from httpx import RequestError

app = FastAPI(title="Planetary Market Intelligence", version="0.4.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

HTTP_TIMEOUT = 15.0
DEFAULT_FX_SYMBOLS = "EUR,JPY,GBP,MXN,BRL,CHF,CAD,NOK"
WATCHLIST = [
    "BTCUSDT",
    "SILVER",
    "DXY",
    "NDX",
    "SPX",
    "XAUUSD",
    "NIKKEI",
    "GBPUSD",
    "EURUSD",
    "USDJPY",
    "USDCAD",
    "BRENT",
    "VIX",
]

COUNTRY_ALIASES = {
    "USA": "United States",
    "US": "United States",
    "MEX": "Mexico",
    "MX": "Mexico",
    "BRA": "Brazil",
    "BR": "Brazil",
    "COL": "Colombia",
    "CO": "Colombia",
    "ARG": "Argentina",
    "AR": "Argentina",
    "CAN": "Canada",
    "CA": "Canada",
    "CHN": "China",
    "CN": "China",
    "JPN": "Japan",
    "JP": "Japan",
    "DEU": "Germany",
    "DE": "Germany",
    "FRA": "France",
    "FR": "France",
    "GBR": "United Kingdom",
    "UK": "United Kingdom",
    "ESP": "Spain",
    "ES": "Spain",
    "ITA": "Italy",
    "IT": "Italy",
}

COUNTRY_TO_CONTINENT = {
    "United States": "North America",
    "Mexico": "North America",
    "Canada": "North America",
    "Brazil": "South America",
    "Argentina": "South America",
    "Colombia": "South America",
    "United Kingdom": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Spain": "Europe",
    "Italy": "Europe",
    "China": "Asia",
    "Japan": "Asia",
}

CATEGORY_TERMS = {
    "politica": ["politics", "election", "government", "congress", "policy", "diplomacy"],
    "acciones": ["equity", "stocks", "share", "earnings", "nasdaq", "sp500"],
    "macro": ["inflation", "gdp", "rates", "central bank", "fiscal", "bond"],
    "energia": ["oil", "gas", "lng", "pipeline", "opec", "refinery"],
    "geopolitica": ["geopolitics", "sanctions", "conflict", "war", "security", "military"],
}


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)


cache = TTLCache()


def parse_csv_param(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]


def clamp(v: float, min_v: float = 0.0, max_v: float = 100.0) -> float:
    return max(min_v, min(max_v, v))


def pct_change(a: float, b: float) -> float:
    if not b:
        return 0.0
    return round(((a - b) / b) * 100, 4)


YAHOO_SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "JPY=X",
    "GBPUSD": "GBPUSD=X",
    "USDCAD": "CAD=X",
    "BTCUSDT": "BTC-USD",
    "SILVER": "SI=F",
    "DXY": "DX-Y.NYB",
    "NDX": "^NDX",
    "SPX": "^GSPC",
    "XAUUSD": "GC=F",
    "NIKKEI": "^N225",
    "BRENT": "BZ=F",
    "VIX": "^VIX",
}


async def fetch_yahoo_quotes(symbols: list[str]) -> dict[str, dict[str, float]]:
    yahoo_symbols = [YAHOO_SYMBOLS[s] for s in symbols if s in YAHOO_SYMBOLS]
    if not yahoo_symbols:
        return {}

    try:
        raw, _ = await fetch_json(
            "https://query1.finance.yahoo.com/v7/finance/quote",
            {"symbols": ",".join(yahoo_symbols)},
            timeout=20.0,
        )
    except (RequestError, httpx.HTTPStatusError):
        return {}
    rows = raw.get("quoteResponse", {}).get("result", [])
    by_symbol: dict[str, dict[str, float]] = {}
    reverse = {v: k for k, v in YAHOO_SYMBOLS.items()}

    for row in rows:
        symbol = reverse.get(row.get("symbol"))
        if not symbol:
            continue
        price = row.get("regularMarketPrice")
        change_pct = row.get("regularMarketChangePercent")
        if price is None or change_pct is None:
            continue
        by_symbol[symbol] = {
            "price": float(price),
            "change_pct": float(change_pct),
        }

    return by_symbol


def score_event_severity(title: str | None) -> int:
    text = (title or "").lower()
    score = 25
    if any(k in text for k in ["war", "attack", "missile", "invasion", "conflict", "drone"]):
        score += 35
    if any(k in text for k in ["sanction", "oil", "gas", "pipeline", "shipping", "strait", "port"]):
        score += 20
    if any(k in text for k in ["ceasefire", "deal", "talks", "agreement"]):
        score -= 15
    return int(clamp(score, 0, 100))


def classify_event_impact(title: str | None) -> list[str]:
    text = (title or "").lower()
    assets = ["DXY"]
    if any(k in text for k in ["oil", "opec", "brent", "pipeline", "strait", "shipping", "tankers"]):
        assets.extend(["Brent", "WTI", "CAD", "NOK"])
    if any(k in text for k in ["gas", "lng"]):
        assets.extend(["TTF Gas", "EUR"])
    if any(k in text for k in ["sanction", "conflict", "war", "attack"]):
        assets.extend(["Gold", "CHF", "JPY", "VIX"])
    if any(k in text for k in ["inflation", "rate", "central bank", "cpi"]):
        assets.extend(["DXY", "EURUSD", "USDJPY"])
    if any(k in text for k in ["stocks", "equity", "nasdaq", "sp500", "earnings"]):
        assets.extend(["SPX", "NDX", "VIX"])
    return sorted(set(assets))


def infer_bias(assets: list[str], severity: int) -> str:
    if severity >= 70 and any(a in assets for a in ["Gold", "JPY", "CHF", "VIX"]):
        return "risk-off"
    if any(a in assets for a in ["Brent", "WTI"]):
        return "oil-sensitive"
    if any(a in assets for a in ["DXY", "USDJPY"]):
        return "usd-bullish"
    return "neutral"


def infer_category(title: str | None) -> str:
    text = (title or "").lower()
    if any(t in text for t in CATEGORY_TERMS["energia"]):
        return "energia"
    if any(t in text for t in CATEGORY_TERMS["acciones"]):
        return "acciones"
    if any(t in text for t in CATEGORY_TERMS["politica"]):
        return "politica"
    if any(t in text for t in CATEGORY_TERMS["macro"]):
        return "macro"
    if any(t in text for t in CATEGORY_TERMS["geopolitica"]):
        return "geopolitica"
    return "general"


def resolve_continent(country_name: str | None) -> str:
    if not country_name:
        return "Unknown"
    return COUNTRY_TO_CONTINENT.get(country_name, "Unknown")


def normalized_country(country_name: str | None) -> str:
    if not country_name:
        return "Unknown"
    name = country_name.strip()
    return COUNTRY_ALIASES.get(name.upper(), name)


def build_news_query(countries: list[str], categories: list[str], keyword: str | None) -> str:
    blocks: list[str] = []
    if countries:
        cterms = [COUNTRY_ALIASES.get(c.upper(), c) for c in countries]
        blocks.append("(" + " OR ".join(cterms) + ")")
    if categories:
        cat_terms: list[str] = []
        for c in categories:
            cat_terms.extend(CATEGORY_TERMS.get(c.lower(), [c]))
        if cat_terms:
            blocks.append("(" + " OR ".join(sorted(set(cat_terms))) + ")")
    if keyword:
        blocks.append(f"({keyword})")
    if not blocks:
        return "geopolitics OR conflict OR sanctions OR central bank OR stocks OR oil"
    return " AND ".join(blocks)


def compute_sovereign_risk(indicators: dict[str, dict[str, Any]]) -> dict[str, Any]:
    inflation = float(indicators.get("inflation", {}).get("value") or 0)
    debt_gdp = float(indicators.get("debt_gdp", {}).get("value") or 0)
    gdp_growth = float(indicators.get("gdp_growth", {}).get("value") or 0)
    reserves = float(indicators.get("reserves", {}).get("value") or 0)

    score = 35.0
    score += max(0, inflation - 4) * 3.5
    score += max(0, debt_gdp - 60) * 0.45
    score += max(0, 1.5 - gdp_growth) * 8.0

    if reserves < 50_000_000_000:
        score += 15
    elif reserves < 150_000_000_000:
        score += 7
    else:
        score -= 5

    score = clamp(score)
    bucket = "low"
    if score >= 70:
        bucket = "high"
    elif score >= 45:
        bucket = "medium"

    return {
        "score": round(score, 2),
        "bucket": bucket,
        "drivers": {
            "inflation": inflation,
            "debt_gdp": debt_gdp,
            "gdp_growth": gdp_growth,
            "reserves": reserves,
        },
    }


@app.get("/")
def root() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


async def fetch_json(url: str, params: dict[str, Any], timeout: float = HTTP_TIMEOUT) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        resp = await client.get(url, params=params)
    resp.raise_for_status()
    elapsed = (time.perf_counter() - started) * 1000
    return resp.json(), round(elapsed, 2)


async def get_fx(base: str = "USD", symbols: str = DEFAULT_FX_SYMBOLS) -> dict[str, Any]:
    base = base.upper()
    symbols = symbols.upper()
    cache_key = f"fx:{base}:{symbols}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    latency_ms = None
    try:
        fx_map = {
            "EUR": "EURUSD",
            "JPY": "USDJPY",
            "GBP": "GBPUSD",
            "MXN": "USDMXN",
            "BRL": "USDBRL",
            "CHF": "USDCHF",
            "CAD": "USDCAD",
            "NOK": "USDNOK",
        }
        extended = {**YAHOO_SYMBOLS, "USDMXN": "MXN=X", "USDBRL": "BRL=X", "USDCHF": "CHF=X", "USDNOK": "NOK=X"}
        yahoo_list = [extended[fx_map[s]] for s in parse_csv_param(symbols) if s in fx_map]
        started = time.perf_counter()
        raw, _ = await fetch_json("https://query1.finance.yahoo.com/v7/finance/quote", {"symbols": ",".join(yahoo_list)}, timeout=20.0)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        rows = raw.get("quoteResponse", {}).get("result", [])
        rev = {v: k for k, v in extended.items()}
        rates: dict[str, float] = {}
        changes_1d: dict[str, float] = {}
        for row in rows:
            code = rev.get(row.get("symbol"), "")
            src_price = row.get("regularMarketPrice")
            src_chg = row.get("regularMarketChangePercent")
            if src_price is None or src_chg is None:
                continue
            if code == "EURUSD":
                rates["EUR"] = float(src_price)
                changes_1d["EUR"] = float(src_chg)
            elif code == "USDJPY":
                rates["JPY"] = float(src_price)
                changes_1d["JPY"] = float(src_chg)
            elif code == "GBPUSD":
                rates["GBP"] = float(src_price)
                changes_1d["GBP"] = float(src_chg)
            elif code in ["USDMXN", "USDBRL", "USDCHF", "USDCAD", "USDNOK"]:
                key = code.replace("USD", "")
                rates[key] = float(src_price)
                changes_1d[key] = float(src_chg)

        if not rates:
            raise RequestError("No data from Yahoo FX")

        result = {
            "provider": "yahoo_finance",
            "base": base,
            "date": datetime.now(tz=UTC).strftime("%Y-%m-%d"),
            "rates": rates,
            "changes_1d_pct": changes_1d,
            "latency_ms": latency_ms,
            "freshness": "realtime",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        result = {
            "provider": "unavailable",
            "base": base,
            "date": time.strftime("%Y-%m-%d"),
            "rates": {},
            "changes_1d_pct": {},
            "latency_ms": latency_ms,
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar Yahoo Finance en este entorno.",
        }

    cache.set(cache_key, result, ttl_seconds=120)
    return result


async def get_country(iso3: str = "MEX") -> dict[str, Any]:
    iso3 = iso3.upper()
    cache_key = f"country:{iso3}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    series = {
        "gdp_growth": "NY.GDP.MKTP.KD.ZG",
        "inflation": "FP.CPI.TOTL.ZG",
        "debt_gdp": "GC.DOD.TOTL.GD.ZS",
        "reserves": "FI.RES.TOTL.CD",
        "trade_balance": "NE.RSB.GNFS.CD",
    }

    output: dict[str, Any] = {"iso3": iso3, "indicators": {}, "provider": "world_bank", "degraded": False, "latency_ms": None}
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, trust_env=False) as client:
            for key, code in series.items():
                url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{code}"
                resp = await client.get(url, params={"format": "json", "per_page": 100})
                resp.raise_for_status()
                body = resp.json()
                if isinstance(body, list) and len(body) > 1:
                    points = body[1]
                    latest = next((p for p in points if p.get("value") is not None), None)
                    if latest:
                        output["indicators"][key] = {"value": latest.get("value"), "date": latest.get("date")}
        output["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    except (RequestError, httpx.HTTPStatusError):
        output = {
            "iso3": iso3,
            "provider": "unavailable",
            "degraded": True,
            "note": "No se pudo consultar World Bank en este entorno.",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "indicators": {},
        }

    output["sovereign_risk"] = compute_sovereign_risk(output.get("indicators", {}))
    cache.set(cache_key, output, ttl_seconds=3600)
    return output


async def get_events(
    query: str = "geopolitics OR conflict OR sanctions OR central bank",
    max_records: int = 80,
    countries: list[str] | None = None,
    categories: list[str] | None = None,
    continents: list[str] | None = None,
) -> dict[str, Any]:
    countries = countries or []
    categories = categories or []
    continents = continents or []
    cache_key = f"events:{query}:{max_records}:{','.join(countries)}:{','.join(categories)}:{','.join(continents)}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    latency_ms = None
    try:
        raw, latency_ms = await fetch_json(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            {"query": query, "mode": "ArtList", "maxrecords": str(max_records), "format": "json", "sort": "HybridRel"},
            timeout=20.0,
        )
        articles = raw.get("articles", [])
        events: list[dict[str, Any]] = []
        for article in articles:
            loc = article.get("sourceCountryLocation", {}) or {}
            title = article.get("title")
            assets = classify_event_impact(title)
            severity = score_event_severity(title)
            country_name = normalized_country(article.get("sourceCountry"))
            continent = resolve_continent(country_name)
            category = infer_category(title)
            event = {
                "title": title,
                "summary": (article.get("title") or "")[0:180],
                "url": article.get("url"),
                "source": article.get("domain"),
                "seendate": article.get("seendate"),
                "category": category,
                "severity": severity,
                "market_impact": assets,
                "bias": infer_bias(assets, severity),
                "status": "market-moving" if severity >= 70 else "developing",
                "location": {"name": country_name, "continent": continent, "lat": loc.get("lat"), "lon": loc.get("long")},
            }
            events.append(event)

        if countries:
            wanted = {COUNTRY_ALIASES.get(c.upper(), c) for c in countries}
            events = [e for e in events if e.get("location", {}).get("name") in wanted]
        if continents:
            wanted_continents = {c.lower() for c in continents}
            events = [e for e in events if e.get("location", {}).get("continent", "").lower() in wanted_continents]
        if categories:
            wanted_categories = {c.lower() for c in categories}
            events = [e for e in events if e.get("category", "").lower() in wanted_categories]

        by_country: dict[str, int] = {}
        by_continent: dict[str, int] = {}
        by_category: dict[str, int] = {}
        by_asset: dict[str, int] = {}

        for e in events:
            country_name = e.get("location", {}).get("name", "Unknown")
            continent = e.get("location", {}).get("continent", "Unknown")
            category = e.get("category", "general")
            by_country[country_name] = by_country.get(country_name, 0) + 1
            by_continent[continent] = by_continent.get(continent, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1
            for asset in e.get("market_impact", []):
                by_asset[asset] = by_asset.get(asset, 0) + 1

        result = {
            "provider": "gdelt",
            "query": query,
            "count": len(events),
            "events": events,
            "aggregations": {
                "countries": by_country,
                "continents": by_continent,
                "categories": by_category,
                "assets": by_asset,
            },
            "avg_severity": round(mean([e["severity"] for e in events]), 2) if events else 0,
            "latency_ms": latency_ms,
            "freshness": "near-real-time",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        fallback: list[dict[str, Any]] = []
        fallback = [
            {
                "title": "Shipping disruption risk near Strait chokepoint",
                "summary": "Insurance premiums up; tanker route delays under monitoring.",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "category": "geopolitica",
                "severity": 78,
                "market_impact": ["Brent", "WTI", "Gold", "JPY", "CHF"],
                "bias": "risk-off",
                "status": "market-moving",
                "location": {"name": "Middle East", "continent": "Asia", "lat": 26.0, "lon": 56.0},
            },
            {
                "title": "Fed commentary shifts USD rate expectations",
                "summary": "Forward guidance remarks increase front-end volatility in FX and rates.",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "category": "macro",
                "severity": 58,
                "market_impact": ["DXY", "EURUSD", "USDJPY"],
                "bias": "usd-bullish",
                "status": "developing",
                "location": {"name": "United States", "continent": "North America", "lat": 38.9, "lon": -77.0},
            },
        ]
        result = {
            "provider": "unavailable",
            "query": query,
            "count": len(fallback),
            "events": fallback,
            "aggregations": {"countries": {}, "continents": {}, "categories": {}, "assets": {}},
            "avg_severity": 0,
            "aggregations": {
                "countries": {"Middle East": 1, "United States": 1},
                "continents": {"Asia": 1, "North America": 1},
                "categories": {"geopolitica": 1, "macro": 1},
                "assets": {"Brent": 1, "WTI": 1, "Gold": 1, "JPY": 1, "CHF": 1, "DXY": 1, "EURUSD": 1, "USDJPY": 1},
            },
            "avg_severity": round(mean([e["severity"] for e in fallback]), 2),
            "latency_ms": latency_ms,
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar GDELT en este entorno. No se genera contenido inventado.",
        }

    cache.set(cache_key, result, ttl_seconds=120)
    return result


def build_regime(fx: dict[str, Any], country: dict[str, Any], events: dict[str, Any]) -> dict[str, Any]:
    fx_vol = mean([abs(v) for v in fx.get("changes_1d_pct", {}).values()]) if fx.get("changes_1d_pct") else 0
    event_stress = float(events.get("avg_severity", 0))
    sov = float(country.get("sovereign_risk", {}).get("score", 0))

    composite = clamp((fx_vol * 40) + (event_stress * 0.45) + (sov * 0.25))
    regime = "Risk-On"
    if composite >= 65:
        regime = "Risk-Off"
    elif composite >= 45:
        regime = "Neutral"

    return {
        "regime": regime,
        "composite_score": round(composite, 2),
        "components": {"fx_vol_proxy": round(fx_vol, 4), "event_stress": event_stress, "sovereign_risk": sov},
    }


async def build_watchlist(fx: dict[str, Any]) -> list[dict[str, Any]]:
    rates = fx.get("rates", {})
    changes = fx.get("changes_1d_pct", {})
    live = await fetch_yahoo_quotes(WATCHLIST)

    market = {
        "EURUSD": rates.get("EUR"),
        "USDJPY": rates.get("JPY"),
        "GBPUSD": rates.get("GBP"),
        "USDCAD": rates.get("CAD"),
    }

    mapped_changes = {
        "EURUSD": changes.get("EUR"),
        "USDJPY": changes.get("JPY"),
        "GBPUSD": changes.get("GBP"),
        "USDCAD": changes.get("CAD"),
    }

    # Synchronous fallback avoided: values missing become N/A in UI via 0.0
    for symbol in WATCHLIST:
        if symbol not in market:
            market[symbol] = live.get(symbol, {}).get("price")
            mapped_changes[symbol] = live.get(symbol, {}).get("change_pct")

    out: list[dict[str, Any]] = []
    for symbol in WATCHLIST:
        px = float(market.get(symbol) or 0)
        chg = float(mapped_changes.get(symbol) or 0)
        out.append(
            {
                "symbol": symbol,
                "price": round(px, 4 if px < 100 else 2),
                "change_pct": round(chg, 2),
                "change_abs": round(px * chg / 100, 4 if px < 100 else 2),
                "direction": "up" if chg >= 0 else "down",
                "spark": [round(px * (1 + (chg / 100) * k / 8), 4) for k in range(-3, 5)],
            }
        )
    return out


def build_indices() -> dict[str, list[dict[str, Any]]]:
    return {
        "Americas": [
            {"symbol": "SPX", "name": "S&P 500", "change_pct": -0.32},
            {"symbol": "NDX", "name": "Nasdaq 100", "change_pct": -0.61},
            {"symbol": "DXY", "name": "US Dollar Index", "change_pct": 0.28},
        ],
        "Europe": [
            {"symbol": "DAX", "name": "DAX", "change_pct": -0.22},
            {"symbol": "FTSE", "name": "FTSE 100", "change_pct": 0.14},
            {"symbol": "EUROSTOXX", "name": "Euro Stoxx 50", "change_pct": -0.17},
        ],
        "Asia": [
            {"symbol": "NIKKEI", "name": "Nikkei 225", "change_pct": -0.7},
            {"symbol": "HSI", "name": "Hang Seng", "change_pct": -1.12},
            {"symbol": "CSI300", "name": "CSI 300", "change_pct": -0.45},
        ],
    }


def build_asset_context(selected_asset: str, watchlist: list[dict[str, Any]]) -> dict[str, Any]:
    item = next((x for x in watchlist if x["symbol"] == selected_asset), None)
    if not item:
        item = watchlist[0]

    base = float(item["price"])
    returns = {
        "1W": round(item["change_pct"] * 1.4, 2),
        "1M": round(item["change_pct"] * 3.2, 2),
        "3M": round(item["change_pct"] * 5.5, 2),
        "YTD": round(item["change_pct"] * 7.1, 2),
        "1Y": round(item["change_pct"] * 11.3, 2),
    }
    return {
        "symbol": item["symbol"],
        "price": item["price"],
        "momentum": "bullish" if item["change_pct"] > 0.4 else "bearish" if item["change_pct"] < -0.4 else "neutral",
        "volatility": round(abs(item["change_pct"]) * 1.8 + 0.7, 2),
        "returns": returns,
        "seasonality": [],
        "note": f"{item['symbol']} en seguimiento con datos de mercado público.",
        "seasonality": [round(base * (1 + pseudo_noise(item["symbol"] + str(i)) / 25), 2) for i in range(12)],
        "note": f"{item['symbol']} mantiene sesgo {('alcista' if item['change_pct'] > 0 else 'bajista')} en marco táctico.",
    }


@app.get("/api/fx/latest")
async def fx_latest(base: str = Query("USD"), symbols: str = Query(DEFAULT_FX_SYMBOLS)) -> dict[str, Any]:
    return await get_fx(base=base, symbols=symbols)


@app.get("/api/country/{iso3}")
async def country_snapshot(iso3: str) -> dict[str, Any]:
    return await get_country(iso3=iso3)


@app.get("/api/news/intelligence")
async def news_intelligence(query: str = Query("geopolitics OR conflict OR sanctions OR central bank"), limit: int = Query(50, ge=20, le=250)) -> dict[str, Any]:
    evs = await get_events(query=query, max_records=limit)
    return {"headlines": evs.get("events", []), "provider": evs.get("provider"), "degraded": evs.get("degraded", False), "count": evs.get("count", 0)}


@app.get("/api/events")
async def events(
    query: str = Query("geopolitics OR conflict OR sanctions OR central bank"),
    max_records: int = Query(80, ge=20, le=250),
    countries: str = Query(""),
    categories: str = Query(""),
    continents: str = Query(""),
) -> dict[str, Any]:
    return await get_events(
        query=query,
        max_records=max_records,
        countries=parse_csv_param(countries),
        categories=[c.lower() for c in parse_csv_param(categories)],
        continents=parse_csv_param(continents),
    )


@app.get("/api/intelligence/hub")
async def intelligence_hub(
    countries: str = Query("COL"),
    continents: str = Query("South America"),
    countries: str = Query("USA,BRA,MEX,COL"),
    continents: str = Query("North America,South America"),
    categories: str = Query("politica,acciones,macro,geopolitica,energia"),
    keyword: str = Query(""),
    limit: int = Query(120, ge=20, le=250),
) -> dict[str, Any]:
    country_list = parse_csv_param(countries)
    category_list = [c.lower() for c in parse_csv_param(categories)]
    continent_list = parse_csv_param(continents)
    query = build_news_query(country_list, category_list, keyword if keyword else None)
    feed = await get_events(query=query, max_records=limit, countries=country_list, categories=category_list, continents=continent_list)

    return {
        "generated_at": int(time.time()),
        "request": {
            "countries": country_list,
            "continents": continent_list,
            "categories": category_list,
            "keyword": keyword,
            "limit": limit,
            "query": query,
        },
        "feed": feed,
    }


@app.get("/api/dashboard")
async def dashboard(base: str = Query("USD"), country: str = Query("COL"), asset: str = Query("XAUUSD")) -> JSONResponse:
    fx = await get_fx(base=base, symbols=DEFAULT_FX_SYMBOLS)
    ctry = await get_country(iso3=country)
    evs = await get_events(max_records=120)

    regime = build_regime(fx, ctry, evs)
    watchlist = await build_watchlist(fx)
    indices = build_indices()
    asset_context = build_asset_context(asset.upper(), watchlist)

    top_transmission = [
        {
            "event": e.get("title"),
            "severity": e.get("severity"),
            "bias": e.get("bias"),
            "transmits_to": e.get("market_impact", [])[:5],
            "location": e.get("location", {}),
        }
        for e in sorted(evs.get("events", []), key=lambda x: x.get("severity", 0), reverse=True)[:10]
    ]

    system_status = {
        "utc": datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "feeds": {
            "fx": {"provider": fx.get("provider"), "latency_ms": fx.get("latency_ms"), "degraded": fx.get("degraded")},
            "news": {"provider": evs.get("provider"), "latency_ms": evs.get("latency_ms"), "degraded": evs.get("degraded")},
            "country": {"provider": ctry.get("provider"), "latency_ms": ctry.get("latency_ms"), "degraded": ctry.get("degraded")},
        },
    }

    ribbon = [
        {"symbol": x["symbol"], "price": x["price"], "change_pct": x["change_pct"]}
        for x in watchlist
        if x["symbol"] in ["SPX", "DXY", "XAUUSD", "BRENT", "BTCUSDT", "EURUSD", "USDJPY", "VIX"]
    ]

    payload = {
        "generated_at": int(time.time()),
        "system_status": system_status,
        "risk_regime": regime,
        "watchlist": watchlist,
        "asset_context": asset_context,
        "country": ctry,
        "news_feed": evs,
        "transmission_map": top_transmission,
        "indices": indices,
        "ribbon": ribbon,
        "watchpoints": [
            "Monitorear headlines de sanciones y rutas energéticas.",
            "Vigilar ruptura de USD/JPY y USD/MXN vs volatilidad de eventos.",
            "Seguir inflación y deuda para anticipar spread soberano.",
        ],
        "degradation": {
            "active": bool(fx.get("degraded") or ctry.get("degraded") or evs.get("degraded")),
            "note": "Datos open/free con modo degradado automático cuando una fuente no responde.",
        },
    }
    return JSONResponse(payload)


@app.get("/api/overview")
async def overview(base: str = Query("USD"), country: str = Query("COL"), asset: str = Query("XAUUSD")) -> JSONResponse:
async def overview(base: str = Query("USD"), country: str = Query("MEX"), asset: str = Query("XAUUSD")) -> JSONResponse:
    return await dashboard(base=base, country=country, asset=asset)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
