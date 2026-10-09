#!/usr/bin/env python3
"""Download freely licensed country landmark photos from Wikimedia Commons.
Run in GitHub Actions or locally. Check credits in landscapes/CREDITS.md.
"""
import json, os, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
from io import BytesIO
from html import unescape

SEARCHES = {
 "kr": "Gyeongbokgung palace Seoul",
 "jp": "Mount Fuji Chureito pagoda",
 "fr": "Eiffel Tower Paris",
 "br": "Christ the Redeemer Rio de Janeiro",
 "au": "Sydney Opera House harbour",
 "cn": "Great Wall China Mutianyu",
 "ca": "Niagara Falls Canada",
 "us": "Statue of Liberty New York",
 "gb": "Big Ben London",
 "de": "Brandenburg Gate Berlin",
 "it": "Colosseum Rome",
}
API="https://commons.wikimedia.org/w/api.php"
HEADERS={"User-Agent":"WorldCatchEducationalGame/1.0 (Wikimedia Commons attribution; educational game)"}
def request(params):
    url=API+"?"+urllib.parse.urlencode(params)
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
def clean(s):
    return re.sub(r"<[^>]+>","",unescape(s or "")).strip()
def get_photo(term):
    result=request({"action":"query","generator":"search","gsrsearch":"filetype:bitmap "+term,
        "gsrnamespace":6,"gsrlimit":35,"prop":"imageinfo","iiprop":"url|extmetadata|size","format":"json"})
    choices=[]
    for page in result.get("query",{}).get("pages",{}).values():
        info=(page.get("imageinfo") or [{}])[0]
        meta=info.get("extmetadata",{})
        license_name=clean(meta.get("LicenseShortName",{}).get("value",""))
        # CC BY and CC0 are preferred; exclude share-alike to keep derivative licensing simple.
        if not re.match(r"^(CC0|CC BY [234]\\.0)$",license_name):continue
        if info.get("width",0)<1100 or info.get("height",0)<650:continue
        url=info.get("url","")
        if not url.lower().split("?")[0].endswith((".jpg",".jpeg",".png")):continue
        choices.append((info.get("width",0)/max(info.get("height",1),1),page,info,license_name))
    if not choices:raise RuntimeError("No suitable CC0/CC BY photo found for "+term)
    # Prefer landscape framing and high resolution.
    choices.sort(key=lambda c:(1.3<=c[0]<=2.4,c[2].get("width",0)),reverse=True)
    return choices[0]
def main():
    out=Path("landscapes");out.mkdir(exist_ok=True)
    credits=["# Photo credits","", "Images downloaded from Wikimedia Commons. Attribution and license details follow.",""]
    for code,term in SEARCHES.items():
        try:
            ratio,page,info,license_name=get_photo(term)
            req=urllib.request.Request(info["url"],headers=HEADERS)
            with urllib.request.urlopen(req,timeout=70) as r:raw=r.read(22_000_000)
            im=Image.open(BytesIO(raw)).convert("RGB")
            im=ImageOps.fit(im,(1600,900),method=Image.Resampling.LANCZOS,centering=(.5,.48))
            im.save(out/(code+".jpg"),"JPEG",quality=81,optimize=True)
            m=info.get("extmetadata",{})
            author=clean(m.get("Artist",{}).get("value","")) or "See source"
            license_url=clean(m.get("LicenseUrl",{}).get("value",""))
            source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(page["title"].replace(" ","_"),safe=":/()")
            credits.extend([f"## {code.upper()} — {term}",f"- Creator: {author}",f"- Source: {source}",f"- License: {license_name} — {license_url}","- Modification: cropped/resized to 1600 × 900 for the game.",""])
            print("Downloaded",code,page["title"])
        except Exception as exc:
            print("FAILED",code,str(exc))
            raise
        time.sleep(.35)
    (out/"CREDITS.md").write_text("\\n".join(credits),encoding="utf-8")
if __name__=="__main__":main()
