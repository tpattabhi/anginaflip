import json, sys, time, subprocess, urllib.parse

q = sys.argv[1]
out = sys.argv[2]
base = "https://api.openalex.org/works"
cursor, works = "*", []
while cursor:
    url = (
        base
        + "?"
        + urllib.parse.urlencode(
            {
                "filter": f"title_and_abstract.search:{q}",
                "per-page": 200,
                "cursor": cursor,
                "select": "id,doi,title,publication_year,cited_by_count,primary_location,abstract_inverted_index,type",
            }
        )
    )
    d = json.loads(subprocess.run(["curl", "-s", url], capture_output=True, check=True).stdout)
    works += d["results"]
    cursor = d["meta"].get("next_cursor")
    if not d["results"]:
        break
    time.sleep(0.2)
for w in works:
    inv = w.pop("abstract_inverted_index") or {}
    pos = sorted((p, t) for t, ps in inv.items() for p in ps)
    w["abstract"] = " ".join(t for _, t in pos)
    loc = w.pop("primary_location") or {}
    w["venue"] = (loc.get("source") or {}).get("display_name")
json.dump(works, open(out, "w"), indent=1)
print(len(works), "works")
