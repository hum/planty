import logging
import subprocess
import requests

from discord.ext import commands
from random import choice

# TODO:
# Rewrite this godawful thing
IMAGE_QUERY = """
    select 
      i.link, c.category_name, s.server_name
    from 
      p_images as i, p_image_category as c, p_server_images as si, p_servers as s
    where 
      s.server_id = si.server_id
    and
      si.image_id = i.image_id
    and 
      i.category_id = c.category_id
    and
      si.server_id = 1;
"""

ADD_SUBREDDIT_QUERY = "INSERT INTO p_image_category (category_name) values ('%s') RETURNING category_id;"
CHECK_IF_EXISTS_CATEGORY = "SELECT COUNT(*) FROM p_image_category WHERE category_name = '%s';"
LIST_SUBREDDITS = "SELECT category_name FROM p_image_category;"
PRUNE_OLD_IMAGES = "DELETE FROM p_images WHERE add_time < NOW() - interval '%d days';"

ADD = 'add'
REMOVE = 'remove'
LIST = 'list'

avail_actions = [
  ADD,
  REMOVE,
  LIST
]

log = logging.getLogger(__name__)

class Memes(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='meme')
  async def send_meme(self, ctx):
    try:
      result = self.bot.db.select_query(IMAGE_QUERY)
    except Exception as e:
      log.error(e)
      return

    await ctx.send(choice(result)[0])

  @commands.command(name='img')
  async def update_images(self, ctx, cmd: str, days=14):
    if cmd == 'prune':
      msg = await ctx.send("🌱 Pruning images from the database...")
      result = self.bot.db.delete_query(PRUNE_OLD_IMAGES % days)
      await msg.edit(content=msg.content + "```Deleted %d images, because they were older than %d days.```" % (result, days))
    elif cmd == 'fetch':
      msg = await ctx.send("🌱 Fetching images...")

      with requests.session() as session:
        url = "http://sprout:3000"
        data = None

        try:
          data = session.get(url).json()
        except Exception as e:
          await msg.edit(content=msg.content + "```Error: %s```" % e)
          return

        if "OK" in data["Status"]:
          await msg.edit(content=msg.content + "```Fetched %d images into the DB.```" % int(data["Data"]["Count"]))
        else:
          await msg.edit(content=msg.content + "```Failed to fetch images into the DB. Got Status code: %s```" % data["Status"])
    else:
      await ctx.send("Undefined command.\n Please use `.p img [prune/fetch]`")

  @commands.command(name='sub')
  async def subreddit_update(self, ctx, action: str, subreddit_name=""):
    if action in avail_actions:
      if action == ADD:
        if subreddit_name == "":
          await ctx.send("In order to add a new subreddit you need to specify it's name. ```[prefix] sub add [subreddit_name]```")
          return

        result = self.bot.db.select_query(CHECK_IF_EXISTS_CATEGORY % subreddit_name)
        count = result[0][0] # [(0,)]

        if count > 0:
          await ctx.send("Subreddit %s already exists in the database." % subreddit_name)
          return

        result = self.bot.db.insert_query(ADD_SUBREDDIT_QUERY % subreddit_name) 
        if result[0] > 0:
          await ctx.add_reaction('\N{WHITE HEAVY CHECK MARK}')
          await ctx.send("Subreddit [**%s**] has been added to the database. 🌱" % subreddit_name)
      elif action == REMOVE:
        # TODO:
        # Remove subreddit from DB
        return
      elif action == LIST:
        result = self.bot.db.select_query(LIST_SUBREDDITS)
        if len(result) == 0:
          return

        subreddit_names = []

        for value in result:
          subreddit_names.append(value[0])

        fmt = '```' + '\n'.join(subreddit_names) + '```'
        await ctx.send(fmt)

def setup(bot):
  bot.add_cog(Memes(bot))
