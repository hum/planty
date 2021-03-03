import discord
import asyncio
import logging
import contextlib
import os

from logging.handlers import RotatingFileHandler
from bot import Planty
from cogs.utils.db import Db

LOG_FILENAME = "planty.log"

@contextlib.contextmanager
def set_logging():
  try:
    logging.getLogger('discord').setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('discord.state').setLevel(logging.DEBUG)

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
  
    date_format = '%Y-%m-%d %H:%M:%S'
    handler = RotatingFileHandler(filename=LOG_FILENAME, encoding='utf-8', mode='a')
    fmt = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', date_format, style='{')

    handler.setFormatter(fmt)
    log.addHandler(handler)

    yield
  finally:
    for handler in log.handlers[:]:
      handler.close()
      log.removeHandler(handler)

def start_bot():
  log = logging.getLogger()
  loop = asyncio.get_event_loop()
  db = Db()

  try:
    pool = loop.run_until_complete(Db.create_pool(0, 4, os.getenv("POSTGRE_URI")))
    if pool is not None:
      db.pool = pool

      bot = Planty()
      bot.db = db
      bot.run()
  except Exception as e:
    log.error(e)

def main():
  with set_logging():
    start_bot()

if __name__ == '__main__':
  main()
