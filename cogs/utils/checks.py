from discord.ext import commands

async def check_guild_permissions(ctx, perms, *, check=all):
  is_owner = await ctx.bot.is_owner(ctx.author)
  if is_owner:
    return True

  if ctx.guild is None:
    return False

  resolved = ctx.author.guild_permissions
  return check(getattr(resolved, name, None) == value for name, value in perms.items())

# TODO:
# Handle errors wherever this is called to return a proper response
def is_admin():
  async def pred(ctx):
    return await check_guild_permissions(ctx, {'administrator': True})
  return commands.check(pred)
