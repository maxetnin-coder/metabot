import discord
from discord.ext import commands
from discord import app_commands
import json
from utils.helpers import load_data, tier_emoji

class TierList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── /tierlist ────────────────────────────────────────────────────────────
    @app_commands.command(name="tierlist", description="Tier list générale de tous les brawlers")
    async def tierlist(self, interaction: discord.Interaction):
        data = load_data()
        brawlers = data["brawlers"]

        # Score moyen par brawler
        tier_scores = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
        tiers_avg = {"S": [], "A": [], "B": [], "C": [], "D": []}

        for name, info in brawlers.items():
            scores = [tier_scores.get(t, 1) for t in info["tiers"].values()]
            avg = sum(scores) / len(scores) if scores else 1
            if avg >= 4.5:
                tiers_avg["S"].append(f"{info['emoji']} {name}")
            elif avg >= 3.5:
                tiers_avg["A"].append(f"{info['emoji']} {name}")
            elif avg >= 2.5:
                tiers_avg["B"].append(f"{info['emoji']} {name}")
            elif avg >= 1.5:
                tiers_avg["C"].append(f"{info['emoji']} {name}")
            else:
                tiers_avg["D"].append(f"{info['emoji']} {name}")

        embed = discord.Embed(
            title="📊 Tier List Générale — Brawl Stars",
            description="Basée sur la moyenne des tiers dans tous les modes de jeu",
            color=0x9B59B6
        )

        for tier in ["S", "A", "B", "C", "D"]:
            lst = tiers_avg[tier]
            if lst:
                embed.add_field(
                    name=f"{tier_emoji(tier)} Tier {tier}",
                    value=" • ".join(lst),
                    inline=False
                )

        embed.set_footer(text="MetaBot Brawl Stars • /meta <mode> pour une tier list spécifique")
        await interaction.response.send_message(embed=embed)

    # ─── /brawler <nom> ───────────────────────────────────────────────────────
    @app_commands.command(name="brawler", description="Fiche complète d'un brawler")
    @app_commands.describe(nom="Nom du brawler")
    async def brawler_info(self, interaction: discord.Interaction, nom: str):
        data = load_data()
        brawlers = data["brawlers"]

        # Recherche insensible à la casse
        found = None
        for key in brawlers:
            if key.lower() == nom.lower():
                found = (key, brawlers[key])
                break

        if not found:
            # Suggestions
            suggestions = [k for k in brawlers if nom.lower() in k.lower()]
            msg = f"❌ Brawler **{nom}** non trouvé."
            if suggestions:
                msg += f"\n💡 Tu voulais dire : **{', '.join(suggestions[:3])}** ?"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        name, info = found

        embed = discord.Embed(
            title=f"{info['emoji']} {name}",
            description=f"*{info['description']}*",
            color=0xE74C3C
        )

        # Tiers par mode
        tiers_lines = []
        for mode, tier in info["tiers"].items():
            mode_emoji = {"Gem Grab": "💎", "Brawl Ball": "⚽", "Heist": "💰",
                          "Bounty": "⭐", "Siege": "🔩", "Hot Zone": "🔥", "Knockout": "💀"}
            tiers_lines.append(f"{mode_emoji.get(mode, '🎮')} {mode}: **{tier}** {tier_emoji(tier)}")

        embed.add_field(name="📊 Tiers par mode", value="\n".join(tiers_lines), inline=True)

        embed.add_field(
            name="ℹ️ Infos",
            value=f"**Classe :** {info['classe']}\n**Portée :** {info['portee']}\n**Super :** {info['super']}",
            inline=True
        )

        embed.add_field(
            name="⚔️ Counters",
            value=" • ".join([f"{brawlers.get(c, {}).get('emoji', '')} {c}" for c in info["counters"]]) or "Aucun",
            inline=False
        )

        embed.add_field(
            name="🤝 Synergies",
            value=" • ".join([f"{brawlers.get(s, {}).get('emoji', '')} {s}" for s in info["synergies"]]) or "Aucune",
            inline=False
        )

        embed.set_footer(text="MetaBot Brawl Stars • /counter pour plus de détails")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(TierList(bot))
