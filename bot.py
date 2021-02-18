import logging
import config

from discord.ext import commands
from cogs.utils import context

log = logging.getLogger(__name__)

cog_commands = (
  'cogs.memes',
  'cogs.roles',
  'cogs.xkcd',
	'cogs.hn'
)

class Planty(commands.Bot):
  def __init__(self):
    self.db = None
    super().__init__(command_prefix=config.BOT_PREFIX, intents=config.get_intents())

    for command in cog_commands:
      self.load_extension(command)

  async def on_ready(self):
    log.info(f'Planty logged in: {self.user} (ID: {self.user.id})')

  async def process_commands(self, message):
    try:
      ctx = await self.get_context(message, cls=context.PlantyContext)
      if ctx.valid:
        await self.invoke(ctx)
    except Exception as e:
      log.error(e)

  async def on_message(self, message):
    if message.author.bot:
      return
    await self.process_commands(message)

  def run(self):
    try:
      super().run(config.TOKEN, reconnect=True)
    finally:
      log.info(f'Planty logged off.')