import io, os, urllib.request

from PIL import Image, ImageFilter, ImageEnhance

JOBS = [
    {
        "slug": "english-ordering",
        "icon_src": "https://aka.doubaocdn.com/s/Jsq8XsBpfT",
        "cover_src": "https://aka.doubaocdn.com/s/zdzCFGVDWX",
    },
]

ICON_DIR = "icons"
COVER_DIR = "covers"
CW, CH = 1500, 600
IC = 256


def load(src):
    if os.path.exists(src):
        return Image.open(src).convert("RGB")
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=90).read()
    return Image.open(io.BytesIO(data)).convert("RGB")


def make_icon(src, slug):
    im = load(src)
    w, h = im.size
    side = min(w, h)
    x0 = (w - side) // 2
    y0 = (h - side) // 2
    icon = im.crop((x0, y0, x0 + side, y0 + side)).resize((IC, IC), Image.LANCZOS)
    icon.save(os.path.join(ICON_DIR, slug + ".png"))
    print("icon", slug, im.size, "->", icon.size)


def make_cover(src, slug):
    im = load(src)
    w, h = im.size
    target = CW / CH
    if w / h > target:
        nw = int(h * target)
        x0 = (w - nw) // 2
        im = im.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / target)
        y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh))
    im = im.resize((CW, CH), Image.LANCZOS)
    im.save(os.path.join(COVER_DIR, slug + ".png"))
    print("cover", slug, (w, h), "->", im.size)


def main():
    os.makedirs(ICON_DIR, exist_ok=True)
    os.makedirs(COVER_DIR, exist_ok=True)
    for job in JOBS:
        make_icon(job["icon_src"], job["slug"])
        make_cover(job["cover_src"], job["slug"])


if __name__ == "__main__":
    main()
