import discord
from discord.ext import commands
from discord import app_commands
import json
from helpers import load_data, tier_color, tier_emoji, brawler_autocomplete

class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── /meta <mode> ────────────────────────────────────────────────────────
    @app_commands.command(name="meta", description="Affiche la tier list d'un mode de jeu")
    @app_commands.describe(mode="Mode de jeu (Gem Grab, Brawl Ball, Heist...)")
    @app_commands.choices(mode=[
        app_commands.Choice(name="💎 Gem Grab", value="Gem Grab"),
        app_commands.Choice(name="⚽ Brawl Ball", value="Brawl Ball"),
        app_commands.Choice(name="💰 Heist", value="Heist"),
        app_commands.Choice(name="⭐ Bounty", value="Bounty"),
        app_commands.Choice(name="🔩 Siege", value="Siege"),
        app_commands.Choice(name="🔥 Hot Zone", value="Hot Zone"),
        app_commands.Choice(name="💀 Knockout", value="Knockout"),
    ])
    async def meta(self, interaction: discord.Interaction, mode: str):
        data = load_data()
        brawlers = data["brawlers"]
        mode_info = data["modes"].get(mode, {})

        # Grouper par tier
        tiers = {"S": [], "A": [], "B": [], "C": [], "D": []}
        for name, info in brawlers.items():
            tier = info["tiers"].get(mode, "C")
            tiers[tier].append(f"{info['emoji']} {name}")

        embed = discord.Embed(
            title=f"{mode_info.get('emoji', '🎮')} Tier List — {mode}",
            description=f"*{mode_info.get('description', '')}*",
            color=0xFFD700
        )

        for tier in ["S", "A", "B", "C", "D"]:
            brawler_list = tiers[tier]
            if brawler_list:
                embed.add_field(
                    name=f"{tier_emoji(tier)} Tier {tier}",
                    value=" • ".join(brawler_list) if brawler_list else "*Aucun*",
                    inline=False
                )

        embed.set_footer(text="MetaBot Brawl Stars • Données mises à jour régulièrement")
        embed.set_thumbnail(url="https://cdn.brawlify.com/brawlstars/regular/trophy-league.png")
        await interaction.response.send_message(embed=embed)

    # ─── /bestfor <map> ──────────────────────────────────────────────────────
    @app_commands.command(name="bestfor", description="Meilleurs brawlers pour un mode de jeu")
    @app_commands.describe(mode="Mode de jeu dont tu veux le top 5")
    @app_commands.choices(mode=[
        app_commands.Choice(name="💎 Gem Grab", value="Gem Grab"),
        app_commands.Choice(name="⚽ Brawl Ball", value="Brawl Ball"),
        app_commands.Choice(name="💰 Heist", value="Heist"),
        app_commands.Choice(name="⭐ Bounty", value="Bounty"),
        app_commands.Choice(name="🔩 Siege", value="Siege"),
        app_commands.Choice(name="🔥 Hot Zone", value="Hot Zone"),
        app_commands.Choice(name="💀 Knockout", value="Knockout"),
    ])
    async def bestfor(self, interaction: discord.Interaction, mode: str):
        data = load_data()
        brawlers = data["brawlers"]
        tier_order = {"S": 0, "A": 1, "B": 2, "C": 3, "D": 4}

        # Trier les brawlers par tier pour ce mode
        ranked = sorted(
            brawlers.items(),
            key=lambda x: tier_order.get(x[1]["tiers"].get(mode, "D"), 4)
        )
        top5 = ranked[:5]

        mode_info = data["modes"].get(mode, {})
        embed = discord.Embed(
            title=f"🏆 Top 5 Brawlers — {mode_info.get('emoji', '')} {mode}",
            description=f"*{mode_info.get('description', '')}*",
            color=0x00BFFF
        )

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, (name, info) in enumerate(top5):
            tier = info["tiers"].get(mode, "C")
            embed.add_field(
                name=f"{medals[i]} {info['emoji']} {name} — Tier {tier}",
                value=f"*{info['description']}*\n**Classe :** {info['classe']} | **Portée :** {info['portee']}",
                inline=False
            )

        embed.set_footer(text="MetaBot Brawl Stars • Données communautaires")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Meta(bot))
