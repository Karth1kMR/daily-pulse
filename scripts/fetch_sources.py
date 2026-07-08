#!/usr/bin/env python3
"""Fetch raw inputs for the Daily Pulse brief: Bengaluru news + weather.

Uses only free, keyless sources (Google News RSS, Times of India RSS,
Open-Meteo) and the Python standard library. Writes data/raw.json for the
generation step to summarize.

Usage: python3 scripts/fetch_sources.py
"""
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "data" / "raw.json"
IST = ZoneInfo("Asia/Kolkata")

FEEDS = {
    "google_news_bengaluru": "https://news.google.com/rss/search?q=Bengaluru&hl=en-IN&gl=IN&ceid=IN:en",
    "google_news_traffic": "https://news.google.com/rss/search?q=Bengaluru+traffic+OR+metro+OR+BMTC+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "google_news_events": "https://news.google.com/rss/search?q=Bengaluru+event+OR+festival+OR+concert+OR+exhibition+when:2d&hl=en-IN&gl=IN&ceid=IN:en",
    "google_news_india": "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "toi_bengaluru": "https://timesofindia.indiatimes.com/rssfeeds/-2128833038.cms",
}

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=12.9716&longitude=77.5946"
    "&current=temperature_2m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&timezone=Asia%2FKolkata&forecast_days=1"
)

WMO = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Foggy", 51: "Light drizzle", 53: "Drizzle",
    55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
    80: "Rain showers", 81: "Rain showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "DailyPulse/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_rss(xml_bytes, limit=15):
    items = []
    root = ET.fromstring(xml_bytes)
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        source = (item.findtext("source") or "").strip()
        # Google News appends " - Source" to titles; keep it, it's useful.
        if title:
            items.append({"title": title, "link": link, "published": pub, "source": source})
        if len(items) >= limit:
            break
    return items


def get_weather():
    data = json.loads(fetch(WEATHER_URL))
    cur = data.get("current", {})
    daily = data.get("daily", {})
    return {
        "now_c": cur.get("temperature_2m"),
        "condition": WMO.get(cur.get("weather_code"), "—"),
        "high_c": (daily.get("temperature_2m_max") or [None])[0],
        "low_c": (daily.get("temperature_2m_min") or [None])[0],
        "rain_chance_pct": (daily.get("precipitation_probability_max") or [None])[0],
    }


def main():
    now = datetime.now(IST)
    raw = {"fetched_at": now.isoformat(), "city": "Bengaluru", "feeds": {}, "weather": None, "errors": []}

    for name, url in FEEDS.items():
        try:
            raw["feeds"][name] = parse_rss(fetch(url))
        except Exception as e:  # keep going; a dead feed shouldn't kill the brief
            raw["errors"].append(f"{name}: {e}")
            raw["feeds"][name] = []

    try:
        raw["weather"] = get_weather()
    except Exception as e:
        raw["errors"].append(f"weather: {e}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(raw, indent=2, ensure_ascii=False))
    total = sum(len(v) for v in raw["feeds"].values())
    print(f"Wrote {OUT} — {total} headlines, weather={'ok' if raw['weather'] else 'FAILED'}, errors={len(raw['errors'])}")


if __name__ == "__main__":
    main()
