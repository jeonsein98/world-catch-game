#!/usr/bin/env python3
"""Fetch illustrative Wikipedia article photos for treasure cards.
Wikipedia images have individual licenses: review the generated SOURCES.md
and each linked Commons file page before redistributing the images.
"""
import json,time,urllib.request,urllib.parse
from io import BytesIO
from pathlib import Path
from PIL import Image,ImageOps

ITEMS={
"경복궁":"Gyeongbokgung","비빔밥":"Bibimbap","한복":"Hanbok",
"후지산":"Mount Fuji","초밥":"Sushi","기모노":"Kimono",
"에펠탑":"Eiffel Tower","크루아상":"Croissant","베레모":"Beret",
"구세주 그리스도상":"Christ the Redeemer (statue)","브리가데이루":"Brigadeiro","삼바":"Samba",
"캥거루":"Kangaroo","오페라하우스":"Sydney Opera House","코알라":"Koala",
"판다":"Giant panda","만두":"Jiaozi","만리장성":"Great Wall of China",
"단풍잎":"Maple leaf","메이플시럽":"Maple syrup","아이스하키":"Ice hockey",
"자유의 여신상":"Statue of Liberty","햄버거":"Hamburger","흰머리수리":"Bald eagle",
"빨간 이층버스":"Double-decker bus","근위병":"King's Guard","빅벤":"Big Ben",
"프레첼":"Pretzel","노이슈반슈타인성":"Neuschwanstein Castle","자동차":"Car",
"피자":"Pizza","파스타":"Pasta","콜로세움":"Colosseum"
}
out=Path("treasures");out.mkdir(exist_ok=True)
headers={"User-Agent":"WorldCatchGameEducational/1.0 (GitHub jeonsein98/world-catch-game)","Accept":"application/json,image/*"}
sources=["# Treasure photograph sources","","Wikipedia article lead images are used as illustrative photos. Verify each image's individual license and author attribution at the linked source before wider redistribution.",""]
missing=[]
for label,title in ITEMS.items():
 path=out/(label+".jpg")
 url="https://en.wikipedia.org/api/rest_v1/page/summary/"+urllib.parse.quote(title.replace(" ","_"))
 try:
  if path.exists():continue
  req=urllib.request.Request(url,headers=headers)
  with urllib.request.urlopen(req,timeout=20) as r:obj=json.load(r)
  photo=obj.get("thumbnail",{}).get("source")
  if not photo:raise ValueError("No thumbnail")
  with urllib.request.urlopen(urllib.request.Request(photo,headers=headers),timeout=25) as r:raw=r.read(6000000)
  im=Image.open(BytesIO(raw)).convert("RGB")
  im=ImageOps.fit(im,(420,320),method=Image.Resampling.LANCZOS)
  im.save(path,"JPEG",quality=80,optimize=True)
  sources.extend([f"- {label}: {obj.get('content_urls',{}).get('desktop',{}).get('page',url)} — photo: {photo}"])
  print("Saved",label,flush=True)
 except Exception as e:
  missing.append(label)
  print("Missing",label,str(e),flush=True)
 time.sleep(.5)
(out/"SOURCES.md").write_text("\n".join(sources)+"\n",encoding="utf-8")
(out/"MISSING.txt").write_text("\n".join(missing) if missing else "All treasure photos saved.",encoding="utf-8")
print("Treasure photo results:",len(ITEMS)-len(missing),"of",len(ITEMS),flush=True)
