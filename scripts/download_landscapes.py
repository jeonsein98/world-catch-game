#!/usr/bin/env python3
"""Bundle landscape photographs from Unsplash's image CDN.
Downloads run in GitHub Actions, not in the children's browsers.
Source: https://unsplash.com/license (free use; attribution retained).
"""
from pathlib import Path
from io import BytesIO
import time, urllib.request, urllib.error
from PIL import Image, ImageOps

PHOTOS = {
 "kr": ("Gyeongbokgung Palace, Seoul", "photo-1534274988757-a28bf1a57c17"),
 "jp": ("Mount Fuji, Japan", "photo-1493976040374-85c8e12f0c0e"),
 "fr": ("Eiffel Tower, Paris", "photo-1502602898657-3e91760cbb34"),
 "br": ("Christ the Redeemer, Rio de Janeiro", "photo-1483728642387-6c3bdd6c93e5"),
 "au": ("Sydney Opera House", "photo-1506973035872-a4ec16b8e8d9"),
 "cn": ("Great Wall of China", "photo-1508804185872-d7badad00f7d"),
 "ca": ("Niagara Falls, Canada", "photo-1517935706615-2717063c2225"),
 "us": ("Statue of Liberty, New York", "photo-1485738422979-f5c462d49f74"),
 "gb": ("Big Ben, London", "photo-1513635269975-59663e0ac1ad"),
 "de": ("Brandenburg Gate, Berlin", "photo-1467269204594-9661b134dd2b"),
 "it": ("Colosseum, Rome", "photo-1516483638261-f4dbaf036963"),
}
OUT=Path("landscapes")
OUT.mkdir(exist_ok=True)
credits=["# Landscape photo credits","",
         "Images sourced from Unsplash, https://unsplash.com/license.",
         "Photographs were resized/cropped to 1600 × 900 for the educational game.",
         "Individual photographers and landmark accuracy should be reviewed before public distribution.",""]
missing=[]
for country,(landmark,pid) in PHOTOS.items():
    url=f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w=1600&h=900&q=82"
    path=OUT/f"{country}.jpg"
    if path.exists():
        print("Existing:",country,flush=True)
    else:
        success=False
        for attempt in range(3):
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (EducationalGame; world-catch-game)"})
                with urllib.request.urlopen(req,timeout=45) as response:
                    raw=response.read(12_000_000)
                img=Image.open(BytesIO(raw)).convert("RGB")
                img=ImageOps.fit(img,(1600,900),method=Image.Resampling.LANCZOS)
                img.save(path,"JPEG",quality=83,optimize=True)
                print("Saved:",country,landmark,len(raw),flush=True)
                success=True
                break
            except Exception as e:
                print("Retry:",country,str(e),flush=True)
                time.sleep(4*(attempt+1))
        if not success:missing.append(country)
    credits += [f"## {country.upper()} — {landmark}",f"- Image URL: {url}",f"- Source: https://unsplash.com/photos/{pid.removeprefix('photo-')}", "- License: https://unsplash.com/license",""]
(OUT/"CREDITS.md").write_text("\n".join(credits),encoding="utf-8")
(OUT/"MISSING.txt").write_text("\n".join(missing)+"\n" if missing else "All 11 photos downloaded.\n",encoding="utf-8")
print("MISSING:",missing,flush=True)
