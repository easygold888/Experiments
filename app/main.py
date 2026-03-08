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

app = FastAPI(title="Planetary Market Intelligence", version="0.2.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

HTTP_TIMEOUT = 15.0
DEFAULT_SYMBOLS = "EUR,JPY,GBP,MXN,BRL,CHF"


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


def score_event_severity(title: str | None) -> int:
    text = (title or "").lower()
    score = 25
    if any(k in text for k in ["war", "attack", "missile", "invasion", "conflict"]):
        score += 35
    if any(k in text for k in ["sanction", "oil", "gas", "pipeline", "shipping", "strait"]):
        score += 20
    if any(k in text for k in ["ceasefire", "deal", "talks"]):
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
        assets.extend(["Gold", "CHF", "JPY"])
    return sorted(set(assets))


def compute_sovereign_risk(indicators: dict[str, dict[str, Any]]) -> dict[str, Any]:
    inflation = float(indicators.get("inflation", {}).get("value") or 0)
    debt_gdp = float(indicators.get("debt_gdp", {}).get("value") or 0)
    gdp_growth = float(indicators.get("gdp_growth", {}).get("value") or 0)
    reserves = float(indicators.get("reserves", {}).get("value") or 0)

    score = 35.0
    score += max(0, inflation - 4) * 3.5
    score += max(0, debt_gdp - 60) * 0.45
    score += max(0, 1.5 - gdp_growth) * 8.0

    # Reserva baja sube riesgo (normalización simple)
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


async def fetch_json(url: str, params: dict[str, Any], timeout: float = HTTP_TIMEOUT) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout, trust_env=False) as client:
        resp = await client.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


