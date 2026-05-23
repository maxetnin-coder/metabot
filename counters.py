import discord
from discord.ext import commands
from discord import app_commands
from utils.helpers import load_data

class Counters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── /counter <brawler> ───────────────────────────────────────────────────
    @app_commands.command(name="counter", description="Counters d'un brawler")
    @app_commands.describe(brawler="Nom du brawler à counter")
    async def counter(self, interaction: discord.Interaction, brawler: str):
        data = load_data()
        brawlers = data["brawlers"]

        found = None
        for key in brawlers:
            if key.lower() == brawler.lower():
                found = (key, brawlers[key])
                break

        if not found:
            await interaction.response.send_message(
                f"❌ Brawler **{brawler}** introuvable. Vérifie l'orthographe.", ephemeral=True
            )
            return

        name, info = found

        embed = discord.Embed(
            title=f"⚔️ Counters de {info['emoji']} {name}",
            description=f"*{info['description']}*",
            color=0xE74C3C
        )

        # Counters (ce qui bat ce brawler)
        counter_details = []
        for c_name in info["counters"]:
            c_info = brawlers.get(c_name, {})
            counter_details.append(
                f"**{c_info.get('emoji', '')} {c_name}**\n"
                f"└ {c_info.get('description', 'Aucune info')}"
            )
        embed.add_field(
            name=f"❌ Ce qui bat {name}",
            value="\n".join(counter_details) if counter_details else "Aucun connu",
            inline=False
        )

        # Ce que ce brawler counter (cherche dans toutes les données)
        countered_by = []
        for b_name, b_info in brawlers.items():
            if name in b_info.get("counters", []):
                countered_by.append(f"{b_info.get('emoji', '')} **{b_name}**")

        if countered_by:
            embed.add_field(
                name=f"✅ Ce que {name} contre",
                value=" • ".join(countered_by),
                inline=False
            )

        embed.set_footer(text="MetaBot Brawl Stars • /synergy pour les compositions")
        await interaction.response.send_message(embed=embed)

    # ─── /synergy <brawler> ───────────────────────────────────────────────────
    @app_commands.command(name="synergy", description="Meilleures compositions avec un brawler")
    @app_commands.describe(brawler="Nom du brawler")
    async def synergy(self, interaction: discord.Interaction, brawler: str):
        data = load_data()
        brawlers = data["brawlers"]

        found = None
        for key in brawlers:
            if key.lower() == brawler.lower():
                found = (key, brawlers[key])
                break

        if not found:
            await interaction.response.send_message(
                f"❌ Brawler **{brawler}** introuvable.", ephemeral=True
            )
            return

        name, info = found

        embed = discord.Embed(
            title=f"🤝 Synergies — {info['emoji']} {name}",
            description=f"*Meilleures compositions avec {name}*",
            color=0x3498DB
        )

        synergy_details = []
        for s_name in info["synergies"]:
            s_info = brawlers.get(s_name, {})
            synergy_details.append(
                f"**{s_info.get('emoji', '')} {s_name}** *(Tier moyen: {_avg_tier(s_info)})*\n"
                f"└ {s_info.get('description', 'Aucune info')}"
            )

        embed.add_field(
            name="✨ Composition recommandée",
            value="\n".join(synergy_details) if synergy_details else "Aucune synergie connue",
            inline=False
        )

        # Exemple de trio
        if len(info["synergies"]) >= 2:
            trio = f"{info['emoji']} {name} + {brawlers.get(info['synergies'][0], {}).get('emoji', '')} {info['synergies'][0]} + {brawlers.get(info['synergies'][1], {}).get('emoji', '')} {info['synergies'][1]}"
            embed.add_field(name="🏆 Trio recommandé", value=trio, inline=False)

        embed.set_footer(text="MetaBot Brawl Stars")
        await interaction.response.send_message(embed=embed)


def _avg_tier(info):
    tier_scores = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
    rev = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D"}
    scores = [tier_scores.get(t, 1) for t in info.get("tiers", {}).values()]
    if not scores:
        return "?"
    avg = round(sum(scores) / len(scores))
    return rev.get(avg, "B")


async def setup(bot):
    await bot.add_cog(Counters(bot))
