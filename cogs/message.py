from discord.ext import commands
from discord import Embed, Colour
from .utils import checks
import random

class Message(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.latest_deleted_message = None
    self.puns = []

  def is_init_command(self, message) -> bool:
    return not message.content.startswith('.p prune')

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    self.latest_deleted_message = message

  @commands.guild_only()
  @checks.is_admin()
  @commands.command(name="prune")
  async def prune_messages(self, ctx, amount=1):
    deleted = await ctx.channel.purge(limit=amount+1, check=self.is_init_command)
    await ctx.message.delete(delay=2.0)
    await ctx.send("`🌱 Deleted %d messages.`" % len(deleted), delete_after=2.0)

  @commands.command(name="pun")
  async def say_pun(self, ctx):
    if not self.puns:
      self.puns = self._get_puns()

    pun = random.choice(self.puns)
    embed = self._create_embed(ctx.author, pun)
    await ctx.send(embed=embed)

  def _get_puns(self):
    with open('cogs/utils/data/puns') as _file:
      return [line.rstrip() for line in _file]

  def _create_embed(self, author, text):
    embed = Embed(color=Colour.gold())
    embed.set_author(name=author.name, icon_url=author.avatar_url)
    embed.description = text
    return embed

  @commands.command(name="snipe")
  async def get_deleted_message(self, ctx):
    msg = self.latest_deleted_message
    # TODO:
    # Maybe create as an embed?
    if msg is not None:
      await ctx.send("🌱 **%s**: %s" % (msg.author.display_name, msg.content))

def setup(bot):
  bot.add_cog(Message(bot))
