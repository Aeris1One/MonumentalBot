import asyncio
import random
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

from PIL import Image
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps

from helpers import checks

racers = (
    (":rabbit2:", "fast"),
    (":monkey:", "fast"),
    (":cat2:", "fast"),
    (":mouse2:", "slow"),
    (":chipmunk:", "fast"),
    (":rat:", "fast"),
    (":dove:", "fast"),
    (":bird:", "fast"),
    (":dromedary_camel:", "steady"),
    (":camel:", "steady"),
    (":dog2:", "steady"),
    (":poodle:", "steady"),
    (":racehorse:", "steady"),
    (":ox:", "abberant"),
    (":cow2:", "abberant"),
    (":elephant:", "abberant"),
    (":water_buffalo:", "abberant"),
    (":ram:", "abberant"),
    (":goat:", "abberant"),
    (":sheep:", "abberant"),
    (":leopard:", "predator"),
    (":tiger2:", "predator"),
    (":dragon:", "special"),
    (":unicorn:", "special"),
    (":turtle:", "slow"),
    (":bug:", "slow"),
    (":rooster:", "slow"),
    (":snail:", "slow"),
    (":scorpion:", "slow"),
    (":crocodile:", "slow"),
    (":pig2:", "slow"),
    (":turkey:", "slow"),
    (":duck:", "slow"),
    (":baby_chick:", "slow"),
)


class Animal:
    def __init__(self, emoji, _type):
        self.emoji = emoji
        self._type = _type
        self.track = "•   " * 20
        self.position = 80
        self.turn = 0
        self.current = self.track + self.emoji

    def move(self):
        self._update_postion()
        self.turn += 1
        return self.current

    def _update_postion(self):
        distance = self._calculate_movement()
        self.current = "".join(
            (
                self.track[: max(0, self.position - distance)],
                self.emoji,
                self.track[max(0, self.position - distance) :],
            )
        )
        self.position = self._get_position()

    def _get_position(self):
        return self.current.find(self.emoji)

    def _calculate_movement(self):
        if self._type == "slow":
            return random.randint(1, 3) * 3
        elif self._type == "fast":
            return random.randint(0, 4) * 3

        elif self._type == "steady":
            return 2 * 3

        elif self._type == "abberant":
            if random.randint(1, 100) >= 90:
                return 5 * 3
            else:
                return random.randint(0, 2) * 3

        elif self._type == "predator":
            if self.turn % 2 == 0:
                return 0
            else:
                return random.randint(2, 5) * 3

        elif self._type == ":unicorn:":
            if self.turn % 3:
                return random.choice([len("blue"), len("red"), len("green")]) * 3
            else:
                return 0
        else:
            if self.turn == 1:
                return 14 * 3
            elif self.turn == 2:
                return 0
            else:
                return random.randint(0, 2) * 3


# Developed by Redjumpman for Redbot.
# Inspired by the snail race mini game.

class FancyDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class FancyDictList(dict):
    def __missing__(self, key):
        value = self[key] = []
        return value

class JoinButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(emoji="🏁",label="Prendre le départ", style=discord.ButtonStyle.blurple, disabled=True)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ce bouton c'est de la merde il marche pas !", ephemeral=True)

    @discord.ui.button(emoji="🤔",label="Pourquoi c'est grisé ?", style=discord.ButtonStyle.blurple, disabled=False)
    async def why(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Parce que je suis trop con pour arriver à faire fonctionner ce bouton correctement.\n-- Charles", ephemeral=True)

class Race(commands.Cog):
    """Cog for racing animals"""

    def __init__(self, bot):
        self.bot = bot

        self.active = FancyDict()
        self.started = FancyDict()
        self.winners = FancyDictList()
        self.players = FancyDictList()
    

    @commands.hybrid_group(
        name="race",
        description="Gérer les courses."
    )
    async def race(self, ctx):
        """Race related commands."""
        pass

    @race.command(
        base="race",
        name="start",
        description="Démarrer une course.",
    )
    @app_commands.describe(zoo="Activer le mode zoo ?", wait="Combien de temps attendre pour que les joueurs rejoignent ? (entre 10 et 60 secondes, défaut 30)")
    async def start(self, ctx: Context, zoo: bool = False, wait: int = 30):
        """Begins a new race.
        You cannot start a new race until the active on has ended.
        If you are the only player in the race, you will race against
        your bot.
        The user who started the race is automatically entered into the race.
        """
        if wait < 1 or wait > 60:
            return await ctx.send("Le temps d'attente doit être compris entre 10 et 60 secondes.", ephemeral=True)
        if self.active[ctx.guild.id]:
            return await ctx.send(f"Une course est déjà en cours !  Utilisez `/race enter` pour la rejoindre !", ephemeral=True)
        self.active[ctx.guild.id] = True
        self.players[ctx.guild.id].append(ctx.author)
        buttons = JoinButton()
        await ctx.send(
            f"🚩 Une course a démarré ! Utilisez `/race enter` pour la rejoindre ! 🚩"
            f"\nLa course commencera dans {wait} secondes !", view=buttons
        )
        await ctx.send(f"**{ctx.author.mention}** a rejoint la course !")
        await asyncio.sleep(wait)
        self.started[ctx.guild.id] = True
        if zoo:
            await ctx.send("🏁 La course démarre MAINTENANT ! 🏁\n:leopard: :ox: :snail: :water_buffalo: Mode Zoo activé ! :camel: :elephant: :dog2: :hippopotamus:")
        else:
            await ctx.send("🏁 La course démarre MAINTENANT ! 🏁")
        await self.run_game(ctx, zoo)

        msg, file = await self._build_end_screen(ctx)
        await ctx.send(content=msg, file=file)
        await self._race_teardown(ctx)

    @race.command(
        base="race",
        name="enter",
        description="Rejoindre une course.",
    )
    async def enter(self, ctx: Context):
        """Allows you to enter the race.
        This command will return silently if a race has already started.
        By not repeatedly telling the user that they can't enter the race, this
        prevents spam.
        """
        if self.started[ctx.guild.id]:
            return await ctx.send(
                "Une course a déjà démarré. Merci d'attendre qu'elle se termine avant d'en rejoindre une autre.", ephemeral=True)
        elif not self.active.get(ctx.guild.id):
            return await ctx.send("Une course doit être lancée pour pouvoir la rejoindre.", ephemeral=True)
        elif ctx.author in self.players[ctx.guild.id]:
            return await ctx.send("Vous êtes déjà dans la course.", ephemeral=True)
        elif len(self.players[ctx.guild.id]) >= 14:
            return await ctx.send("Le maximum de participants a été atteint.", ephemeral=True)
        else:
            self.players[ctx.guild.id].append(ctx.author)
            await ctx.send(f"{ctx.author.mention} est prêt à courir !")

    @race.command(
        base="race",
        name="debug",
        description="Déboguer une course.",
    )
    @checks.is_owner()
    async def clear(self, ctx):
        """ONLY USE THIS COMMAND FOR DEBUG PURPOSES
        You shouldn't use this command unless the race is stuck
        or you are debugging."""
        self.clear_local(ctx)
        await ctx.send("Race cleared.")

    async def _race_teardown(self, ctx):
        self.clear_local(ctx)

    def clear_local(self, ctx):
        self.players[ctx.guild.id].clear()
        self.winners[ctx.guild.id].clear()
        self.active[ctx.guild.id] = False
        self.started[ctx.guild.id] = False

    async def _build_end_screen(self, ctx):
        color = 0xe74c3c
        if len(self.winners[ctx.guild.id]) == 3:
            first, second, third = self.winners[ctx.guild.id]
        else:
            first, second, = self.winners[ctx.guild.id]
            third = None
        
        template = Image.open("image/podium.jpg")

        firstavatar = BytesIO(await first[0].display_avatar.with_format("png").read())
        firstavatar = Image.open(firstavatar)
        firstavatar = firstavatar.resize((1024, 1024))

        secondavatar = BytesIO(await second[0].display_avatar.with_format("png").read())
        secondavatar = Image.open(secondavatar)
        secondavatar = secondavatar.resize((768, 768))

        if third:
            thirdavatar = BytesIO(await third[0].display_avatar.with_format("png").read())
            thirdavatar = Image.open(thirdavatar)
            thirdavatar = thirdavatar.resize((768, 768))

        template.paste(firstavatar, (2400, 700))
        template.paste(secondavatar, (1500, 1400))
        if third:
            template.paste(thirdavatar, (2200, 1800))

        title = ImageFont.truetype("fonts/CairoPlay-Black.ttf", 400)
        ranking = ImageDraw.Draw(template)

        ranking.text((1500,10), "Résultats !", (160,210,220), font=title)
        template.save("image/generated/ranking.png")

        file = discord.File("image/generated/ranking.png")
        
        #embed = discord.Embed(colour=color, title="Résultats de la course")
        #embed.add_field(name=f"{first[0].display_name} 🥇", value=first[1].emoji)
        #embed.add_field(name=f"{second[0].display_name} 🥈", value=second[1].emoji)
        #if third:
        #    embed.add_field(name=f"{third[0].display_name} 🥉", value=third[1].emoji)
        #embed.add_field(name="-" * 90, value="\u200b", inline=False)
        #embed.set_footer(text="Félicitations aux participants !")
        mentions = "" if first[0].bot else f"{first[0].mention}"
        mentions += "" if second[0].bot else f", {second[0].mention}" if not first[0].bot else f"{second[0].mention}"
        mentions += "" if third is None or third[0].bot else f", {third[0].mention}"
        return mentions, file

    async def _game_setup(self, ctx, zoo: bool):
        users = self.players[ctx.guild.id]
        if zoo:
            players = [(Animal(*random.choice(racers)), user) for user in users]
            if len(players) == 1:
                players.append((Animal(*random.choice(racers)), ctx.bot.user))
        else:
            players = [(Animal(":turtle:", "slow"), user) for user in users]
            if len(players) == 1:
                players.append((Animal(":turtle:", "slow"), ctx.bot.user))
        return players

    async def run_game(self, ctx, zoo: bool):
        players = await self._game_setup(ctx, zoo)
        setup = "\u200b\n" + "\n".join(
            f":carrot: **{animal.current}** 🏁[{jockey.display_name}]" for animal, jockey in players
        )
        track = await ctx.send(setup)
        while not all(animal.position == 0 for animal, jockey in players):

            await asyncio.sleep(1.0)
            fields = []
            for animal, jockey in players:
                if animal.position == 0:
                    fields.append(f":carrot: **{animal.current}** 🏁  [{jockey.display_name}]")
                    continue
                animal.move()
                fields.append(f":carrot: **{animal.current}** 🏁  [{jockey.display_name}]")
                if animal.position == 0 and len(self.winners[ctx.guild.id]) < 3:
                    self.winners[ctx.guild.id].append((jockey, animal))
            t = "\u200b\n" + "\n".join(fields)
            try:
                await track.edit(content=t)
            except discord.errors.NotFound:
            	pass

async def setup(bot):
    await bot.add_cog(Race(bot))