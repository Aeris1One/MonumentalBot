""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.3
"""
import discord
from discord.ext import commands
from discord.ext.commands import Context

from helpers import checks

from PIL import Image
from io import BytesIO
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps

# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.

    @commands.hybrid_command(
        name="testcommand",
        description="Commande de test qui ne fais rien.",
    )
    # This will only allow non-blacklisted members to execute the command
    @checks.not_blacklisted()
    # This will only allow owners of the bot to execute the command -> config.json
    @checks.is_owner()
    async def testcommand(self, context: Context):
        """
        This is a testing command that does nothing.

        :param context: The application command context.
        """
        # Do your stuff here

        # Don't forget to remove "pass", I added this just because there's no content in the method.
        await context.defer(ephemeral=True)

        template = Image.open("image/podium.jpg")

        winner = BytesIO(await context.author.display_avatar.with_static_format("png").with_size(1024).read())
        winner = Image.open(winner)
        winner = winner.resize((1024, 1024))

        #second = BytesIO(await context.author.display_avatar.with_static_format("png").with_size(1024).read())
        #second = Image.open(second)
        second = winner
        second = second.resize((768, 768))

        #third = BytesIO(await context.author.display_avatar.with_static_format("png").with_size(1024).read())
        #third = Image.open(second)
        third = winner
        third = second.resize((768, 768))

        template.paste(winner, (2400, 700))
        template.paste(second, (1500, 1300))
        template.paste(third, (2200, 1800))

        title = ImageFont.truetype("fonts/CairoPlay-Black.ttf", 400)
        ranking = ImageDraw.Draw(template)

        ranking.text((1500,10), "Résultats !", (160,210,220), font=title)
        template.save("image/generated/ranking.png")

        await context.send(file=discord.File("image/generated/ranking.png"))

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Template(bot))
