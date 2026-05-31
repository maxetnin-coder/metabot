import discord
from discord.ext import commands
import os
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# ─── Config ───────────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "TON_TOKEN_ICI")
GUILD_ID = 1503381327456501760
PORT = int(os.getenv("PORT", 8080))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Serveur web ──────────────────────────────────────────────────────────────
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MetaBot is alive!")
    def log_message(self, format, *args):
        pass

def run_webserver():
    server = HTTPServer(("0.0.0.0", PORT), PingHandler)
    print(f"✅ Serveur web démarré sur le port {PORT}", flush=True)
    server.serve_forever()

# ─── Cogs ─────────────────────────────────────────────────────────────────────
COGS = ["meta", "tierlist", "patch", "counters", "votes"]

@bot.event
async def on_ready():
    print(f"✅ MetaBot connecté : {bot.user}", flush=True)
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ {len(synced)} commandes synchronisées", flush=True)
    except Exception as e:
        print(f"❌ Erreur sync : {e}", flush=True)
        traceback.print_exc()

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Cog chargé : {cog}", flush=True)
            except Exception as e:
                print(f"❌ Erreur {cog} : {e}", flush=True)
                traceback.print_exc()
        print("🔄 Connexion à Discord...", flush=True)
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    print("🚀 Démarrage du MetaBot...", flush=True)
    t = threading.Thread(target=run_webserver, daemon=True)
    t.start()
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Erreur fatale : {e}", flush=True)
        traceback.print_exc()
