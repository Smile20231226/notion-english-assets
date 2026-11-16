import json, os, subprocess, sys, urllib.request

OUT = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(OUT, "icons")
COVER_DIR = os.path.join(OUT, "covers")
os.makedirs(ICON_DIR, exist_ok=True)
os.makedirs(COVER_DIR, exist_ok=True)

W, H = 1500, 600
IW, IH = 256, 256


def curl(url):
    try:
        out = subprocess.run(["curl", "-s", "-m", "25", url], capture_output=True, timeout=40).stdout
        return out.decode("utf-8", "replace")
    except Exception:
        return ""

def fetch_iconify(name):
    body = curl("https://api.iconify.design/%s.svg" % name.replace(":", "/"))
    return body if body.startswith("<svg") else None


def search_iconify(q):
    import urllib.parse

    url = "https://api.iconify.design/search?query=%s&limit=12" % urllib.parse.quote(q)
    body = curl(url)
    try:
        d = json.loads(body)
    except Exception:
        return None
    icons = d.get("icons", [])
    pref = [i for i in icons if i.startswith("fluent-emoji-flat/")] or icons
    return pref[0] if pref else None


def split_svg(svg):
    """return (viewBox_string_as_tuple, inner_markup)"""
    i = svg.find(">")
    head = svg[:i]
    inner = svg[i + 1 : svg.rfind("</svg>")]
    import re

    m = re.search(r'viewBox="([^"]+)"', head)
    vb = [float(x) for x in m.group(1).split()] if m else [0, 0, 24, 24]
    return vb, inner


def motif_g(cx, cy, size, vb, inner, op=1.0):
    s = size / float(vb[2])
    tx = cx - size / 2 - vb[0] * s
    ty = cy - size / 2 - vb[1] * s
    return '<g transform="translate(%.2f,%.2f) scale(%.4f)" opacity="%.2f">%s</g>' % (
        tx,
        ty,
        s,
        op,
        inner,
    )


def base_defs(pal, ident="g"):
    return (
        '<defs><linearGradient id="%s" x1="0" y1="0" x2="%d" y2="%d" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="%s"/><stop offset=".58" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
        '</linearGradient><radialGradient id="spot" cx=".5" cy=".5" r=".5">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity=".22"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        "</radialGradient></defs>"
    ) % (ident, W, H, pal[0], pal[1], pal[2])


def cover_cinema(pal, mv):
    bars = (
        '<rect x="0" y="0" width="%d" height="64" fill="#05070a" opacity=".62"/>'
        '<rect x="0" y="%d" width="%d" height="64" fill="#05070a" opacity=".62"/>'
    ) % (W, H - 64, W)
    spot = '<ellipse cx="1055" cy="300" rx="430" ry="270" fill="url(#spot)"/>'
    line = '<path d="M120 300h250" stroke="#ffffff" stroke-opacity=".35" stroke-width="3" stroke-linecap="round"/>'
    dots = '<circle cx="392" cy="300" r="7" fill="#ffffff" fill-opacity=".5"/><circle cx="470" cy="300" r="4" fill="#ffffff" fill-opacity=".35"/>'
    return (
        base_defs(pal)
        + '<rect width="%d" height="%d" fill="url(#g)"/>' % (W, H)
        + spot
        + bars
        + line
        + dots
        + motif_g(1055, 300, 300, mv[0], mv[1])
        + '<rect x="0" y="0" width="%d" height="%d" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="2"/>'
        % (W, H)
    )


