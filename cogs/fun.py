""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3
"""

import random

import aiohttp
import asyncio
import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks

class IQTestView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Pile", style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "pile"
        self.stop()

    @discord.ui.button(label="Face", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "face"
        self.stop()

class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Ciseaux", description="Vous avez choisi ciseaux.", emoji="✂"
            ),
            discord.SelectOption(
                label="Pierre", description="Vous avez choisi pierre.", emoji="🪨"
            ),
            discord.SelectOption(
                label="Papier", description="Vous avez choisi papier.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Choisissez...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "pierre": 0,
            "feuille": 1,
            "ciseaux": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0x9C84EF)
        result_embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url
        )

        if user_choice_index == bot_choice_index:
            result_embed.description = f"**Match nul !**\nVous avez choisi {user_choice} et j'ai choisi {bot_choice}."
            result_embed.colour = 0xF59E42
        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**Vous gagnez !**\nVous avez choisi {user_choice} et j'ai choisi {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 1 and bot_choice_index == 0:
            result_embed.description = f"**Vous gagnez !**\nVous avez choisi {user_choice} et j'ai choisi {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**Vous gagnez !**\nVous avez choisi {user_choice} et j'ai choisi {bot_choice}."
            result_embed.colour = 0x9C84EF
        else:
            result_embed.description = f"**J'ai gagné !**\nVous avez choisi {user_choice} et j'ai choisi {bot_choice}."
            result_embed.colour = 0xE02B2B
        await interaction.response.edit_message(embed=result_embed, content=None, view=None)


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="randomfact",
        description="Obtenir un fait aléatoire (en anglais, parce que j'ai pas d'API en français :/)."
    )
    @checks.not_blacklisted()
    async def randomfact(self, context: Context) -> None:
        """
        Obtenir un fait aléatoire.

        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"],
                        color=0xD75BF4
                    )
                else:
                    embed = discord.Embed(
                        title="Erreur!",
                        description="Problème d'API, réessaye plus tard",
                        color=0xE02B2B
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="pileouface",
        description="Un pile ou face classique."
    )
    @checks.not_blacklisted()
    async def coinflip(self, context: Context) -> None:
        """
        Un pile ou face classique.

        :param context: The hybrid command context.
        """
        buttons = Choice()
        embed = discord.Embed(
            description="Quel est votre choix ?",
            color=0x9C84EF
        )
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["pile", "face"])
        if buttons.value == result:
            embed = discord.Embed(
                description=f"Correct ! Vous avez deviné `{buttons.value}` et la pièce est tombée sur `{result}`.",
                color=0x9C84EF
            )
        else:
            embed = discord.Embed(
                description=f"Dommage ! Vous avez demandé `{buttons.value}` et la pièce est tombée sur `{result}`, la prochaine fois peut-être !",
                color=0xE02B2B
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="pfc",
        description="Pierre-feuille-ciseaux contre le bot."
    )
    @checks.not_blacklisted()
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Pierre-feuille-ciseaux contre le bot.

        :param context: The hybrid command context.
        """
        view = RockPaperScissorsView()
        await context.send("Faites un choix !", view=view)

    @commands.hybrid_command(
        name="iqtest",
        description="Teste ton QI d'huitre."
    )
    @checks.not_blacklisted()
    async def IQtest(self, context: Context) -> None:
        """
        Test de QI.

        :param context: The hybrid command context.
        """
        await context.send("Calcul en cours...")
        await asyncio.sleep(2)
        await context.edit(f"Ton QI est de {random.randint(0, 200)}.")



async def setup(bot):
    await bot.add_cog(Fun(bot))
