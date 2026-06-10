#!/usr/bin/env python3
"""Generate brand logo and Hachiyo-style menu SVG assets."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRANDS_DIR = ROOT / "assets" / "brands"
MENUS_DIR = ROOT / "assets" / "menus"

FONT = "'PingFang TC','Noto Sans TC','Microsoft JhengHei',sans-serif"

BRANDS = [
    {
        "slug": "50lan",
        "label": "五十嵐",
        "bg": "#F5D547",
        "fg": "#1B5E20",
        "accent": "#1B5E20",
        "featured": ["波霸奶茶", "四季春青茶", "8冰綠"],
        "categories": [
            ("純茶系列", [("四季春青茶", 25, 30), ("茉莉綠茶", 25, 30), ("阿薩姆紅茶", 25, 30), ("黃金烏龍", 30, 35)]),
            ("調味茶", [("8冰綠", 30, 35), ("檸檬綠", 30, 35), ("梅綠", 30, 35), ("蜂蜜綠茶", 35, 40)]),
            ("奶茶系列", [("波霸奶茶", 40, 50), ("燕麥奶茶", 45, 55), ("布丁奶茶", 45, 55), ("椰果奶茶", 40, 50)]),
        ],
    },
    {
        "slug": "chingshin",
        "label": "清心福全",
        "bg": "#00A651",
        "fg": "#FFFFFF",
        "accent": "#007A3D",
        "featured": ["烏龍奶茶", "冬瓜檸檬", "仙草凍奶"],
        "categories": [
            ("招牌奶茶", [("烏龍奶茶", 35, 45), ("珍珠奶茶", 35, 45), ("仙草凍奶", 40, 50), ("布丁奶茶", 40, 50)]),
            ("清新茶飲", [("檸檬青茶", 30, 35), ("冬瓜檸檬", 30, 35), ("蜂蜜綠茶", 35, 40), ("梅綠", 30, 35)]),
            ("特調系列", [("多多綠", 40, 45), ("鮮柚綠", 45, 50), ("金桔檸檬", 40, 45), ("百香綠", 40, 45)]),
        ],
    },
    {
        "slug": "coco",
        "label": "CoCo都可",
        "bg": "#F47920",
        "fg": "#FFFFFF",
        "accent": "#D45F00",
        "featured": ["奶茶三兄弟", "百香雙響炮", "珍珠奶茶"],
        "categories": [
            ("人氣奶茶", [("珍珠奶茶", 40, 50), ("奶茶三兄弟", 50, 60), ("鮮芋青稞牛奶", 55, 65), ("巧克力奶茶", 45, 55)]),
            ("果茶系列", [("百香雙響炮", 50, 60), ("檸檬霸", 45, 55), ("葡萄柚綠", 45, 55), ("芒果綠茶", 50, 60)]),
            ("純茶系列", [("四季春青茶", 25, 30), ("黃金烏龍", 30, 35), ("阿薩姆紅茶", 25, 30), ("茉莉綠茶", 25, 30)]),
        ],
    },
    {
        "slug": "milksha",
        "label": "迷客夏",
        "bg": "#C4A574",
        "fg": "#3E2723",
        "accent": "#6D4C2C",
        "featured": ["大正紅茶拿鐵", "珍珠鮮奶", "烤布丁鮮奶"],
        "categories": [
            ("鮮奶系列", [("珍珠鮮奶", 55, 65), ("烤布丁鮮奶", 60, 70), ("大正紅茶拿鐵", 55, 65), ("燕麥奶茶", 55, 65)]),
            ("純茶系列", [("大正紅茶", 30, 35), ("文山包種", 30, 35), ("黃金烏龍", 35, 40), ("翡翠綠茶", 30, 35)]),
            ("特調飲品", [("檸檬汁", 45, 55), ("鮮榨柳橙汁", 55, 65), ("蜂蜜檸檬", 45, 55), ("仙草凍奶", 50, 60)]),
        ],
    },
    {
        "slug": "kebuke",
        "label": "可不可",
        "bg": "#C8102E",
        "fg": "#FFFFFF",
        "accent": "#8B0000",
        "featured": ["熟成紅茶", "白玉歐蕾", "胭脂紅茶"],
        "categories": [
            ("熟成紅茶", [("熟成紅茶", 30, 35), ("胭脂紅茶", 35, 40), ("熟成青茶", 30, 35), ("春梅冰茶", 40, 45)]),
            ("奶茶歐蕾", [("白玉歐蕾", 50, 60), ("珍珠奶茶", 45, 55), ("布丁奶茶", 50, 60), ("燕麥奶茶", 50, 60)]),
            ("特調系列", [("檸檬紅茶", 40, 45), ("多多紅茶", 45, 50), ("蜂蜜檸檬", 45, 50), ("鮮奶熟成", 50, 60)]),
        ],
    },
    {
        "slug": "tptea",
        "label": "茶湯會",
        "bg": "#5D4037",
        "fg": "#FFFFFF",
        "accent": "#3E2723",
        "featured": ["鐵觀音奶茶", "翡翠檸檬", "阿薩姆奶茶"],
        "categories": [
            ("經典奶茶", [("鐵觀音奶茶", 40, 50), ("阿薩姆奶茶", 40, 50), ("珍珠奶茶", 40, 50), ("布丁奶茶", 45, 55)]),
            ("純茶系列", [("鐵觀音", 25, 30), ("阿薩姆", 25, 30), ("茉莉綠茶", 25, 30), ("黃金烏龍", 30, 35)]),
            ("果茶特調", [("翡翠檸檬", 40, 45), ("冬瓜檸檬", 35, 40), ("梅綠", 35, 40), ("蜂蜜綠茶", 40, 45)]),
        ],
    },
    {
        "slug": "dayung",
        "label": "大苑子",
        "bg": "#2E7D32",
        "fg": "#FFFFFF",
        "accent": "#1B5E20",
        "featured": ["翡翠檸檬", "葡萄柚綠", "鮮榨柳橙汁"],
        "categories": [
            ("鮮果系列", [("翡翠檸檬", 45, 55), ("葡萄柚綠", 50, 60), ("鮮榨柳橙汁", 55, 65), ("百香綠茶", 50, 60)]),
            ("奶茶系列", [("珍珠奶茶", 40, 50), ("布丁奶茶", 45, 55), ("燕麥奶茶", 45, 55), ("椰果奶茶", 40, 50)]),
            ("純茶系列", [("四季春青茶", 25, 30), ("黃金烏龍", 30, 35), ("茉莉綠茶", 25, 30), ("阿薩姆紅茶", 25, 30)]),
        ],
    },
    {
        "slug": "yifang",
        "label": "一芳",
        "bg": "#F9A825",
        "fg": "#5D4037",
        "accent": "#E65100",
        "featured": ["水果茶", "粉粿青茶", "檸檬綠"],
        "categories": [
            ("水果茶", [("水果茶", 55, 65), ("葡萄柚綠", 50, 60), ("檸檬綠", 40, 45), ("百香綠茶", 50, 60)]),
            ("奶茶系列", [("烏龍奶茶", 40, 50), ("珍珠奶茶", 40, 50), ("粉粿青茶", 45, 55), ("布丁奶茶", 45, 55)]),
            ("純茶系列", [("粉粿青茶", 35, 40), ("冬瓜檸檬", 35, 40), ("四季春青茶", 25, 30), ("黃金烏龍", 30, 35)]),
        ],
    },
    {
        "slug": "starbucks",
        "label": "星巴克",
        "bg": "#00704A",
        "fg": "#FFFFFF",
        "accent": "#004D33",
        "featured": ["那提", "美式咖啡", "星冰樂"],
        "categories": [
            ("咖啡", [("美式咖啡", 95, 110), ("那提", 110, 125), ("焦糖瑪奇朵", 125, 140), ("冷萃咖啡", 120, 135)]),
            ("星冰樂", [("抹茶星冰樂", 140, 155), ("可可星冰樂", 140, 155), ("焦糖星冰樂", 140, 155), ("芒果星冰樂", 145, 160)]),
            ("茶飲", [("紅茶那提", 110, 125), ("抹茶那提", 125, 140), ("冰搖紅茶", 95, 110), ("冰搖檸茶", 105, 120)]),
        ],
    },
    {
        "slug": "louisa",
        "label": "路易莎",
        "bg": "#1A1A1A",
        "fg": "#D4AF37",
        "accent": "#8B7500",
        "featured": ["美式咖啡", "拿鐵", "手沖單品"],
        "categories": [
            ("咖啡", [("美式咖啡", 75, 90), ("拿鐵", 90, 105), ("卡布奇諾", 95, 110), ("手沖單品", 120, 140)]),
            ("茶飲", [("紅茶", 60, 75), ("綠茶", 60, 75), ("奶茶", 80, 95), ("檸檬茶", 75, 90)]),
            ("輕食", [("可頌", 55, 65), ("貝果", 65, 75), ("三明治", 85, 95), ("沙拉", 120, 140)]),
        ],
    },
    {
        "slug": "comebuy",
        "label": "COMEBUY",
        "bg": "#1565C0",
        "fg": "#FFFFFF",
        "accent": "#0D47A1",
        "featured": ["玩火奶茶", "百香雙響炮", "珍珠奶茶"],
        "categories": [
            ("奶茶", [("珍珠奶茶", 40, 50), ("玩火奶茶", 50, 60), ("布丁奶茶", 45, 55), ("燕麥奶茶", 45, 55)]),
            ("果茶", [("百香雙響炮", 50, 60), ("檸檬綠", 40, 45), ("葡萄柚綠", 45, 55), ("蜂蜜綠茶", 40, 45)]),
            ("純茶", [("鐵觀音", 25, 30), ("茉莉綠茶", 25, 30), ("黃金烏龍", 30, 35), ("阿薩姆紅茶", 25, 30)]),
        ],
    },
    {
        "slug": "tiger",
        "label": "老虎堂",
        "bg": "#1A1A1A",
        "fg": "#F5A623",
        "accent": "#C47D00",
        "featured": ["黑糖波霸", "黑糖厚鮮奶", "烏龍拿鐵"],
        "categories": [
            ("黑糖系列", [("黑糖波霸", 55, 65), ("黑糖厚鮮奶", 60, 70), ("黑糖珍珠鮮奶", 60, 70), ("黑糖布丁", 60, 70)]),
            ("拿鐵系列", [("烏龍拿鐵", 60, 70), ("抹茶拿鐵", 65, 75), ("紅茶拿鐵", 60, 70), ("燕麥拿鐵", 65, 75)]),
            ("純茶", [("黃金烏龍", 35, 40), ("鐵觀音", 30, 35), ("翡翠綠茶", 30, 35), ("阿薩姆紅茶", 30, 35)]),
        ],
    },
    {
        "slug": "dejeng",
        "label": "得正",
        "bg": "#F0E6D2",
        "fg": "#3D2914",
        "accent": "#6B4423",
        "featured": ["烏龍純茶", "檸檬烏龍", "珍珠烏龍"],
        "categories": [
            ("烏龍茶", [("烏龍純茶", 30, 35), ("檸檬烏龍", 40, 45), ("珍珠烏龍", 45, 55), ("熟成紅茶", 30, 35)]),
            ("奶茶", [("烏龍奶茶", 45, 55), ("燕麥烏龍", 50, 60), ("布丁烏龍", 50, 60), ("鮮奶烏龍", 50, 60)]),
            ("特調", [("蜂蜜烏龍", 40, 45), ("梅烏龍", 40, 45), ("多多烏龍", 45, 50), ("冬瓜烏龍", 40, 45)]),
        ],
    },
    {
        "slug": "wanpo",
        "label": "萬波",
        "bg": "#E91E8C",
        "fg": "#FFFFFF",
        "accent": "#AD1457",
        "featured": ["紅豆粉粿", "芋頭粉粿", "冬瓜檸檬"],
        "categories": [
            ("粉粿系列", [("紅豆粉粿", 45, 55), ("芋頭粉粿", 45, 55), ("綠豆粉粿", 45, 55), ("粉粿奶茶", 50, 60)]),
            ("奶茶", [("烏龍奶茶", 40, 50), ("珍珠奶茶", 40, 50), ("布丁奶茶", 45, 55), ("燕麥奶茶", 45, 55)]),
            ("茶飲", [("冬瓜檸檬", 35, 40), ("四季春青茶", 25, 30), ("檸檬綠", 35, 40), ("梅綠", 35, 40)]),
        ],
    },
    {
        "slug": "zhuzhudan",
        "label": "珍煮丹",
        "bg": "#1A1A1A",
        "fg": "#E53935",
        "accent": "#B71C1C",
        "featured": ["黑糖珍珠", "黑糖鮮奶", "烏龍奶茶"],
        "categories": [
            ("黑糖系列", [("黑糖珍珠", 50, 60), ("黑糖鮮奶", 55, 65), ("黑糖布丁", 55, 65), ("黑糖燕麥", 55, 65)]),
            ("奶茶", [("烏龍奶茶", 45, 55), ("珍珠奶茶", 45, 55), ("燕麥鮮奶", 50, 60), ("布丁奶茶", 50, 60)]),
            ("純茶", [("四季春青茶", 30, 35), ("黃金烏龍", 35, 40), ("翡翠綠茶", 30, 35), ("阿薩姆紅茶", 30, 35)]),
        ],
    },
    {
        "slug": "shangyulin",
        "label": "上宇林",
        "bg": "#2E7D32",
        "fg": "#FFFFFF",
        "accent": "#1B5E20",
        "featured": ["珍珠奶茶", "檸檬綠", "冬瓜茶"],
        "categories": [
            ("奶茶", [("珍珠奶茶", 35, 45), ("布丁奶茶", 40, 50), ("燕麥奶茶", 40, 50), ("椰果奶茶", 35, 45)]),
            ("茶飲", [("檸檬綠", 30, 35), ("冬瓜茶", 25, 30), ("梅綠", 30, 35), ("蜂蜜綠茶", 35, 40)]),
            ("純茶", [("四季春青茶", 25, 30), ("黃金烏龍", 30, 35), ("茉莉綠茶", 25, 30), ("阿薩姆紅茶", 25, 30)]),
        ],
    },
    {
        "slug": "macu",
        "label": "麻古茶坊",
        "bg": "#8B0000",
        "fg": "#FFD700",
        "accent": "#5C0000",
        "featured": ["芝芝葡萄", "楊枝甘露", "珍珠奶茶"],
        "categories": [
            ("芝芝系列", [("芝芝葡萄", 65, 75), ("芝芝芒果", 65, 75), ("芝芝蜜桃", 65, 75), ("芝芝草莓", 65, 75)]),
            ("奶茶", [("珍珠奶茶", 45, 55), ("布丁奶茶", 50, 60), ("燕麥奶茶", 50, 60), ("椰果奶茶", 45, 55)]),
            ("果茶", [("楊枝甘露", 60, 70), ("百香綠茶", 50, 60), ("檸檬汁", 45, 55), ("葡萄柚綠", 50, 60)]),
        ],
    },
]

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="24" fill="{bg}"/>
  <text x="64" y="78" text-anchor="middle" font-size="{size}" font-weight="700" fill="{fg}" font-family="{font}">{label}</text>
</svg>
"""