def cover_news(pal, mv):
    rules = "".join(
        '<line x1="0" y1="%d" x2="%d" y2="%d" stroke="#ffffff" stroke-opacity=".07" stroke-width="1.5"/>'
        % (y, W, y)
        for y in range(40, H, 58)
    )
    bar = (
        '<rect x="0" y="0" width="14" height="%d" fill="#ffffff" fill-opacity=".55"/>'
        % H
    )
    grid = "".join(
        '<line x1="%d" y1="0" x2="%d" y2="%d" stroke="#ffffff" stroke-opacity=".05" stroke-width="1.5"/>'
        % (x, x, H)
        for x in range(0, W, 150)
    )
    return (
        base_defs(pal)
        + '<rect width="%d" height="%d" fill="url(#g)"/>' % (W, H)
        + grid
        + rules
        + bar
        + '<rect x="1120" y="150" width="300" height="300" fill="#ffffff" fill-opacity=".06" rx="26"/>'
        + motif_g(1160, 300, 240, mv[0], mv[1])
        + '<rect x="120" y="252" width="180" height="96" fill="none" stroke="#ffffff" stroke-opacity=".3" stroke-width="2"/>'
        + '<rect x="120" y="252" width="60" height="96" fill="#ffffff" fill-opacity=".22"/>'
    )


def cover_pop(pal, mv):
    band = '<polygon points="900,0 1500,0 1500,600 640,600" fill="#ffffff" fill-opacity=".07"/>'
    ring = '<circle cx="1090" cy="300" r="235" fill="none" stroke="#ffffff" stroke-opacity=".22" stroke-width="3"/>'
    ring2 = '<circle cx="1090" cy="300" r="300" fill="none" stroke="#ffffff" stroke-opacity=".1" stroke-width="2"/>'
    dots = "".join(
        '<circle cx="%d" cy="%d" r="%d" fill="#ffffff" fill-opacity="%.2f"/>' % v
        for v in [
            (320, 140, 13, 0.5),
            (250, 430, 9, 0.4),
            (520, 470, 7, 0.32),
            (600, 120, 6, 0.28),
        ]
    )
    return (
        base_defs(pal)
        + '<rect width="%d" height="%d" fill="url(#g)"/>' % (W, H)
        + band
        + ring2
        + ring
        + dots
        + motif_g(1090, 300, 300, mv[0], mv[1])
        + '<path d="M120 500h340" stroke="#ffffff" stroke-opacity=".45" stroke-width="4" stroke-linecap="round"/>'
    )


def cover_wave(pal, mv):
    arcs = "".join(
        '<circle cx="140" cy="620" r="%d" fill="none" stroke="#ffffff" stroke-opacity="%.2f" stroke-width="3"/>'
        % (r, 0.12 - i * 0.02)
        for i, r in enumerate([220, 330, 440, 550])
    )
    return (
        base_defs(pal)
        + '<rect width="%d" height="%d" fill="url(#g)"/>' % (W, H)
        + arcs
        + '<circle cx="1080" cy="300" r="255" fill="#ffffff" fill-opacity=".08"/>'
        + motif_g(1080, 300, 290, mv[0], mv[1])
        + '<path d="M120 300h210" stroke="#ffffff" stroke-opacity=".4" stroke-width="4" stroke-linecap="round"/>'
        + '<circle cx="380" cy="300" r="6" fill="#ffffff" fill-opacity=".5"/>'
    )


def cover_paper(pal, mv):
    dots = "".join(
        '<circle cx="%d" cy="%d" r="2.4" fill="#0f172a" fill-opacity=".18"/>' % (x, y)
        for x in range(30, 700, 42)
        for y in range(30, H, 42)
    )
    panel = '<rect x="880" y="0" width="620" height="%d" fill="%s"/>' % (H, pal[1])
    ring = '<circle cx="1110" cy="300" r="200" fill="none" stroke="#ffffff" stroke-opacity=".25" stroke-width="2"/>'
    return (
        base_defs(pal)
        + '<rect width="%d" height="%d" fill="%s"/>' % (W, H, pal[0])
        + dots
        + panel
        + ring
        + motif_g(1110, 300, 260, mv[0], mv[1])
        + '<path d="M120 300h200" stroke="%s" stroke-opacity=".55" stroke-width="5" stroke-linecap="round"/>'
        % pal[2]
        + '<rect x="120" y="255" width="26" height="26" fill="%s" fill-opacity=".85"/>'
        % pal[2]
    )


TPL = {
    "cinema": cover_cinema,
    "news": cover_news,
    "pop": cover_pop,
    "wave": cover_wave,
    "paper": cover_paper,
}


