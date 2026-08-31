"""P0 skill 打包: zip + sha256 → manifest (卖家侧发布前置动作)
输出: packages/<skill_id>.zip + manifests.json
"""
import json, os, zipfile, hashlib, datetime

SKILLS = {
    "silver-price-collection": r"C:/Users/Administrator/.hermes/skills/intelligence/silver-price-collection",
    "tianji-ge": r"C:/Users/Administrator/.hermes/skills/intelligence/tianji-ge",
    "browser-workspace": r"C:/Users/Administrator/.hermes/skills/software-development/browser-workspace",
}
OUT = r"C:/Users/Administrator/.hermes/data/skill-market/packages"
os.makedirs(OUT, exist_ok=True)

manifests = {}
for sid, src in SKILLS.items():
    pkg = os.path.join(OUT, f"{sid}.zip")
    with zipfile.ZipFile(pkg, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.join(sid, os.path.relpath(full, src))
                z.write(full, arc)
    h = hashlib.sha256(open(pkg, "rb").read()).hexdigest()
    size = os.path.getsize(pkg)
    manifests[sid] = {"package": pkg, "manifest_hash": h, "size_bytes": size, "packed_at": datetime.datetime.now().isoformat()}
    print(f"{sid:28s} {size:8d}B sha256={h[:16]}...")

with open(r"C:/Users/Administrator/.hermes/data/skill-market/manifests.json", "w", encoding="utf-8") as f:
    json.dump(manifests, f, ensure_ascii=False, indent=1)
print("\nmanifest 已写: skill-market/manifests.json")