async def get_fx(base: str = "USD", symbols: str = DEFAULT_SYMBOLS) -> dict[str, Any]:
    base = base.upper()
    symbols = symbols.upper()
    cache_key = f"fx:{base}:{symbols}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    try:
        latest = await fetch_json("https://api.frankfurter.app/latest", {"from": base, "to": symbols})
        prev_date = (datetime.now(tz=UTC) - timedelta(days=2)).strftime("%Y-%m-%d")
        prev = await fetch_json(f"https://api.frankfurter.app/{prev_date}", {"from": base, "to": symbols})

        rates = latest.get("rates", {})
        prev_rates = prev.get("rates", {})
        changes_1d: dict[str, float] = {}
        for k, v in rates.items():
            p = prev_rates.get(k)
            if p:
                changes_1d[k] = round(((v - p) / p) * 100, 4)

        result = {
            "provider": "frankfurter",
            "base": latest.get("base", base),
            "date": latest.get("date"),
            "rates": rates,
            "changes_1d_pct": changes_1d,
            "freshness": "live-ish",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        result = {
            "provider": "fallback",
            "base": base,
            "date": time.strftime("%Y-%m-%d"),
            "rates": {"EUR": 0.92, "JPY": 149.8, "GBP": 0.78, "MXN": 16.9, "BRL": 5.2, "CHF": 0.88},
            "changes_1d_pct": {"EUR": -0.15, "JPY": 0.32, "GBP": -0.08, "MXN": 0.55, "BRL": 0.41, "CHF": -0.03},
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
    }

    output: dict[str, Any] = {"iso3": iso3, "indicators": {}, "provider": "world_bank", "degraded": False}

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
    except (RequestError, httpx.HTTPStatusError):
        output = {
            "iso3": iso3,
            "provider": "fallback",
            "degraded": True,
            "note": "No se pudo consultar World Bank en este entorno.",
            "indicators": {
                "gdp_growth": {"value": 3.2, "date": "2023"},
                "inflation": {"value": 5.5, "date": "2023"},
                "debt_gdp": {"value": 46.1, "date": "2023"},
                "reserves": {"value": 220_000_000_000, "date": "2023"},
            },
        }

    output["sovereign_risk"] = compute_sovereign_risk(output.get("indicators", {}))

    if not output.get("indicators"):
        output["degraded"] = True
        output["note"] = "Sin indicadores disponibles"

    cache.set(cache_key, output, ttl_seconds=3600)
    return output


async def get_events(query: str = "geopolitics OR conflict OR sanctions", max_records: int = 30) -> dict[str, Any]:
    cache_key = f"events:{query}:{max_records}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    try:
        raw = await fetch_json(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            {"query": query, "mode": "ArtList", "maxrecords": str(max_records), "format": "json", "sort": "HybridRel"},
            timeout=20.0,
        )
        articles = raw.get("articles", [])
        events: list[dict[str, Any]] = []
        for article in articles:
            loc = article.get("sourceCountryLocation", {}) or {}
            title = article.get("title")
            events.append(
                {
                    "title": title,
                    "url": article.get("url"),
                    "source": article.get("domain"),
                    "seendate": article.get("seendate"),
                    "severity": score_event_severity(title),
                    "market_impact": classify_event_impact(title),
                    "location": {"name": article.get("sourceCountry"), "lat": loc.get("lat"), "lon": loc.get("long")},
                }
            )

        result = {
            "provider": "gdelt",
            "query": query,
            "count": len(events),
            "events": events,
            "avg_severity": round(mean([e["severity"] for e in events]), 2) if events else 0,
            "freshness": "near-real-time",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        fallback = [
            {
                "title": "Simulated: maritime disruption risk at chokepoint",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "severity": 78,
                "market_impact": ["Brent", "WTI", "Gold", "JPY", "CHF"],
                "location": {"name": "Middle East", "lat": 26.0, "lon": 56.0},
            },
            {
                "title": "Simulated: sanctions escalation headline",
                "url": "#",
                "source": "fallback",
                "seendate": time.strftime("%Y%m%d%H%M%S"),
                "severity": 72,
                "market_impact": ["EUR", "Gold", "DXY"],
                "location": {"name": "Eastern Europe", "lat": 50.0, "lon": 30.0},
            },
        ]
        result = {
            "provider": "fallback",
            "query": query,
            "count": len(fallback),
            "events": fallback,
            "avg_severity": round(mean([e["severity"] for e in fallback]), 2),
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar GDELT en este entorno.",
        }

    cache.set(cache_key, result, ttl_seconds=300)
    return result


def build_what_moved(fx: dict[str, Any], country: dict[str, Any], events: dict[str, Any]) -> list[dict[str, Any]]:
    narratives: list[dict[str, Any]] = []
    changes = fx.get("changes_1d_pct", {})
    if changes:
        top = sorted(changes.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
        for ccy, chg in top:
            direction = "debilidad" if chg > 0 else "fortaleza"
            narratives.append(
                {
                    "title": f"USD/{ccy} {chg:+.2f}% en 1D",
                    "why_it_matters": f"Movimiento de {direction} relativa en {ccy} frente a USD.",
                    "confidence": 0.66,
                }
            )

    avg_sev = float(events.get("avg_severity", 0))
    if avg_sev >= 65:
        narratives.append(
            {
                "title": "Riesgo geopolítico elevado en feed global",
                "why_it_matters": "Mayor probabilidad de flujo hacia activos refugio (JPY/CHF/Oro).",
                "confidence": 0.72,
            }
        )

    sov = country.get("sovereign_risk", {}).get("score", 0)
    if sov >= 55:
        narratives.append(
            {
                "title": f"Riesgo soberano {country.get('iso3')} en zona {country.get('sovereign_risk', {}).get('bucket')}",
                "why_it_matters": "Puede amplificar sensibilidad FX y primas de riesgo país.",
                "confidence": 0.69,
            }
        )

    return narratives[:5]


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


@app.get("/api/fx/latest")
async def fx_latest(base: str = Query("USD"), symbols: str = Query(DEFAULT_SYMBOLS)) -> dict[str, Any]:
    return await get_fx(base=base, symbols=symbols)


@app.get("/api/country/{iso3}")
async def country_snapshot(iso3: str) -> dict[str, Any]:
    return await get_country(iso3=iso3)


@app.get("/api/events")
async def events(query: str = Query("geopolitics OR conflict OR sanctions"), max_records: int = Query(30, ge=1, le=80)) -> dict[str, Any]:
    return await get_events(query=query, max_records=max_records)


@app.get("/api/overview")
async def overview(base: str = Query("USD"), country: str = Query("MEX")) -> JSONResponse:
    fx = await get_fx(base=base, symbols=DEFAULT_SYMBOLS)
    ctry = await get_country(iso3=country)
    evs = await get_events()

    what_moved = build_what_moved(fx, ctry, evs)
    regime = build_regime(fx, ctry, evs)

    transmission = [
        {
            "event": e.get("title"),
            "severity": e.get("severity"),
            "transmits_to": e.get("market_impact", [])[:5],
            "location": e.get("location", {}),
        }
        for e in sorted(evs.get("events", []), key=lambda x: x.get("severity", 0), reverse=True)[:8]
    ]

    payload = {
        "generated_at": int(time.time()),
        "fx": fx,
        "country": ctry,
        "events": evs,
        "what_moved": what_moved,
        "risk_regime": regime,
        "transmission_map": transmission,
        "watchpoints": [
            "Monitorear headlines de sanciones y rutas energéticas.",
            "Vigilar ruptura de USD/JPY y USD/MXN vs volatilidad de eventos.",
            "Seguir cambios de inflación y deuda para riesgo soberano.",
        ],
        "degradation": {
            "active": bool(fx.get("degraded") or ctry.get("degraded") or evs.get("degraded")),
            "note": "Datos open/free con modo degradado automático cuando una fuente no responde.",
        },
    }
    return JSONResponse(payload)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