def icon_svg(pal, mv):
    d = (
        '<defs><linearGradient id="ig" x1="0" y1="0" x2="256" y2="256" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient></defs>'
    ) % (pal[1], pal[2])
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">'
        + d
        + '<rect width="256" height="256" rx="58" fill="url(#ig)"/>'
        '<circle cx="128" cy="128" r="86" fill="#ffffff" fill-opacity=".10"/>'
        + motif_g(128, 128, 132, mv[0], mv[1])
        + "</svg>"
    )


# slug, page_id, template, palette, motif, generate flags
PAGES = [
    (
        "iphone-fold",
        "3dfabdd7-e4df-81b5-8fa4-f121e1a26842",
        "pop",
        ["#141428", "#3d3a8f", "#00d1ff"],
        "fluent-emoji-flat/mobile-phone",
        1,
        1,
    ),
    (
        "stock-gap",
        "3deabdd7-e4df-8063-ae27-e2cbcded9b6d",
        "wave",
        ["#08160f", "#12664f", "#e63946"],
        "fluent-emoji-flat/chart-increasing",
        1,
        1,
    ),
    (
        "changsha-charger",
        "3ebabdd7-e4df-81a2-ac7f-e6b4cabc5905",
        "pop",
        ["#0f2027", "#1c6e5c", "#a8e05f"],
        "fluent-emoji-flat/electric-plug",
        1,
        1,
    ),
    (
        "scattered-points",
        "3f1abdd7-e4df-8122-9a0e-f672f76329cb",
        "wave",
        ["#221856", "#4a35c9", "#9a77ff"],
        "mdi/star-four-points",
        1,
        1,
    ),
    (
        "polish-speaking",
        "3efabdd7-e4df-819b-80a4-efb1ef6594a5",
        "wave",
        ["#2b1a12", "#8a4b22", "#f2b134"],
        "fluent-emoji-flat/speech-balloon",
        1,
        1,
    ),
    (
        "the-office",
        "406abdd7-e4df-8183-a4e5-d97f820c6822",
        "cinema",
        ["#0d1319", "#2c3e50", "#8794a3"],
        "fluent-emoji-flat/clapper-board",
        1,
        1,
    ),
    (
        "china-shopping",
        "406abdd7-e4df-81fd-a7b0-f70c213d5857",
        "pop",
        ["#2b0b3f", "#c2185b", "#ff8a65"],
        "fluent-emoji-flat/shopping-bags",
        1,
        1,
    ),
    (
        "homeland",
        "408abdd7-e4df-8145-b37d-c44cb082373d",
        "cinema",
        ["#12060a", "#5a0f14", "#d7263d"],
        "fluent-emoji-flat/movie-camera",
        0,
        0,
    ),
    (
        "suits",
        "3e1abdd7-e4df-8114-a8a9-e67b36a42660",
        "cinema",
        ["#101215", "#3a3f47", "#c9a227"],
        "fluent-emoji-flat/balance-scale",
        1,
        1,
    ),
    (
        "bbc-listening",
        "3e1abdd7-e4df-81ed-bc85-cc0b2955210b",
        "news",
        ["#0a1420", "#123a5e", "#2d9cdb"],
        "fluent-emoji-flat/headphone",
        1,
        1,
    ),
    (
        "bbc-news",
        "3e1abdd7-e4df-81ba-98c6-ccb15a5eafbb",
        "news",
        ["#0b1220", "#1b3b6f", "#4f9dff"],
        "fluent-emoji-flat/newspaper",
        1,
        1,
    ),
    (
        "obama-health",
        "3e2abdd7-e4df-819c-b19a-c52d46e717dc",
        "news",
        ["#0d1524", "#243b6b", "#c0392b"],
        "fluent-emoji-flat/microphone",
        1,
        1,
    ),
    (
        "china-haul",
        "402abdd7-e4df-8191-8246-fc19902dcc2f",
        "pop",
        ["#241033", "#d81b60", "#ffa726"],
        "fluent-emoji-flat/shopping-cart",
        1,
        1,
    ),
    (
        "climate",
        "407abdd7-e4df-815d-b17e-f812b2908472",
        "wave",
        ["#08222a", "#0f6b6b", "#7ed957"],
        "fluent-emoji-flat/globe-showing-americas",
        1,
        1,
    ),
    (
        "coffee",
        "3e0abdd7-e4df-8114-a006-c80f6e920d4a",
        "wave",
        ["#241008", "#7b3f1d", "#f6bd60"],
        "fluent-emoji-flat/hot-beverage",
        1,
        1,
    ),
    (
        "esports",
        "3f4abdd7-e4df-81bc-b1bd-e7c17e2cb97d",
        "pop",
        ["#12002b", "#7b2ff7", "#00e5ff"],
        "fluent-emoji-flat/video-game",
        1,
        1,
    ),
    (
        "ted-ed-story",
        "3f8abdd7-e4df-81f6-b902-e3c8f9aa4821",
        "wave",
        ["#2a0505", "#a4161a", "#ff8fa3"],
        "fluent-emoji-flat/speech-balloon",
        1,
        1,
    ),
    (
        "jungle-gremlins",
        "3e9abdd7-e4df-8197-8491-ca9e4b848e05",
        "cinema",
        ["#07130c", "#1f5132", "#a3d977"],
        "fluent-emoji-flat/monkey-face",
        1,
        1,
    ),
    (
        "yellowstone",
        "3ecabdd7-e4df-812d-a041-ea696ce36044",
        "cinema",
        ["#1a0f05", "#7a4a12", "#f0a202"],
        "fluent-emoji-flat/horse",
        1,
        1,
    ),
    (
        "mind-switch",
        "3f4abdd7-e4df-8197-8b7b-cde3e6b20d15",
        "paper",
        ["#f6f3ea", "#1f2430", "#7b5cff"],
        "fluent-emoji-flat/brain",
        1,
        1,
    ),
    (
        "training-methods",
        "40aabdd7-e4df-8112-a571-ec93da4a6081",
        "paper",
        ["#f6f3ea", "#243447", "#00a896"],
        "fluent-emoji-flat/spiral-notepad",
        1,
        1,
    ),
    (
        "translation-system",
        "40aabdd7-e4df-8129-82ff-ee0acf6fb2c5",
        "paper",
        ["#f6f3ea", "#2d2a4a", "#f25f5c"],
        "fluent-emoji-flat/counterclockwise-arrows-button",
        1,
        1,
    ),
    (
        "thinking-pits",
        "40aabdd7-e4df-81d3-a820-d51c0338c1b8",
        "paper",
        ["#f6f3ea", "#33272a", "#e07a5f"],
        "fluent-emoji-flat/hole",
        1,
        1,
    ),
    (
        "skills-inventory",
        "40aabdd7-e4df-8189-8d99-f1a57dbe2242",
        "paper",
        ["#f6f3ea", "#1d3557", "#457b9d"],
        "fluent-emoji-flat/abacus",
        1,
        1,
    ),
    (
        "camera-shot",
        "40aabdd7-e4df-8155-957f-dfee9b7dc563",
        "paper",
        ["#f6f3ea", "#2b2d42", "#ef8354"],
        "fluent-emoji-flat/movie-camera",
        1,
        1,
    ),
    (
        "matching-rules",
        "40aabdd7-e4df-812a-8daf-fb238b930333",
        "paper",
        ["#f6f3ea", "#3d315b", "#6c5ce7"],
        "fluent-emoji-flat/link",
        1,
        1,
    ),
    (
        "practice-actions",
        "40aabdd7-e4df-81f1-86dc-caae5936d8dd",
        "paper",
        ["#f6f3ea", "#2f3b52", "#f4a261"],
        "fluent-emoji-flat/hammer-and-wrench",
        1,
        1,
    ),
    (
        "persona",
        "407abdd7-e4df-8126-a2a6-f327bfa0d5ea",
        "paper",
        ["#f6f3ea", "#1b1b1f", "#c9a227"],
        "fluent-emoji-flat/bust-in-silhouette",
        1,
        1,
    ),
    (
        "marvel-cut",
        "3f2abdd7-e4df-81b1-bf0d-d78e45aac003",
        "cinema",
        ["#150306", "#8b0f16", "#ff4d4d"],
        "fluent-emoji-flat/superhero",
        1,
        1,
    ),
    (
        "business-english",
        "419abdd7-e4df-81cf-bbd6-eb641791ad42",
        "news",
        ["#0c1a24", "#1d3b53", "#4ea8de"],
        "fluent-emoji-flat/briefcase",
        1,
        1,
    ),
    (
        "tsmc-acquired",
        "407abdd7-e4df-8109-8ff2-f09d754f1911",
        "news",
        ["#0a0f1a", "#2b3a55", "#b8c6db"],
        "fluent-emoji-flat/microchip",
        1,
        1,
    ),
    (
        "helmet",
        "40cabdd7-e4df-8124-b940-e4574048202d",
        "pop",
        ["#1a1207", "#b45309", "#fbbf24"],
        "fluent-emoji-flat/rescue-worker-s-helmet",
        0,
        1,
    ),
    (
        "pliers",
        "40cabdd7-e4df-810d-a62d-e82c085d737f",
        "pop",
        ["#14171c", "#3f4a5a", "#9aa5b1"],
        "fluent-emoji-flat/wrench",
        0,
        1,
    ),
    (
        "golf",
        "40dabdd7-e4df-8163-bd4b-cb439c9b71fd",
        "pop",
        ["#0b2417", "#2f7d4f", "#c9f299"],
        "fluent-emoji-flat/person-golfing",
        0,
        1,
    ),
    (
        "udon",
        "40dabdd7-e4df-815c-bf3f-d75f30749650",
        "pop",
        ["#241506", "#a45a1f", "#ffcf6b"],
        "fluent-emoji-flat/steaming-bowl",
        0,
        1,
    ),
    (
        "barnacle",
        "417abdd7-e4df-8140-9669-f15ba4f63f0b",
        "pop",
        ["#1b1a05", "#b59f00", "#ffe066"],
        "fluent-emoji-flat/automobile",
        0,
        1,
    ),
    (
        "focus",
        "3e0abdd7-e4df-8113-9f77-caf12a1dff4e",
        "paper",
        ["#f6f3ea", "#1c2541", "#3a86ff"],
        "fluent-emoji-flat/bullseye",
        1,
        1,
    ),
    (
        "workplace-blame",
        "419abdd7-e4df-81fc-bffa-f040c4f75c5f",
        "news",
        ["#101317", "#333d47", "#e07a5f"],
        "fluent-emoji-flat/backhand-index-pointing-right",
        1,
        1,
    ),
]

