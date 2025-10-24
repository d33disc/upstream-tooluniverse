# scripts/harvest_datagov.py
import os, json, time, requests, argparse, math
from urllib.parse import urlparse
from pathlib import Path

DATA_GOV = "https://catalog.data.gov/api/3/action/package_search"
TRUST_TLDS = (".gov", ".mil", ".int", ".edu")
KEEP_CTYPES = ("application/json", "application/vnd.api+json", "application/ld+json")

VSD_DIR = Path(os.environ.get("TOOLUNIVERSE_VSD_DIR", Path.home() / ".tooluniverse" / "vsd"))
CATALOG_DIR = VSD_DIR / "catalog"
CATALOG_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = CATALOG_DIR / "vsd_catalog_candidates.json"

def is_trusted(url: str) -> bool:
    TRUSTED_DOMAINS = [
        "clinicaltrials.gov","api.fda.gov","data.nih.gov","ncbi.nlm.nih.gov",
        "pubchem.ncbi.nlm.nih.gov","chembl.org","ebi.ac.uk","ensembl.org","uniprot.org",
        "rcsb.org","humanproteinatlas.org","genome.jp","who.int","ema.europa.eu",
        "zinc20.docking.org","cdc.gov","data.cdc.gov","data.gov","nasa.gov","noaa.gov",
    ]
    return any(dom in url for dom in TRUSTED_DOMAINS) or (
        url.endswith(".gov") or url.endswith(".mil") or url.endswith(".edu")
    )

def fetch_page(q: str, start=0, rows=100):
    r = requests.get(DATA_GOV, params={"q": q, "start": start, "rows": rows}, timeout=45)
    r.raise_for_status()
    return r.json()["result"]

def extract_json_endpoints(pkg):
    out = []
    for r in pkg.get("resources", []):
        url = (r.get("url") or "").strip()
        if not url or not is_trusted(url):
            continue
        fmt = (r.get("format") or "").lower()
        ctype = (r.get("mimetype") or "").lower()
        if any(ext in fmt for ext in ["json", "csv", "xml"]) \
            or any(k in ctype for k in KEEP_CTYPES) \
            or url.lower().endswith((".json", ".geojson", ".csv", ".xml")):
                out.append(url)
    return out

def harvest(query="api OR JSON", max_items=200, rows=100):
    """Harvest up to max_items candidates by paging Data.gov"""
    seen = set(); items = []
    pages = math.ceil(max_items / rows)
    start = 0
    for _ in range(pages):
        res = fetch_page(query, start=start, rows=rows)
        for pkg in res.get("results", []):
            eps = extract_json_endpoints(pkg)
            for ep in eps:
                host = (urlparse(ep).hostname or "").lower()
                key = (host, ep)
                if key in seen:
                    continue
                seen.add(key)
                items.append({
                    "domain": host,
                    "label": pkg.get("title") or host,
                    "registry": "data.gov",
                    "endpoint": ep,
                    "license": (pkg.get("license_title") or "unknown"),
                    "trust": 0.9 if host.endswith(".gov") else 0.85,
                    "freshness": pkg.get("metadata_modified") or pkg.get("modified") or "",
                    "api_kind": "rest",
                    "tags": [t.get("name") for t in (pkg.get("tags") or []) if isinstance(t, dict)],
                    "status": "candidate"
                })
        start += len(res.get("results", []))
        if start >= res.get("count", 0) or len(items) >= max_items:
            break
        time.sleep(0.2)
    return items[:max_items]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=200,
                        help="Number of candidates to fetch (default 200)")
    parser.add_argument("--query", type=str, default="api OR JSON",
                        help="Search query string")
    args = parser.parse_args()

    items = harvest(query=args.query, max_items=args.n)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    print(f" Wrote {len(items)} candidates → {OUT_PATH}")

if __name__ == "__main__":
    main()
