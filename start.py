
from PIL import Image
import json
import os

# Beállítások
# CARD_WIDTH = 743
# CARD_HEIGHT = 1125
CARD_WIDTH = 1486
CARD_HEIGHT = 2250

template_path = "template.png"
json_path = "template.json"
output_dir = "output_cards"
os.makedirs(output_dir, exist_ok=True)

# Dinamikus pip pozíciók sprite méret alapján
def generate_scaled_pip_layouts(sprite_width, sprite_height):
    max_dx = 420 - sprite_width // 2
    max_dy = 840 - sprite_height // 2

    return {
        2:  [(0, -max_dy), (0, max_dy)],
        3:  [(0, -max_dy), (0, 0), (0, max_dy)],
        4:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (-max_dx, max_dy), (max_dx, max_dy)],
        5:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (0, 0),
             (-max_dx, max_dy), (max_dx, max_dy)],
        6:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (-max_dx, 0), (max_dx, 0),
             (-max_dx, max_dy), (max_dx, max_dy)],
        7:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (-max_dx, 0), (max_dx, 0),
             (-max_dx, max_dy), (max_dx, max_dy),
             (0, -max_dy // 2)],
        8:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (-max_dx, 0), (max_dx, 0),
             (-max_dx, max_dy), (max_dx, max_dy),
             (0, -max_dy // 2), (0, max_dy // 2)],
        9:  [(-max_dx, -max_dy), (max_dx, -max_dy),
             (-max_dx, 0), (max_dx, 0),
             (-max_dx, max_dy), (max_dx, max_dy),
             (0, -max_dy // 2), (0, max_dy // 2), (0, 0)],
        10: [(-max_dx, -max_dy), (max_dx, -max_dy),
              (-max_dx, -max_dy // 2), (max_dx, -max_dy // 2),
              (-max_dx, 0), (max_dx, 0),
              (-max_dx, max_dy // 2), (max_dx, max_dy // 2),
              (-max_dx, max_dy), (max_dx, max_dy)]
    }

# Betöltés
with open(json_path, "r") as f:
    data = json.load(f)

base = {item["cell"]: item for item in data["base"]}

cards = {}
for entry in data["cards"]:
    for card_name, layers in entry.items():
        cards[card_name] = layers

template = Image.open(template_path)

# Kártyák generálása
for card_name, layers in cards.items():
    result = Image.new("RGBA", (CARD_WIDTH, CARD_HEIGHT), (255, 255, 255, 0))

    for layer in layers:
        if isinstance(layer, list) and len(layer) == 2 and isinstance(layer[1], int):
            sprite_key, count = layer
            sprite_region = base.get(sprite_key)
            if not sprite_region:
                continue

            x, y, w, h = sprite_region["x"], sprite_region["y"], sprite_region["width"], sprite_region["height"]
            sprite = template.crop((x, y, x + w, y + h))
            layout = generate_scaled_pip_layouts(w, h).get(count, [])

            center_x = CARD_WIDTH // 2
            center_y = CARD_HEIGHT // 2

            for dx, dy in layout:
                px = int(center_x + dx - w // 2)
                py = int(center_y + dy - h // 2)
                result.paste(sprite, (px, py), sprite)

        elif isinstance(layer, str):
            region = base.get(layer)
            if not region:
                continue
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            part = template.crop((x, y, x + w, y + h))
            pos_x = (CARD_WIDTH - w) // 2
            pos_y = (CARD_HEIGHT - h) // 2
            result.paste(part, (pos_x, pos_y), part)

    result.save(os.path.join(output_dir, f"{card_name}.png"))
    print(f"✅ Elmentve: {card_name}.png")