def logo_size(label: str) -> int:
    if len(label) <= 3:
        return 36
    if len(label) <= 5:
        return 28
    return 22


def info_boxes(x: int, y: int) -> str:
    labels = ["冰", "糖", "卡"]
    parts = []
    for index, label in enumerate(labels):
        bx = x + index * 22
        parts.append(f'<rect x="{bx}" y="{y - 12}" width="18" height="14" fill="#f5f5f5" stroke="#ccc" stroke-width="0.5"/>')
        parts.append(
            f'<text x="{bx + 9}" y="{y - 2}" text-anchor="middle" font-size="7" fill="#666" font-family="{FONT}">{label}</text>'
        )
    return "".join(parts)


def render_menu_item(name: str, m_price: int, l_price: int, x: int, y: int) -> str:
    return (
        f'<text x="{x}" y="{y}" font-size="11" font-weight="600" fill="#1a1a1a" font-family="{FONT}">{name}</text>'
        f'{info_boxes(x + 108, y)}'
        f'<text x="{x + 178}" y="{y}" text-anchor="end" font-size="11" font-weight="700" fill="#1a1a1a">{m_price}</text>'
        f'<text x="{x + 218}" y="{y}" text-anchor="end" font-size="11" font-weight="700" fill="#1a1a1a">{l_price}</text>'
        f'<line x1="{x}" y1="{y + 6}" x2="{x + 218}" y2="{y + 6}" stroke="#ececec" stroke-width="0.8"/>'
    )


