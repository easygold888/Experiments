from __future__ import annotations

import os
import time
from typing import Any

import httpx
from httpx import RequestError
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Planetary Market Intelligence", version="0.1.0")
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
        payload = await fetch_json(
            "https://api.frankfurter.app/latest",
            {"from": base, "to": symbols},
        )
        result = {
            "provider": "frankfurter",
            "base": payload.get("base", base),
            "date": payload.get("date"),
            "rates": payload.get("rates", {}),
            "freshness": "live-ish",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        result = {
            "provider": "fallback",
            "base": base,
            "date": time.strftime("%Y-%m-%d"),
            "rates": {"EUR": 0.92, "JPY": 149.8, "GBP": 0.78, "MXN": 16.9},
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

    output: dict[str, Any] = {
        "iso3": iso3,
        "indicators": {},
        "provider": "world_bank",
        "degraded": False,
    }

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, trust_env=False) as client:
            for key, code in series.items():
                url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{code}"
                resp = await client.get(url, params={"format": "json", "per_page": 100})
                resp.raise_for_status()
                body = resp.json()
                if not isinstance(body, list) or len(body) < 2:
                    continue
                points = body[1]
                latest = next((p for p in points if p.get("value") is not None), None)
                if latest:
                    output["indicators"][key] = {
                        "value": latest.get("value"),
                        "date": latest.get("date"),
                    }
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

    if not output.get("indicators"):
        output["degraded"] = True
        output["note"] = "Sin indicadores disponibles"

    cache.set(cache_key, output, ttl_seconds=3600)
    return output


async def get_events(query: str = "geopolitics OR conflict OR sanctions", max_records: int = 20) -> dict[str, Any]:
    cache_key = f"events:{query}:{max_records}"
    cached = cache.get(cache_key)
    if cached:
        return {"cache": True, **cached}

    try:
        raw = await fetch_json(
            "https://api.gdeltproject.org/api/v2/doc/doc",
            {
                "query": query,
                "mode": "ArtList",
                "maxrecords": str(max_records),
                "format": "json",
                "sort": "HybridRel",
            },
            timeout=20.0,
        )
        articles = raw.get("articles", [])
        events = []
        for article in articles:
            loc = article.get("sourceCountryLocation", {}) or {}
            events.append(
                {
                    "title": article.get("title"),
                    "url": article.get("url"),
                    "source": article.get("domain"),
                    "seendate": article.get("seendate"),
                    "location": {
                        "name": article.get("sourceCountry"),
                        "lat": loc.get("lat"),
                        "lon": loc.get("long"),
                    },
                }
            )
        result = {
            "provider": "gdelt",
            "query": query,
            "count": len(events),
            "events": events,
            "freshness": "near-real-time",
            "degraded": False,
        }
    except (RequestError, httpx.HTTPStatusError):
        result = {
            "provider": "fallback",
            "query": query,
            "count": 2,
            "freshness": "degraded-fallback",
            "degraded": True,
            "note": "No se pudo consultar GDELT en este entorno.",
            "events": [
                {
                    "title": "Simulated: maritime disruption risk at chokepoint",
                    "url": "#",
                    "source": "fallback",
                    "seendate": time.strftime("%Y%m%d%H%M%S"),
                    "location": {"name": "Middle East", "lat": 26.0, "lon": 56.0},
                },
                {
                    "title": "Simulated: sanctions escalation headline",
                    "url": "#",
                    "source": "fallback",
                    "seendate": time.strftime("%Y%m%d%H%M%S"),
                    "location": {"name": "Eastern Europe", "lat": 50.0, "lon": 30.0},
                },
            ],
        }

    cache.set(cache_key, result, ttl_seconds=300)
    return result


@app.get("/api/fx/latest")
async def fx_latest(base: str = Query("USD"), symbols: str = Query(DEFAULT_SYMBOLS)) -> dict[str, Any]:
    return await get_fx(base=base, symbols=symbols)


@app.get("/api/country/{iso3}")
async def country_snapshot(iso3: str) -> dict[str, Any]:
    return await get_country(iso3=iso3)


@app.get("/api/events")
async def events(query: str = Query("geopolitics OR conflict OR sanctions"), max_records: int = Query(20, ge=1, le=50)) -> dict[str, Any]:
    return await get_events(query=query, max_records=max_records)


@app.get("/api/overview")
async def overview(base: str = Query("USD"), country: str = Query("MEX")) -> JSONResponse:
    fx = await get_fx(base=base, symbols=DEFAULT_SYMBOLS)
    ctry = await get_country(iso3=country)
    evs = await get_events()

    return JSONResponse(
        {
            "generated_at": int(time.time()),
            "fx": fx,
            "country": ctry,
            "events": evs,
            "degradation": {
                "active": bool(fx.get("degraded") or ctry.get("degraded") or evs.get("degraded")),
                "note": "Datos open/free con modo degradado automático cuando una fuente no responde.",
            },
        }
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
