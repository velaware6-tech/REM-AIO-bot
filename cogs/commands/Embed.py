from utils import emojis

import discord
from discord.ext import commands
from discord.ui import LayoutView, Select, Button
import asyncio

from utils.Tools import *
from utils.cv2_compat import embed_to_view


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
        msgx = "Example embed. You can customize everything.\n*Respond within 30 seconds to avoid timeout.*"

        embed = discord.Embed(
            title="Edit your Embed!",
            description=(
                "- Select what you want to edit from the menu below.\n\n"
                "You should edit the embed title and description to remove these instructions."
            ),
            color=0x000000,
        )

        interaction_user = ctx.author
        msg = None

        def chk(m: discord.Message):
            return (
                m.channel.id == ctx.channel.id
                and m.author.id == ctx.author.id
                and not m.author.bot
            )

        editor_view = LayoutView(timeout=180)

        async def refresh_message():
            if msg:
                await msg.edit(
                    content=msgx,
                    view=embed_to_view(embed, view=editor_view),
                )

        async def select_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message does not belong to you.\nYou must run this command yourself to interact with it.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()
            selected_value = select.values[0]

            if selected_value == "Title":
                await ctx.send("Please enter the **title** of the embed:")
                try:
                    title_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.title = title_msg.content
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Description":
                await ctx.send("Please enter the **description** of the embed:")
                try:
                    desc_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.description = desc_msg.content
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Color":
                await ctx.send("Please enter the embed color as a hex value, for example `#FF0000`:")
                try:
                    color_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    parsed = int(color_msg.content.strip().replace("#", ""), 16)
                    embed.color = discord.Colour(parsed)
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid hex color. Please try again with a valid value like `#5865F2`.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Thumbnail":
                await ctx.send("Please enter the **thumbnail URL**:")
                try:
                    thumb_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not thumb_msg.content.startswith(("http://", "https://")):
                        raise ValueError
                    embed.set_thumbnail(url=thumb_msg.content)
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid URL. Please provide a valid `http://` or `https://` link.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Image":
                await ctx.send("Please enter the **image URL**:")
                try:
                    image_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not image_msg.content.startswith(("http://", "https://")):
                        raise ValueError
                    embed.set_image(url=image_msg.content)
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid URL. Please provide a valid `http://` or `https://` link.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Footer Text":
                await ctx.send("Please enter the **footer text**:")
                try:
                    footer_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    current_icon = getattr(embed.footer, "icon_url", None)
                    embed.set_footer(text=footer_msg.content, icon_url=current_icon)
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Footer Icon":
                await ctx.send("Please enter the **footer icon URL**:")
                try:
                    footer_icon_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not footer_icon_msg.content.startswith(("http://", "https://")):
                        raise ValueError
                    current_text = getattr(embed.footer, "text", None) or "Footer"
                    embed.set_footer(text=current_text, icon_url=footer_icon_msg.content)
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid URL. Please provide a valid `http://` or `https://` link.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Author Text":
                await ctx.send("Please enter the **author text**:")
                try:
                    author_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    current_icon = getattr(embed.author, "icon_url", None)
                    current_url = getattr(embed.author, "url", None)
                    embed.set_author(name=author_msg.content, icon_url=current_icon, url=current_url)
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Author Icon":
                await ctx.send("Please enter the **author icon URL**:")
                try:
                    author_icon_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    if not author_icon_msg.content.startswith(("http://", "https://")):
                        raise ValueError
                    current_name = getattr(embed.author, "name", None) or "Author"
                    current_url = getattr(embed.author, "url", None)
                    embed.set_author(name=current_name, icon_url=author_icon_msg.content, url=current_url)
                    await refresh_message()
                except ValueError:
                    await ctx.send("Invalid URL. Please provide a valid `http://` or `https://` link.")
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

            elif selected_value == "Add Field":
                await ctx.send("Please enter the **field title**:")
                try:
                    field_name_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    await ctx.send("Please enter the **field value**:")
                    field_value_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)
                    embed.add_field(
                        name=field_name_msg.content,
                        value=field_value_msg.content,
                        inline=False,
                    )
                    await refresh_message()
                except asyncio.TimeoutError:
                    await ctx.send("Timed out.")

        select = Select(
            placeholder="Choose what to edit",
            min_values=1,
            max_values=1,
            row=0,
            options=[
                discord.SelectOption(label="Title", description="Edit the embed title"),
                discord.SelectOption(label="Description", description="Edit the embed description"),
                discord.SelectOption(label="Add Field", description="Add a new field"),
                discord.SelectOption(label="Color", description="Edit the embed color"),
                discord.SelectOption(label="Thumbnail", description="Set the thumbnail URL"),
                discord.SelectOption(label="Image", description="Set the image URL"),
                discord.SelectOption(label="Footer Text", description="Edit the footer text"),
                discord.SelectOption(label="Footer Icon", description="Set the footer icon URL"),
                discord.SelectOption(label="Author Text", description="Edit the author text"),
                discord.SelectOption(label="Author Icon", description="Set the author icon URL"),
            ],
        )
        select.callback = select_callback

        async def send_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message does not belong to you.\nYou must run this command yourself to interact with it.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()
            await ctx.send("Please mention the **channel** where you want to send this embed:")

            try:
                channel_msg = await ctx.bot.wait_for("message", timeout=30, check=chk)

                if not channel_msg.channel_mentions:
                    await ctx.send("No valid channel mention was found. Please mention a channel like `#general`.")
                    return

                target_channel = channel_msg.channel_mentions[0]
                await target_channel.send(view=embed_to_view(embed))

                success_embed = discord.Embed(
                    title=f"{emojis.TICK} Success",
                    description="The embed was sent to the selected channel.",
                    color=0x000000,
                )
                await ctx.send(view=embed_to_view(success_embed))

            except asyncio.TimeoutError:
                await ctx.send("Timed out.")

        async def delete_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction_user.id:
                await interaction.response.send_message(
                    "Uh oh! That message does not belong to you.\nYou must run this command yourself to interact with it.",
                    ephemeral=True,
                )
                return

            await interaction.response.defer()

            if msg:
                await msg.delete()

        button_send = Button(
            label="Send Embed",
            emoji=f"{emojis.TICK}",
            style=discord.ButtonStyle.success,
            row=1,
        )
        button_send.callback = send_callback

        button_delete = Button(
            label="Cancel Setup",
            emoji=f"{emojis.CROSSICON}",
            style=discord.ButtonStyle.danger,
            row=1,
        )
        button_delete.callback = delete_callback

        editor_view.add_item(select)
        editor_view.add_item(button_send)
        editor_view.add_item(button_delete)

        msg = await ctx.send(
            content=msgx,
            view=embed_to_view(embed, view=editor_view),
        )


async def setup(bot):
    await bot.add_cog(Embed(bot))


"""
@Author: Sonu Jana
    + Discord: me.sonu
    + Community: https://discord.gg/stVsvE9rhT (REM ALL IN ONE BOT)
    + for any queries reach out support or DM me.
"""
