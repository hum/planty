import logging
import discord

from discord.ext import commands

log = logging.getLogger(__name__)

class PlantyContext(commands.Context):
  async def add_reaction(self, emoji):
    try:
      await self.message.add_reaction(emoji)
    except discord.HTTPException as e:
       log.error(e)
