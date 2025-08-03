# 🃏 def-card-generator

**Python script for generating printable playing cards** from a large PNG template, based on positional data from a JSON layout.

Designed for projects like custom decks, AI art series, or stylized card games.  
Originally developed for the **DarkEggFactory** fantasy brand.

---

## 📂 Files included

| File | Purpose |
|------|---------|
| `template.svg` | Source vector layout (editable in Inkscape/Illustrator) |
| `template.png` | High-res image (7431 × 18000 px) used for card slicing |
| `template.json` | Contains coordinates & names of each card (x, y, width, height, filename) |
| `start.py` | The main script – processes the template and exports each card to `/output_cards/` |

---

## 🚀 How to use

1. Make sure you have **Python 3.7+** and **Pillow** installed:
pip install pillow

2. Create your own design (use the template.svg for example)

3. Save your template az template.png (7431×18000 px)

4. Run the script
python start.py

5. Your cards appear in output_cards subdir

