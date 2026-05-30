import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from helpers import load_data, tier_emoji

VOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "votes.json")

def load_votes():
    if not os.path.exists(VOTES_FILE):
        return {}
    with open(VOTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_votes(data):
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_community_tier(brawler_votes):
    if not brawler_votes:
        return "?"
    tier_scores = {"S": 5, "A": 4, "B": 3, "C": 2, "D": 1}
    rev = {5: "S", 4: "A", 3: "B", 2: "C", 1: "D"}
    total = sum(tier_scores.get(t, 3) for t in brawler_votes.values())
    avg = round(total / len(brawler_votes))
    return rev.get(avg, "B")

class Votes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="voter", description="Voter pour le tier d'un brawler")
    @app_commands.describe(brawler="Nom du brawler", tier="Tier selon toi (S/A/B/C/D)")
    @app_commands.choices(tier=[
        app_commands.Choice(name="🔴 S — Overpowered", value="S"),
        app_commands.Choice(name="🟠 A — Très fort", value="A"),
        app_commands.Choice(name="🟡 B — Correct", value="B"),
        app_commands.Choice(name="🔵 C — Faible", value="C"),
        app_commands.Choice(name="⚫ D — Inutilisable", value="D"),
    ])
    async def voter(self, interaction: discord.Interaction, brawler: str, tier: str):
        data = load_data()
        brawlers = data["brawlers"]

        found = None
        for key in brawlers:
            if key.lower() == brawler.lower():
                found = key
                break

        if not found:
            suggestions = [k for k in brawlers if brawler.lower() in k.lower()]
            msg = f"❌ Brawler **{brawler}** introuvable."
            if suggestions:
                msg += f"\n💡 Tu voulais dire : **{', '.join(suggestions[:3])}** ?"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        votes = load_votes()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)

        if guild_id not in votes:
            votes[guild_id] = {}
        if found not in votes[guild_id]:
            votes[guild_id][found] = {}

        ancien_vote = votes[guild_id][found].get(user_id)
        votes[guild_id][found][user_id] = tier
        save_votes(votes)

        brawler_info = brawlers[found]
        nb_votes = len(votes[guild_id][found])
        tier_communautaire = get_community_tier(votes[guild_id][found])

        embed = discord.Embed(title=f"✅ Vote enregistré !", color=0x2ECC71)
        embed.add_field(name=f"{brawler_info['emoji']} {found}", value=f"Ton vote : **Tier {tier}** {tier_emoji(tier)}", inline=False)
        if ancien_vote:
            embed.add_field(name="📝 Modification", value=f"Ancien vote : Tier {ancien_vote} → Tier {tier}", inline=False)
        embed.add_field(name="👥 Votes totaux", value=str(nb_votes), inline=True)
        embed.add_field(name="📊 Tier communautaire", value=f"**{tier_communautaire}** {tier_emoji(tier_communautaire)}", inline=True)
        embed.set_footer(text="MetaBot • /tierlist_communautaire pour voir la tier list complète")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tierlist_communautaire", description="Tier list basée sur les votes de la communauté")
    async def tierlist_communautaire(self, interaction: discord.Interaction):
        votes = load_votes()
        guild_id = str(interaction.guild_id)
        guild_votes = votes.get(guild_id, {})

        if not guild_votes:
            await interaction.response.send_message("❌ Aucun vote enregistré ! Utilisez `/voter` pour commencer.", ephemeral=True)
            return

        data = load_data()
        brawlers = data["brawlers"]
        tiers = {"S": [], "A": [], "B": [], "C": [], "D": []}

        for brawler, brawler_votes in guild_votes.items():
            if brawler in brawlers:
                info = brawlers[brawler]
                tier = get_community_tier(brawler_votes)
                nb = len(brawler_votes)
                if tier in tiers:
                    tiers[tier].append(f"{info['emoji']} {brawler} *({nb}🗳️)*")

        embed = discord.Embed(title="🗳️ Tier List Communautaire", description=f"Basée sur les votes des membres de **{interaction.guild.name}**", color=0x9B59B6)
        for tier in ["S", "A", "B", "C", "D"]:
            if tiers[tier]:
                embed.add_field(name=f"{tier_emoji(tier)} Tier {tier}", value=" • ".join(tiers[tier]), inline=False)

        total_votes = sum(len(v) for v in guild_votes.values())
        embed.set_footer(text=f"Total : {total_votes} votes • /voter pour participer")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mon_vote", description="Voir tous tes votes")
    async def mon_vote(self, interaction: discord.Interaction):
        votes = load_votes()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        guild_votes = votes.get(guild_id, {})
        data = load_data()
        brawlers = data["brawlers"]

        mes_votes = []
        for brawler, brawler_votes in guild_votes.items():
            if user_id in brawler_votes and brawler in brawlers:
                info = brawlers[brawler]
                tier = brawler_votes[user_id]
                mes_votes.append(f"{info['emoji']} **{brawler}** → Tier {tier} {tier_emoji(tier)}")

        if not mes_votes:
            await interaction.response.send_message("❌ Tu n'as encore voté pour aucun brawler ! Utilise `/voter`.", ephemeral=True)
            return

        embed = discord.Embed(title=f"🗳️ Votes de {interaction.user.display_name}", description="\n".join(mes_votes), color=0x3498DB)
        embed.set_footer(text=f"{len(mes_votes)} votes • /voter pour modifier")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reset_votes", description="[Admin] Réinitialiser tous les votes")
    @app_commands.default_permissions(administrator=True)
    async def reset_votes(self, interaction: discord.Interaction):
        votes = load_votes()
        guild_id = str(interaction.guild_id)
        if guild_id in votes:
            del votes[guild_id]
            save_votes(votes)
        await interaction.response.send_message("✅ Tous les votes ont été réinitialisés !")

    @app_commands.command(name="votes_brawler", description="Voir les votes pour un brawler spécifique")
    @app_commands.describe(brawler="Nom du brawler")
    async def votes_brawler(self, interaction: discord.Interaction, brawler: str):
        data = load_data()
        brawlers = data["brawlers"]
        found = None
        for key in brawlers:
            if key.lower() == brawler.lower():
                found = key
                break

        if not found:
            await interaction.response.send_message(f"❌ Brawler **{brawler}** introuvable.", ephemeral=True)
            return

        votes = load_votes()
        guild_id = str(interaction.guild_id)
        brawler_votes = votes.get(guild_id, {}).get(found, {})
        info = brawlers[found]

        if not brawler_votes:
            await interaction.response.send_message(f"❌ Aucun vote pour **{found}** ! Utilise `/voter {found}`.", ephemeral=True)
            return

        tier_count = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        for t in brawler_votes.values():
            if t in tier_count:
                tier_count[t] += 1

        tier_communautaire = get_community_tier(brawler_votes)
        embed = discord.Embed(title=f"{info['emoji']} Votes — {found}", color=0xFFD700)
        embed.add_field(name="📊 Tier communautaire", value=f"**{tier_communautaire}** {tier_emoji(tier_communautaire)}", inline=True)
        embed.add_field(name="👥 Total votes", value=str(len(brawler_votes)), inline=True)
        distribution = "\n".join([f"{tier_emoji(t)} Tier {t} : **{n}** vote{'s' if n > 1 else ''}" for t, n in tier_count.items() if n > 0])
        embed.add_field(name="📈 Distribution", value=distribution, inline=False)
        embed.set_footer(text="MetaBot • /voter pour participer")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Votes(bot))
