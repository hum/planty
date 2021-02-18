from discord import Intents

def get_intents() -> Intents:
  intents = Intents.default()
  intents.reactions = True
  intents.members = True
  return intents

postgresql = ''

LOG_FILENAME = 'planty.log'
TOKEN = ''
BOT_PREFIX = ['planty ', 'Planty ', '.p ', '.P ', '🌱 ']
