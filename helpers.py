import json
import os

# Cherche brawlers.json dans le même dossier que le script ou dans data/
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    # Essaie plusieurs emplacements
    paths = [
        os.path.join(base, "..", "data", "brawlers.json"),
        os.path.join(base, "..", "brawlers.json"),
        os.path.join(base, "brawlers.json"),
        "brawlers.json",
        "data/brawlers.json",
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("brawlers.json introuvable")

def tier_color(tier: str) -> int:
    colors = {"S": 0xFF6B35, "A": 0xFFD700, "B": 0x2ECC71, "C": 0x3498DB, "D": 0x95A5A6}
    return colors.get(tier, 0xFFFFFF)

def tier_emoji(tier: str) -> str:
    emojis = {"S": "🔴", "A": "🟠", "B": "🟡", "C": "🔵", "D": "⚫"}
    return emojis.get(tier, "⚪")

def brawler_autocomplete(current: str):
    data = load_data()
    return [name for name in data["brawlers"] if current.lower() in name.lower()]
