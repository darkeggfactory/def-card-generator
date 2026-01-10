import random
import re
import math
from pathlib import Path
from PIL import Image, ImageFilter

# --- Beállítások ---
CANVAS_SIZE = 500  # Vászon mérete (szélesség = magasság)
BLEED = int(CANVAS_SIZE * 0.05)  # 5% bleed
SCRIPT_DIR = Path(__file__).parent
FULLDECK_DIR = SCRIPT_DIR / "fulldeck"
OUTPUT = SCRIPT_DIR / "showcase.png"
SEED = None  # pl. 42 ha mindig ugyanazt szeretnéd

# --- Automatikus méretezés ---
INNER_SIZE = CANVAS_SIZE - (2 * BLEED)
CARD_TARGET_HEIGHT = int(INNER_SIZE * 0.4)  # kb. a belső terület 24%-a
CENTER_RADIUS = int(INNER_SIZE * 0.33)       # félkör sugár
SHADOW_OFFSET = (int(CANVAS_SIZE * 0.004), int(CANVAS_SIZE * 0.004))
SHADOW_BLUR = int(CANVAS_SIZE * 0.006)

# --- Segédfüggvények ---
def parse_rank(fname: str):
    n = fname.lower()
    if n.startswith("card_back"):
        return "back"
    if n.startswith("joker"):
        return "joker"
    m = re.match(r"^(clubs|diamonds|hearts|spades)_(a|k|q|j|10|[2-9])\.png$", n)
    if m:
        return m.group(2).upper()
    return None

def load_and_scale(p: Path, target_h: int):
    img = Image.open(p).convert("RGBA")
    w, h = img.size
    scale = target_h / h
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img

def add_shadow(img, offset=SHADOW_OFFSET, blur_radius=SHADOW_BLUR, shadow_color=(0, 0, 0, 100)):
    """Létrehoz egy elmosott árnyékot az alfa alapján."""
    shadow = Image.new('RGBA', (img.width + abs(offset[0]), img.height + abs(offset[1])), (0, 0, 0, 0))
    alpha = img.split()[3]
    shadow_layer = Image.new('RGBA', img.size, shadow_color)
    shadow.paste(shadow_layer, (0, 0), mask=alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    base = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
    base.alpha_composite(shadow, (max(offset[0], 0), max(offset[1], 0)))
    return base

# --- Főprogram ---
def main():
    if SEED is not None:
        random.seed(SEED)

    # hátlap
    back_card = SCRIPT_DIR / "card_back.png"
    if not back_card.exists():
        raise FileNotFoundError("Nincs card_back.png a script mappájában!")

    # előlapok betöltése
    files = sorted(p for p in FULLDECK_DIR.glob("*.png"))
    named_ranks = {"A", "K", "Q", "J", "joker"}
    named_pool = [p for p in files if parse_rank(p.name) in named_ranks]
    other_pool = [p for p in files if parse_rank(p.name) not in named_ranks]

    if len(named_pool) < 4:
        raise RuntimeError("Nincs legalább 4 különböző neves lap!")
    if len(other_pool) < 6:
        raise RuntimeError("Nincs legalább 6 különböző nem neves lap!")

    # kiválasztás: 4 neves (2 bal belső, 2 jobb belső) + 6 másik (3-3 külső)
    chosen_named = random.sample(named_pool, 4)
    chosen_others = random.sample(other_pool, 6)

    left_cards = [chosen_others[0], chosen_others[1], chosen_others[2], chosen_named[0], chosen_named[1]]
    right_cards = [chosen_others[3], chosen_others[4], chosen_others[5], chosen_named[2], chosen_named[3]]

    # vászon (átlátszó)
    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2

    # hátlap középre
    back_img = load_and_scale(back_card, CARD_TARGET_HEIGHT + int(CANVAS_SIZE * 0.016))
    back_shadow = add_shadow(back_img, offset=SHADOW_OFFSET, blur_radius=SHADOW_BLUR)
    bx = cx - back_img.width // 2
    by = cy - back_img.height // 2
    canvas.alpha_composite(back_shadow, (bx, by))
    canvas.alpha_composite(back_img, (bx, by))

    # félkör pozíciók (szélsők fent, belsők lent)
    angles_left = [55, 35, 15, -5, -25]
    left_positions = []
    for ang in angles_left:
        rad = math.radians(ang)
        x = cx - (CENTER_RADIUS * math.cos(rad))
        y = cy - (CENTER_RADIUS * math.sin(rad))
        left_positions.append((x, y, -ang))

    # bal oldali kártyák
    for i, path in enumerate(left_cards):
        img = load_and_scale(path, CARD_TARGET_HEIGHT)
        rotated = img.rotate(left_positions[i][2], resample=Image.BICUBIC, expand=True)
        shadow = add_shadow(rotated)
        pos_x = int(left_positions[i][0] - rotated.width // 2)
        pos_y = int(left_positions[i][1] - rotated.height // 2)
        canvas.alpha_composite(shadow, (pos_x, pos_y))
        canvas.alpha_composite(rotated, (pos_x, pos_y))

    # jobb oldali kártyák (tükörszimmetria)
    for i, path in enumerate(right_cards):
        img = load_and_scale(path, CARD_TARGET_HEIGHT)
        x, y, ang = left_positions[i]
        x = cx + (cx - x)
        ang = -ang
        rotated = img.rotate(ang, resample=Image.BICUBIC, expand=True)
        shadow = add_shadow(rotated)
        pos_x = int(x - rotated.width // 2)
        pos_y = int(y - rotated.height // 2)
        canvas.alpha_composite(shadow, (pos_x, pos_y))
        canvas.alpha_composite(rotated, (pos_x, pos_y))

    # mentés átlátszó PNG-ként
    canvas.save(OUTPUT, format="PNG")
    print(f"Mentve: {OUTPUT}")

if __name__ == "__main__":
    main()