manifest = []
for slug, pid, tpl, pal, motif, do_cover, do_icon in PAGES:
    svg = fetch_iconify(motif)
    used = motif
    if not svg:
        alt = search_iconify(motif.split("/")[-1].replace("-", " "))
        if alt:
            svg = fetch_iconify(alt)
            used = alt
    if not svg:
        print("MISSING MOTIF", slug, motif)
        continue
    vb, inner = split_svg(svg)
    if do_cover:
        c = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="600" viewBox="0 0 1500 600">'
            + TPL[tpl](pal, (vb, inner))
            + "</svg>"
        )
        open(os.path.join(COVER_DIR, slug + ".svg"), "w", encoding="utf-8").write(c)
    if do_icon:
        open(os.path.join(ICON_DIR, slug + ".svg"), "w", encoding="utf-8").write(
            icon_svg(pal, (vb, inner))
        )
    manifest.append(
        {
            "slug": slug,
            "page_id": pid,
            "cover": bool(do_cover),
            "icon": bool(do_icon),
            "motif": used,
        }
    )

json.dump(
    manifest,
    open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=1,
)
print(
    "pages:",
    len(manifest),
    "icons:",
    len(os.listdir(ICON_DIR)),
    "covers:",
    len(os.listdir(COVER_DIR)),
)
for m in manifest:
    if m["motif"].split("/")[-1].replace("-", " ") in ("",):
        print("fallback", m["slug"], m["motif"])
