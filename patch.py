import discord
from discord.ext import commands
from discord import app_commands
from helpers import load_data, tier_color, tier_emoji, brawler_autocomplete

class Patch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── /patch ───────────────────────────────────────────────────────────────
    @app_commands.command(name="patch", description="Résumé du dernier patch et impact sur la méta")
    async def patch(self, interaction: discord.Interaction):
        data = load_data()
        patches = data.get("patches", [])

        if not patches:
            await interaction.response.send_message("❌ Aucun patch disponible.", ephemeral=True)
            return

        latest = patches[0]

        embed = discord.Embed(
            title=f"📰 {latest['titre']} — v{latest['version']}",
            description=f"📅 *{latest['date']}*\n\n{latest['analyse']}",
            color=0x2ECC71
        )

        # Buffs
        buffs = [c for c in latest["changements"] if c["type"] == "buff"]
        if buffs:
            buff_lines = [f"✅ **{c['brawler']}** — {c['detail']}" for c in buffs]
            embed.add_field(name="⬆️ Buffs", value="\n".join(buff_lines), inline=False)

        # Nerfs
        nerfs = [c for c in latest["changements"] if c["type"] == "nerf"]
        if nerfs:
            nerf_lines = [f"❌ **{c['brawler']}** — {c['detail']}" for c in nerfs]
            embed.add_field(name="⬇️ Nerfs", value="\n".join(nerf_lines), inline=False)

        # Nouveaux brawlers
        if latest.get("nouveaux_brawlers"):
            embed.add_field(
                name="✨ Nouveaux Brawlers",
                value=" • ".join(latest["nouveaux_brawlers"]),
                inline=False
            )

        embed.set_footer(text="MetaBot Brawl Stars • Données Null's Brawl & officiel")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Patch(bot))