def render_category(title: str, items: list[tuple[str, int, int]], col_x: int, start_y: int) -> tuple[str, int]:
    parts = [
        f'<rect x="{col_x - 4}" y="{start_y - 16}" width="230" height="22" fill="#f7f7f7"/>',
        f'<text x="{col_x}" y="{start_y}" font-size="13" font-weight="800" fill="#1a1a1a" font-family="{FONT}">{title}</text>',
        f'<text x="{col_x + 150}" y="{start_y}" font-size="9" fill="#999" font-family="{FONT}">M</text>',
        f'<text x="{col_x + 190}" y="{start_y}" font-size="9" fill="#999" font-family="{FONT}">L</text>',
    ]
    y = start_y + 22
    for name, m_price, l_price in items:
        parts.append(render_menu_item(name, m_price, l_price, col_x, y))
        y += 28
    return "".join(parts), y + 8


def render_hachiyo_menu(brand: dict) -> str:
    label = brand["label"]
    accent = brand["accent"]
    featured = brand["featured"]

    sidebar_items = []
    for index, item in enumerate(featured):
        y = 200 + index * 90
        sidebar_items.append(
            f'<rect x="24" y="{y}" width="120" height="72" rx="6" fill="#fafafa" stroke="#e0e0e0"/>'
            f'<circle cx="84" cy="{y + 28}" r="18" fill="{accent}" opacity="0.15"/>'
            f'<text x="84" y="{y + 33}" text-anchor="middle" font-size="16" fill="{accent}">🍵</text>'
            f'<text x="84" y="{y + 60}" text-anchor="middle" font-size="10" font-weight="700" fill="#333" font-family="{FONT}">{item}</text>'
        )

    columns = []
    col_x_positions = [170, 420, 670]
    col_y_starts = [120, 120, 120]

    for col_index, category in enumerate(brand["categories"]):
        if col_index >= len(col_x_positions):
            break
        html, next_y = render_category(category[0], category[1], col_x_positions[col_index], col_y_starts[col_index])
        columns.append(html)
        col_y_starts[col_index] = next_y

    sugar_legend = (
        f'<text x="170" y="1080" font-size="11" font-weight="700" fill="#333" font-family="{FONT}">甜度</text>'
        + "".join(
            f'<rect x="{220 + i * 52}" y="1068" width="44" height="18" fill="{"#333" if i == 2 else "#f5f5f5"}" stroke="#ccc"/>'
            f'<text x="{242 + i * 52}" y="1081" text-anchor="middle" font-size="8" fill="{"#fff" if i == 2 else "#666"}" font-family="{FONT}">{level}</text>'
            for i, level in enumerate(["0%", "30%", "50%", "70%", "全糖"])
        )
        + f'<text x="170" y="1110" font-size="11" font-weight="700" fill="#333" font-family="{FONT}">冰量</text>'
        + "".join(
            f'<rect x="{220 + i * 52}" y="1098" width="44" height="18" fill="{"#333" if i == 2 else "#f5f5f5"}" stroke="#ccc"/>'
            f'<text x="{242 + i * 52}" y="1111" text-anchor="middle" font-size="8" fill="{"#fff" if i == 2 else "#666"}" font-family="{FONT}">{level}</text>'
            for i, level in enumerate(["去冰", "微冰", "少冰", "正常", "溫熱"])
        )
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 1140">
  <rect width="920" height="1140" fill="#ffffff"/>
  <rect x="0" y="0" width="920" height="72" fill="#ffffff" stroke="#e8e8e8"/>
  <text x="36" y="48" font-size="28" font-weight="800" fill="{accent}" font-family="{FONT}">{label}</text>
  <text x="884" y="48" text-anchor="end" font-size="11" fill="#999" font-family="{FONT}">價格僅供參考 · 以門市為準</text>
  <line x1="0" y1="72" x2="920" y2="72" stroke="#e0e0e0" stroke-width="1.5"/>
  <rect x="0" y="72" width="160" height="1068" fill="#fafafa"/>
  <text x="84" y="110" text-anchor="middle" font-size="12" font-weight="800" fill="{accent}" font-family="{FONT}" transform="rotate(-90 84 110)">人氣必點</text>
  {"".join(sidebar_items)}
  {"".join(columns)}
  <rect x="160" y="1040" width="760" height="100" fill="#fafafa" stroke="#ececec"/>
  {sugar_legend}
  <text x="460" y="1125" text-anchor="middle" font-size="9" fill="#bbb" font-family="{FONT}">找茶？ 菜單示意圖 · 非官方文件</text>
</svg>"""


def main() -> None:
    BRANDS_DIR.mkdir(parents=True, exist_ok=True)
    MENUS_DIR.mkdir(parents=True, exist_ok=True)

    for brand in BRANDS:
        slug = brand["slug"]
        label = brand["label"]
        logo_path = BRANDS_DIR / f"{slug}.svg"
        logo_path.write_text(
            LOGO_SVG.format(
                bg=brand["bg"],
                fg=brand["fg"],
                label=label,
                size=logo_size(label),
                font=FONT,
            ),
            encoding="utf-8",
        )

        menu_path = MENUS_DIR / f"{slug}.svg"
        menu_path.write_text(render_hachiyo_menu(brand), encoding="utf-8")

    print(f"Generated {len(BRANDS)} brand logos and menus.")


if __name__ == "__main__":
    main()
