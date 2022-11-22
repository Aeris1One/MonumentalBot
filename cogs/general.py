""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3
"""

import platform
import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="Lister toutes les commandes du bot."
    )
    @checks.not_blacklisted()
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(
            title="Aide", description="Liste des commandes:", color=0x9C84EF)
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            data = []
            for command in commands:
                description = command.description.partition('\n')[0]
                data.append(f"{prefix}{command.name} - {description}")
            help_text = "\n".join(data)
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="botinfo",
        description="Quelques infos (utiles ou non) sur le bot.",
    )
    @checks.not_blacklisted()
    async def botinfo(self, context: Context) -> None:
        """
        Quelques infos (utiles ou non) sur le bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description="Basé sur une template de [Krypton](https://krypton.ninja)",
            color=0x9C84EF
        )
        embed.set_author(
            name="Informations sur le bot",
        )
        embed.add_field(
            name="Admin:",
            value="Aeris One#9906",
            inline=True
        )
        embed.add_field(
            name="Version de Python:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Préfixe:",
            value=f"/ (commandes slash) ou {self.bot.config['prefix']} pour les commandes classiques",
            inline=False
        )
        embed.set_footer(
            text=f"Demandé par {context.author}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Obtenir des informations sur le serveur.",
    )
    @checks.not_blacklisted()
    async def serverinfo(self, context: Context) -> None:
        """
        Obtenir des informations sur le serveur.

        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Affichage des rôles [50/{len(roles)}]")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Nom du serveur:**",
            description=f"{context.guild}",
            color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(
                url=context.guild.icon.url
            )
        embed.add_field(
            name="ID Serveur",
            value=context.guild.id
        )
        embed.add_field(
            name="Nombre de membres",
            value=context.guild.member_count
        )
        embed.add_field(
            name="Nombre de channels",
            value=f"{len(context.guild.channels)}"
        )
        embed.add_field(
            name=f"Rôles ({len(context.guild.roles)})",
            value=roles
        )
        embed.set_footer(
            text=f"Crée le: {context.guild.created_at}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Voir le ping du bot.",
    )
    @checks.not_blacklisted()
    async def ping(self, context: Context) -> None:
        """
        Voir le ping du bot.

        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Mon ping est de {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Posez une question à la boule magique.",
    )
    @checks.not_blacklisted()
    @app_commands.describe(question="La question à poser à la boule magique.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Posez une question à la boule magique.

        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """
        answers = ["C'est certain.", "Absolument.", "Croyez-m'en.", "Sans doute.",
                   "Oui - sûrement.", "D'aprés moi, oui.", "Probablement.", "Il semblerait.", "Oui.",
                   "Les signes semblent dire que oui.", "Je n'ai pas de réponse, réessayez.", "Et si vous essayiez plus tard.", "Il vaut mieux ne rien dire pour l'instant.",
                   "Je ne peux rien prédire pour l'instant.", "Laissez-moi me concentrer et réessayez plus tard.", "Ne comptez pas là-dessus.", "Ma réponse est non.",
                   "Mes sources me disent que non.", "Il ne semble pas, non.", "Vraiment peu probable.", "Pas officiellement.", "Ce n'est pas impossible.", "Pourquoi pas.",
                   "Ce n'est pas impossible.", "Tant que ce n'est pas illégal.", "Comme vous voulez.", "Je n'en sais foutrement rien."]
        embed = discord.Embed(
            title=f"{question}",
            description=f"{random.choice(answers)}",
            color=0x9C84EF
        )
        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
