import io, os, urllib.request

from PIL import Image, ImageEnhance, ImageFilter

SRC = "http://bkimg.cdn.bcebos.com/pic/4bed2e738bd4b31c87016cc9ab98307f9e2f07085238"
SLUG = "silicon-valley-s01e01"
ICON_DIR = "icons"
COVER_DIR = "covers"
CW, CH = 1500, 600
IC = 256


def load(src):
    if os.path.exists(src):
        return Image.open(src).convert("RGB")
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
    return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=90).read())).convert("RGB")


def main():
    im = load(SRC)
    w, h = im.size
    os.makedirs(ICON_DIR, exist_ok=True)
    os.makedirs(COVER_DIR, exist_ok=True)

    side = int(w * 0.62)
    x0 = (w - side) // 2
    y0 = int(h * 0.13)
    icon = im.crop((x0, y0, x0 + side, y0 + side)).resize((IC, IC), Image.LANCZOS)
    icon.save(os.path.join(ICON_DIR, SLUG + ".png"))

    bg = im.resize((CW, int(CW * h / w)), Image.LANCZOS)
    top = max(0, (bg.height - CH) // 2)
    bg = bg.crop((0, top, CW, top + CH)).filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)

    fh = CH
    fw = int(fh * w / h)
    fg = im.resize((fw, fh), Image.LANCZOS)
    bg.paste(fg, ((CW - fw) // 2, 0))
    bg.save(os.path.join(COVER_DIR, SLUG + ".png"))
    print("source", im.size, "cover", bg.size, "icon", icon.size)


if __name__ == "__main__":
    main()
