from discord.ext import commands
from .utils import checks

class Message(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.latest_deleted_message = None

  def is_init_command(self, message) -> bool:
    return not message.content.startswith('.p prune')

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    self.latest_deleted_message = message

  @commands.guild_only()
  @checks.is_admin()
  @commands.command(name="prune")
  async def prune_messages(self, ctx, amount=1):
    # amount has to be incremented otherwise it would count the invocation command as the one to delete
    # Example:
    # [0] bad message
    # [1] .p prune 1
    # ---------------
    # [1] gets deleted, [0] stays
    amount += 1
    deleted = await ctx.channel.purge(limit=amount, check=self.is_init_command)
    await ctx.message.delete(delay=2.0)
    await ctx.send("`🌱 Deleted %d messages.`" % len(deleted), delete_after=2.0)

  @commands.command(name="snipe")
  async def get_deleted_message(self, ctx):
    msg = self.latest_deleted_message
    # TODO:
    # Maybe create as an embed?
    if msg is not None:
      await ctx.send("🌱 **%s**: %s" % (msg.author.display_name, msg.content))

def setup(bot):
  bot.add_cog(Message(bot))
