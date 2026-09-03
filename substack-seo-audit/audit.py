import json, sys, time, urllib.request

PUBS = {"danielrusnok": "https://danielrusnok.substack.com",
        "readsinmotion": "https://readsinmotion.substack.com"}

def fetch(base):
    posts, off = [], 0
    while True:
        u = f"{base}/api/v1/archive?sort=new&limit=50&offset={off}"
        r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(r))
        if not d:
            break
        posts += d
        off += 50
        if len(d) < 50:
            break
        time.sleep(0.4)
    return posts

def audit(p):
    s = lambda k: (p.get(k) or "").strip()
    st, sd, t, sub, soc = s("search_engine_title"), s("search_engine_description"), s("title"), s("subtitle"), s("social_title")
    tags = [x.get("name") for x in (p.get("postTags") or [])]
    i = []
    if not st: i.append("no-seo-title")
    elif len(st) > 60: i.append(f"seo-title-long({len(st)})")
    if not sd: i.append("no-seo-desc")
    elif len(sd) < 70: i.append(f"seo-desc-short({len(sd)})")
    elif len(sd) > 165: i.append(f"seo-desc-long({len(sd)})")
    if len(t) > 60: i.append(f"title-long({len(t)})")
    if not soc: i.append("no-social-title")
    if not sub: i.append("no-subtitle")
    if not tags: i.append("no-tags")
    if (p.get("wordcount") or 0) < 400: i.append(f"thin({p.get('wordcount')}w)")
    return {"id": p["id"], "date": (p.get("post_date") or "")[:10], "title": t, "subtitle": sub,
            "seo_title": st, "seo_desc": sd, "social_title": soc, "slug": p.get("slug"),
            "wordcount": p.get("wordcount"), "tags": tags, "url": p.get("canonical_url"), "issues": i}

if __name__ == "__main__":
    acct = sys.argv[1] if len(sys.argv) > 1 else "danielrusnok"
    rows = sorted((audit(x) for x in fetch(PUBS[acct])), key=lambda r: r["date"])
    broken = [r for r in rows if r["issues"]]
    print(f"# SEO meta audit — {acct} — {len(rows)} posts, {len(broken)} with issues\n")
    for r in broken:
        print(f"{r['date']}  id={r['id']}  {r['title']}")
        print(f"    slug={r['slug']}  wc={r['wordcount']}  tags={r['tags'] or '-'}")
        print(f"    seo_title={r['seo_title'] or '(empty)'}")
        print(f"    seo_desc={r['seo_desc'] or '(empty)'}")
        print(f"    subtitle={r['subtitle'][:120]}")
        print(f"    ISSUES: {', '.join(r['issues'])}\n")
    from collections import Counter
    c = Counter(i.split("(")[0] for r in rows for i in r["issues"])
    print("## Aggregate")
    for k, v in c.most_common():
        print(f"{v:3}x {k}")
    json.dump(rows, open(f"/tmp/seo-audit-{acct}.json", "w"), ensure_ascii=False, indent=1)
    print(f"\nRaw: /tmp/seo-audit-{acct}.json")
