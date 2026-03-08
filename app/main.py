from __future__ import annotations

import os
import time
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from httpx import RequestError

app = FastAPI(title="Planetary Market Intelligence", version="0.3.0")
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


def clamp(v: float, min_v: float = 0.0, max_v: float = 100.0) -> float:
    return max(min_v, min(max_v, v))


def pct_change(a: float, b: float) -> float:
    if not b:
        return 0.0
    return round(((a - b) / b) * 100, 4)


def pseudo_noise(seed: str) -> float:
    n = sum(ord(c) for c in seed)
    return ((n % 100) - 50) / 100.0


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
    return sorted(set(assets))


def infer_bias(assets: list[str], severity: int) -> str:
    if severity >= 70 and any(a in assets for a in ["Gold", "JPY", "CHF", "VIX"]):
        return "risk-off"
    if any(a in assets for a in ["Brent", "WTI"]):
        return "oil-sensitive"
    if any(a in assets for a in ["DXY", "USDJPY"]):
        return "usd-bullish"
    return "neutral"


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
        latest, latency_ms = await fetch_json("https://api.frankfurter.app/latest", {"from": base, "to": symbols})
        prev_date = (datetime.now(tz=UTC) - timedelta(days=2)).strftime("%Y-%m-%d")
        prev, _ = await fetch_json(f"https://api.frankfurter.app/{prev_date}", {"from": base, "to": symbols})

        rates = latest.get("rates", {})
        prev_rates = prev.get("rates", {})
        changes_1d = {k: pct_change(v, prev_rates.get(k, v)) for k, v in rates.items()}

        result = {
            "provider": "frankfurter",
            "base": latest.get("base", base),
            "date": latest.get("date"),
            "rates": rates,
            "changes_1d_pct": changes_1d,
            "latency_ms": latency_ms,
            "freshness": "live-ish",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        result = {
            "provider": "fallback",
            "base": base,
            "date": time.strftime("%Y-%m-%d"),
            "rates": {"EUR": 0.92, "JPY": 149.8, "GBP": 0.78, "MXN": 16.9, "BRL": 5.2, "CHF": 0.88, "CAD": 1.35, "NOK": 10.6},
            "changes_1d_pct": {"EUR": -0.15, "JPY": 0.32, "GBP": -0.08, "MXN": 0.55, "BRL": 0.41, "CHF": -0.03, "CAD": 0.18, "NOK": 0.26},
            "latency_ms": latency_ms,
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar Frankfurter en este entorno.",
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
            "provider": "fallback",
            "degraded": True,
            "note": "No se pudo consultar World Bank en este entorno.",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "indicators": {
                "gdp_growth": {"value": 3.2, "date": "2023"},
                "inflation": {"value": 5.5, "date": "2023"},
                "debt_gdp": {"value": 46.1, "date": "2023"},
                "reserves": {"value": 220_000_000_000, "date": "2023"},
                "trade_balance": {"value": -9_400_000_000, "date": "2023"},
            },
        }

    output["sovereign_risk"] = compute_sovereign_risk(output.get("indicators", {}))
    cache.set(cache_key, output, ttl_seconds=3600)
    return output


async def get_events(query: str = "geopolitics OR conflict OR sanctions OR central bank", max_records: int = 40) -> dict[str, Any]:
    cache_key = f"events:{query}:{max_records}"
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
            events.append(
                {
                    "title": title,
                    "summary": (article.get("title") or "")[0:140],
                    "url": article.get("url"),
                    "source": article.get("domain"),
                    "seendate": article.get("seendate"),
                    "category": "Geopolitics" if severity >= 55 else "Macro",
                    "severity": severity,
                    "market_impact": assets,
                    "bias": infer_bias(assets, severity),
                    "status": "market-moving" if severity >= 70 else "developing",
                    "location": {"name": article.get("sourceCountry"), "lat": loc.get("lat"), "lon": loc.get("long")},
                }
            )

        result = {
            "provider": "gdelt",
            "query": query,
            "count": len(events),
            "events": events,
            "avg_severity": round(mean([e["severity"] for e in events]), 2) if events else 0,
            "latency_ms": latency_ms,
            "freshness": "near-real-time",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        fallback = [
            {
                "title": "Shipping disruption risk near Strait chokepoint",
                "summary": "Insurance premiums up; tanker route delays under monitoring.",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "category": "Geopolitics",
                "severity": 78,
                "market_impact": ["Brent", "WTI", "Gold", "JPY", "CHF"],
                "bias": "risk-off",
                "status": "market-moving",
                "location": {"name": "Middle East", "lat": 26.0, "lon": 56.0},
            },
            {
                "title": "Central bank commentary shifts USD rate expectations",
                "summary": "Forward guidance remarks increase front-end volatility in FX.",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "category": "Central Banks",
                "severity": 58,
                "market_impact": ["DXY", "EURUSD", "USDJPY"],
                "bias": "usd-bullish",
                "status": "developing",
                "location": {"name": "United States", "lat": 38.9, "lon": -77.0},
            },
        ]
        result = {
            "provider": "fallback",
            "query": query,
            "count": len(fallback),
            "events": fallback,
            "avg_severity": round(mean([e["severity"] for e in fallback]), 2),
            "latency_ms": latency_ms,
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar GDELT en este entorno.",
        }

    cache.set(cache_key, result, ttl_seconds=180)
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


def build_watchlist(fx: dict[str, Any]) -> list[dict[str, Any]]:
    rates = fx.get("rates", {})
    changes = fx.get("changes_1d_pct", {})

    market = {
        "EURUSD": rates.get("EUR", 0.92),
        "USDJPY": rates.get("JPY", 149.8),
        "GBPUSD": rates.get("GBP", 0.78),
        "USDCAD": rates.get("CAD", 1.35),
        "BTCUSDT": 67000 * (1 + pseudo_noise("btc") / 20),
        "SILVER": 24.5 * (1 + pseudo_noise("silver") / 25),
        "DXY": 103.4 * (1 + pseudo_noise("dxy") / 40),
        "NDX": 17950 * (1 + pseudo_noise("ndx") / 35),
        "SPX": 5120 * (1 + pseudo_noise("spx") / 45),
        "XAUUSD": 2160 * (1 + pseudo_noise("xau") / 35),
        "NIKKEI": 39500 * (1 + pseudo_noise("nikkei") / 30),
        "BRENT": 82.4 * (1 + pseudo_noise("brent") / 20),
        "VIX": 15.2 * (1 + pseudo_noise("vix") / 15),
    }

    mapped_changes = {
        "EURUSD": changes.get("EUR", -0.12),
        "USDJPY": changes.get("JPY", 0.22),
        "GBPUSD": changes.get("GBP", -0.08),
        "USDCAD": changes.get("CAD", 0.1),
        "BTCUSDT": 1.2,
        "SILVER": -0.4,
        "DXY": 0.3,
        "NDX": -0.7,
        "SPX": -0.25,
        "XAUUSD": 0.35,
        "NIKKEI": -0.65,
        "BRENT": 0.95,
        "VIX": 1.8,
    }

    out: list[dict[str, Any]] = []
    for symbol in WATCHLIST:
        px = float(market.get(symbol, 0))
        chg = float(mapped_changes.get(symbol, 0))
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
        "seasonality": [round(base * (1 + pseudo_noise(item["symbol"] + str(i)) / 25), 2) for i in range(12)],
        "note": f"{item['symbol']} mantiene sesgo {('alcista' if item['change_pct']>0 else 'bajista')} en marco táctico.",
    }


@app.get("/api/fx/latest")
async def fx_latest(base: str = Query("USD"), symbols: str = Query(DEFAULT_FX_SYMBOLS)) -> dict[str, Any]:
    return await get_fx(base=base, symbols=symbols)


@app.get("/api/country/{iso3}")
async def country_snapshot(iso3: str) -> dict[str, Any]:
    return await get_country(iso3=iso3)


@app.get("/api/news/intelligence")
async def news_intelligence(query: str = Query("geopolitics OR conflict OR sanctions OR central bank"), limit: int = Query(20, ge=5, le=80)) -> dict[str, Any]:
    evs = await get_events(query=query, max_records=limit)
    return {"headlines": evs.get("events", []), "provider": evs.get("provider"), "degraded": evs.get("degraded", False)}


@app.get("/api/events")
async def events(query: str = Query("geopolitics OR conflict OR sanctions OR central bank"), max_records: int = Query(40, ge=5, le=80)) -> dict[str, Any]:
    return await get_events(query=query, max_records=max_records)


@app.get("/api/dashboard")
async def dashboard(base: str = Query("USD"), country: str = Query("MEX"), asset: str = Query("XAUUSD")) -> JSONResponse:
    fx = await get_fx(base=base, symbols=DEFAULT_FX_SYMBOLS)
    ctry = await get_country(iso3=country)
    evs = await get_events()

    regime = build_regime(fx, ctry, evs)
    watchlist = build_watchlist(fx)
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
async def overview(base: str = Query("USD"), country: str = Query("MEX"), asset: str = Query("XAUUSD")) -> JSONResponse:
    # Compat endpoint for previous frontend versions.
    return await dashboard(base=base, country=country, asset=asset)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
