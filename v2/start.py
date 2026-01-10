import os
from PIL import Image

# --- Beállítások ---
SPRITE_WIDTH = 600
SPRITE_HEIGHT = 600
SPRITE_COLS = 9
SPRITE_ROWS = 2

CARD_WIDTH = 1494  # 63 mm @ 600 DPI
CARD_HEIGHT = 2244  # 88 mm @ 600 DPI

#bleed: 1494 x 2244
#cut: 1350 x 2100
#safe: 1230 x 1980

OUTPUT_DIR = "fulldeck"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SPRITE_NAMES = [
    "spades", "hearts", "clubs", "diamonds",
    "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "J", "Q", "K", "A", "JOKER"
]

# --- Szimbólumok középre (2–10) ---
pip_col_l = 500
pip_col_c = (CARD_WIDTH // 2)
pip_col_r = (CARD_WIDTH - pip_col_l)

PIP_POSITIONS = {
    "2": [(pip_col_c, 450), (pip_col_c, CARD_HEIGHT - 450)],
    "3": [(pip_col_r, 450), (pip_col_c, CARD_HEIGHT // 2), (pip_col_l, CARD_HEIGHT - 450)],
    "4": [(pip_col_l, 500), (pip_col_r, 500), (pip_col_l, CARD_HEIGHT - 500), (pip_col_r, CARD_HEIGHT - 500)],
    "5": [(pip_col_c, CARD_HEIGHT // 2), (pip_col_l, 500), (pip_col_r, 500),
          (pip_col_l, CARD_HEIGHT - 500), (pip_col_r, CARD_HEIGHT - 500)],
    "6": [(pip_col_l, 500), (pip_col_r, 500), (pip_col_l, CARD_HEIGHT // 2), (pip_col_r, CARD_HEIGHT // 2),
          (pip_col_l, CARD_HEIGHT - 500), (pip_col_r, CARD_HEIGHT - 500)],
}

# Ezeket utólag adjuk hozzá, hogy a hivatkozás működjön
PIP_POSITIONS["7"] = [(pip_col_c, 775)] + PIP_POSITIONS["6"]
PIP_POSITIONS["8"] = [(pip_col_c, CARD_HEIGHT - 775)] + PIP_POSITIONS["7"]
PIP_POSITIONS["9"] = [(pip_col_c, CARD_HEIGHT // 2)] + PIP_POSITIONS["8"]
PIP_POSITIONS["10"] = [(pip_col_l, 775), (pip_col_l, CARD_HEIGHT - 775), (pip_col_r, 775), (pip_col_r, CARD_HEIGHT - 775)] + PIP_POSITIONS["6"]


# --- Sprite feldarabolás ---
def load_sprites(sheet_path):
    sheet = Image.open(sheet_path)
    sprites = {}
    for i, name in enumerate(SPRITE_NAMES):
        col = i % SPRITE_COLS
        row = i // SPRITE_COLS
        x0 = col * SPRITE_WIDTH
        y0 = row * SPRITE_HEIGHT
        sprite = sheet.crop((x0, y0, x0 + SPRITE_WIDTH, y0 + SPRITE_HEIGHT))
        sprites[name] = sprite
    return sprites

# --- Kártya generátor ---
def generate_card(card_name, sprites):
    card = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), "white")

    suit = card_name.split("_")[0]

    if os.path.exists("./template/card_front.png"):
        overlay = Image.open("./template/card_front.png").convert("RGBA")
        ox = (CARD_WIDTH - overlay.width) // 2
        oy = (CARD_HEIGHT - overlay.height) // 2
        card.paste(overlay, (ox, oy), overlay)
    elif os.path.exists(f"./template/{suit}_bg.png"):
        bg = Image.open(f"./template/{suit}_bg.png").convert("RGBA")
        ox = (CARD_WIDTH - bg.width) // 2
        oy = (CARD_HEIGHT - bg.height) // 2
        card.paste(bg, (ox, oy), bg)

    if card_name.startswith("joker"):
        label = sprites["JOKER"].resize((200, 200))
        # Sarokfelirat: JOKER felül és alul (tükrözve)
        card.paste(label, (170, 110), label)
        card.paste(label.rotate(180), (CARD_WIDTH - 170 - label.width, CARD_HEIGHT - 110 - label.height), label.rotate(180))

        # Középen a 4 színes sprite
        center_x, center_y = CARD_WIDTH // 2, CARD_HEIGHT // 2
        size = 600  # 300% méret (kb.)
        offset = 250  # távolság a középponttól

        # Szimbólumok elrendezése: (suit_name, rotation, dx, dy)
        elements = [
            ("hearts",     45, -offset, -offset),  # bal felső
            ("clubs",     -45,  offset, -offset),  # jobb felső
            ("spades",    135, -offset,  offset),  # bal alsó
            ("diamonds", -135,  offset,  offset)   # jobb alsó
        ]

        for suit, angle, dx, dy in elements:
            sym = sprites[suit].resize((size, size)).rotate(angle, expand=True)
            pos_x = center_x + dx - sym.width // 2
            pos_y = center_y + dy - sym.height // 2
            card.paste(sym, (pos_x, pos_y), sym)
    else:
        suit, rank = card_name.split("_")
        suit_sprite = sprites[suit].resize((220, 220))
        rank_sprite = sprites[rank].resize((220, 220))

        # Sarok elrendezés – szám felül, jel alul
        # Bal felső
        card.paste(rank_sprite, (170, 110), rank_sprite)
        card.paste(suit_sprite, (170, 280), suit_sprite)

        # Jobb alsó (tükrözve)
        rank_rot = rank_sprite.rotate(180)
        suit_rot = suit_sprite.rotate(180)
        card.paste(rank_rot, (CARD_WIDTH - 170 - rank_rot.width, CARD_HEIGHT - 110 - rank_rot.height), rank_rot)
        card.paste(suit_rot, (CARD_WIDTH - 170 - suit_rot.width, CARD_HEIGHT - 280 - suit_rot.height), suit_rot)

        # Középső mintázat csak 2–10 esetén
        if rank in PIP_POSITIONS:
            pip_sprite = suit_sprite.resize((200, 200))
            for (x, y) in PIP_POSITIONS[rank]:
                card.paste(pip_sprite, (x - pip_sprite.width // 2, y - pip_sprite.height // 2), pip_sprite)

        # Középső mintázat csak A esetén
        if rank in ["A", "J", "Q", "K"]:
            if os.path.exists(f"{suit}_{rank}.png"):
                print(f"✅ Van {suit}_{rank} overlay")
                overlay = Image.open(f"{suit}_{rank}.png").convert("RGBA")
                ox = (CARD_WIDTH - overlay.width) // 2
                oy = (CARD_HEIGHT - overlay.height) // 2
                card.paste(overlay, (ox, oy), overlay)
            else:
                big_suit = suit_sprite.resize((600, 600))
                card.paste(big_suit, ((CARD_WIDTH - big_suit.width) // 2, (CARD_HEIGHT - big_suit.height) // 2), big_suit)
    
    return card

# --- Pakli generálás ---
def main():
    sprites = load_sprites("./template/template.png")

    suits = ["hearts", "spades", "diamonds", "clubs"]
    ranks = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]
    cards = [f"{suit}_{rank}" for suit in suits for rank in ranks] + ["joker_card"]


    for card_name in cards:
        print(f"🎴 Generate: {card_name}")
        card = generate_card(card_name, sprites)
        card.save(os.path.join(OUTPUT_DIR, f"{card_name}.png"))

    print(f"✅ Done: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
