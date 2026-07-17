from utils import emojis

import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import asyncio

from utils.Tools import *


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = bot

    @commands.hybrid_command(name="embed")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 7, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    async def _embed(self, ctx: commands.Context):
        msgx = "Example embed. You can customize everything.\n*Respond within 30 seconds to avoid time out.*"

        embed = discord.Embed(
            title="Edit your Embed!",
            description="- Select Options what to edit from the below select menu.\n\nMust edit embed title & description to remove these instructions.",
            color=0x000000
        )

        interaction_user = ctx.author

        def chk(m: discord.Message):
            return (
                m.channel.id == ctx.channel.id
                and m.author.id == ctx.author.id
                and not m.author.bot
            )

        msg = None

        async def refresh_message():
            if msg:
                await msg.edit(content=msgx, embed=embed, view=view)

        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message doesn't belong to you.\nYou must run this command to interact with it.",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            selected_value = select.values[0]

            if selected_value == "Title":
                await ctx.send("Please enter the **Title of the embed**:")
                try:
                    tit = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.title = tit.content
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Description":
                await ctx.send("Please enter the **Description of the embed**:")
                try:
                    desc = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.description = desc.content
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Color":
                await ctx.send("Please enter the color of the embed as a hexadecimal value (e.g., `#FF0000` for red):")
                try:
                    col = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    color = discord.Colour(int(col.content.strip().replace("#", ""), 16))
                    embed.color = color
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid color format. Please retry with a valid hexadecimal color value.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Thumbnail":
                await ctx.send("Please enter the **URL of the thumbnail**:")
                try:
                    thumb = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not thumb.content.startswith(("http://", "https://")):
                        raise ValueError("Invalid URL format")
                    embed.set_thumbnail(url=thumb.content)
                    await refresh_message()
                except ValueError as e:
                    await ctx.send(str(e))
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Image":
                await ctx.send("Please enter the **URL of the image**:")
                try:
                    img = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not img.content.startswith(("http://", "https://")):
                        raise ValueError("Invalid URL format")
                    embed.set_image(url=img.content)
                    await refresh_message()
                except ValueError as e:
                    await ctx.send(str(e))
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Footer Text":
                await ctx.send("Please enter the **text of the footer**:")
                try:
                    foot = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    current_icon = embed.footer.icon_url if embed.footer else None
                    embed.set_footer(text=foot.content, icon_url=current_icon)
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Footer Icon":
                await ctx.send("Please enter the **URL of the footer icon**:")
                try:
                    foot_icon = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not foot_icon.content.startswith(("http://", "https://")):
                        raise ValueError("Invalid URL format")
                    current_text = embed.footer.text if embed.footer and embed.footer.text else "Footer"
                    embed.set_footer(text=current_text, icon_url=foot_icon.content)
                    await refresh_message()
                except ValueError as e:
                    await ctx.send(str(e))
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Author Text":
                await ctx.send("Please enter the **author text**:")
                try:
                    auth_text = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    current_icon = embed.author.icon_url if embed.author else None
                    current_url = embed.author.url if embed.author else None
                    embed.set_author(name=auth_text.content, icon_url=current_icon, url=current_url)
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Author Icon":
                await ctx.send("Please enter the **URL of the author icon**:")
                try:
                    auth_icon = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not auth_icon.content.startswith(("http://", "https://")):
                        raise ValueError("Invalid URL format")
                    current_name = embed.author.name if embed.author and embed.author.name else "Author"
                    current_url = embed.author.url if embed.author else None
                    embed.set_author(name=current_name, icon_url=auth_icon.content, url=current_url)
                    await refresh_message()
                except ValueError as e:
                    await ctx.send(str(e))
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

            elif selected_value == "Add Field":
                await ctx.send("**Enter Field title:**")
                try:
                    field_name = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    await ctx.send("**Enter Field value:**")
                    field_value = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.add_field(name=field_name.content, value=field_value.content, inline=False)
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed Out")

        select = Select(
            placeholder="Choose an option to edit the Embed",
            min_values=1,
            max_values=1,
            row=0,
            options=[
                discord.SelectOption(label="Title", description="Edit the title of the embed"),
                discord.SelectOption(label="Description", description="Edit the description of the embed"),
                discord.SelectOption(label="Add Field", description="Add a field to the embed"),
                discord.SelectOption(label="Color", description="Edit the color of the embed"),
                discord.SelectOption(label="Thumbnail", description="Edit the thumbnail of the embed"),
                discord.SelectOption(label="Image", description="Edit the image of the embed"),
                discord.SelectOption(label="Footer Text", description="Edit the footer text of the embed"),
                discord.SelectOption(label="Footer Icon", description="Edit the footer icon of the embed"),
                discord.SelectOption(label="Author Text", description="Edit the author text of the embed"),
                discord.SelectOption(label="Author Icon", description="Edit the author icon of the embed"),
            ]
        )
        select.callback = select_callback

        async def send_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message doesn't belong to you.\nYou must run this command to interact with it.",
                    ephemeral=True
                )
                return

            await interaction.response.defer()
            await ctx.send("Please mention the **channel** where you want to send this embed:")

            try:
                channel_message = await ctx.bot.wait_for("message", timeout=30, check=chk)

                if not channel_message.channel_mentions:
                    await ctx.send("Walang valid channel mention. Pakimention ang channel like `#general`.")
                    return

                chnl = channel_message.channel_mentions[0]
                await chnl.send(embed=embed)

                success_embed = discord.Embed(
                    title=f"{emojis.TICK} Success",
                    description="Sent the embed message to the mentioned channel",
                    color=0x000000
                )
                await ctx.send(embed=success_embed)

            except asyncio.TimeoutError:
                await ctx.send("Timed Out")

        async def delete_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message doesn't belong to you.\nYou must run this command to interact with it.",
                    ephemeral=True
                )
                return

            await interaction.response.defer()

            if msg:
                await msg.delete()

        button_send = Button(
            label="Send Embed",
            emoji=f"{emojis.TICK}",
            style=discord.ButtonStyle.success,
            row=1
        )
        button_send.callback = send_callback

        button_delete = Button(
            label="Cancel Setup",
            emoji=f"{emojis.CROSSICON}",
            style=discord.ButtonStyle.danger,
            row=1
        )
        button_delete.callback = delete_callback

        view = View(timeout=180)
        view.add_item(select)
        view.add_item(button_send)
        view.add_item(button_delete)

        msg = await ctx.send(content=msgx, embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Embed(bot))


"""
@Author: Sonu Jana
    + Discord: me.sonu
    + Community: https://discord.gg/stVsvE9rhT (REM ALL IN ONE BOT)
    + for any queries reach out support or DM me.
"""
