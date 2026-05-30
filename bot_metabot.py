import discord
from discord.ext import commands
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ─── Config ───────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "TON_TOKEN_ICI")
PREFIX = "/"

# Ajouter le dossier courant au path pour trouver les fichiers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ─── Serveur web pour UptimeRobot ─────────────────────────────────────────────
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MetaBot is alive!")
    def log_message(self, format, *args):
        pass

def run_webserver():
    server = HTTPServer(("0.0.0.0", 8080), PingHandler)
    server.serve_forever()

# ─── Load cogs ────────────────────────────────────────────────────────────────
COGS = ["meta", "tierlist", "patch", "counters", "votes"]

@bot.event
async def on_ready():
    print(f"✅ MetaBot connecté en tant que {bot.user}")
    await bot.tree.sync()
    print("✅ Slash commands synchronisées")

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Cog chargé : {cog}")
            except Exception as e:
                print(f"❌ Erreur chargement {cog} : {e}")
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    t = threading.Thread(target=run_webserver, daemon=True)
    t.start()
    print("✅ Serveur web démarré sur le port 8080")
    asyncio.run(main())
