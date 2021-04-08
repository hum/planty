import os
import requests
import datetime
import discord.utils

from .utils import checks
from discord.ext import commands, tasks
from discord import Embed, Colour

# TODO:
# Handle this through a webhook before generalizing the code
# This is only a proof of concept
TWITCH_URL          = "https://twitch.tv/%s"
GET_STREAMER_ID_URL = "https://api.twitch.tv/helix/users?login=%s"
GET_STREAM_DATA_URL = "https://api.twitch.tv/helix/streams?user_id=%s"
GET_USER_FROM_ID    = "https://api.twitch.tv/helix/users?id=%s"

TWITCH_CLIENT_ID      = os.getenv('TWITCH_CLIENT_ID')
TWITCH_AUTHORIZATION  = os.getenv('TWITCH_AUTHORIZATION')
TWITCH_HEADERS        = {"Client-Id": TWITCH_CLIENT_ID, "Authorization": TWITCH_AUTHORIZATION}

USER_ADD    = "add"
USER_REMOVE = "remove"
LIST        = "list"

SUCCESSFULLY_ADDED_STREAMER     =   "🌱 Added **%s** to the list."
ERROR_ADDING_STREAMER           =   "🌱 Could not add **%s** to the list.\nEither the user is already added or does not exist."
SPECIFY_USERNAME_TO_ADD         =   "🌱 Please specify the user's name to add."
SUCCESSFULLY_REMOVED_USER       =   "🌱 Successfully removed **%s** from the list."
COULD_NOT_REMOVE_USER           =   "🌱 Could not remove user **%s** from the list."
SPECIFY_USERNAME_TO_REMOVE      =   "🌱 Please specify the user's name to remove."

# TODO:
# might have to change the DB schema later
DB_CHECK_STREAMER_EXISTS        = "SELECT COUNT(*) FROM p_twitch_users WHERE streamer_id = '%s';"
DB_GET_STREAMER_IDS             = "SELECT streamer_id FROM p_twitch_users;"
DB_GET_STREAMER_ID_FROM_USER_ID = "SELECT streamer_id FROM p_twitch_list AS p WHERE p.user_id = %d;"
DB_INSERT_NEW_STREAMER          = "INSERT INTO p_twitch_users(streamer_id, streamer_name) VALUES (%d, '%s') RETURNING streamer_id;"
DB_INSERT_INTO_DISCORD_LIST     = "INSERT INTO p_twitch_list(user_id, streamer_id) VALUES (%d, %d);"
DB_DELETE_TWITCH_STREAMER       = "DELETE FROM p_twitch_users WHERE streamer_id = %d;"

class TwitchAPI:
  def get_streamer_id(self, name: str) -> str:
    with requests.session() as session:
      response = session.get(GET_STREAMER_ID_URL % name, headers=TWITCH_HEADERS).json()
      if len(response['data']) > 0:
        return response['data'][0]['id']
      return None

  def is_live(self, streamer_id: str):
    with requests.session() as session:
      response = session.get(GET_STREAM_DATA_URL % streamer_id, headers=TWITCH_HEADERS).json()
      if len(response['data']) > 0:
        return response['data'][0], True
      else:
        return None, False

class Twitch(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.twitch_api = TwitchAPI()
    self.streamer_ids = []

    # temporary values
    self.channel_id = 814850421620342814
    self.twitch_role = "" 
    self.streamer = {}
  
  # A function for current testing purposes 
  @commands.Cog.listener()
  async def on_ready(self):
    guild = self.bot.get_guild(638151136439959573)
    role = discord.utils.get(guild.roles, name='twitch')
    self.twitch_role = role.mention
    self.streamer_ids = self.get_streamer_ids()
    self.check_is_live.start()

  def cog_unload(self):
    if self.check_is_live.is_running():
      self.check_is_live.cancel()

  @tasks.loop(minutes=1.0)
  async def check_is_live(self):
    for streamer_id in self.streamer_ids:
      data, ok = self.twitch_api.is_live(streamer_id)
      if ok and self.is_different_stream(data):
        embed = self._create_embed(data)
        channel = self.bot.get_channel(self.channel_id)
        await channel.send("🌱 " + self.twitch_role)
        await channel.send(embed=embed)

  def get_streamer_ids(self):
    result = []
    query_result = self.bot.db.select_query(DB_GET_STREAMER_IDS)
    if len(query_result) > 0:
      for row in query_result:
        result.append(row[0])
    return result
  
  # A terrible ad-hoc hacky solution to not repeat the same stream twice
  def is_different_stream(self, data):
    time = datetime.datetime.strptime(data['started_at'][:len(data['started_at'])-1], '%Y-%m-%dT%H:%M:%S')

    if data['user_name'] in self.streamer:
      if not time == self.streamer[data['user_name']]:
        self.streamer[data['user_name']] = time
        return True
      return False
    else:
      self.streamer[data['user_name']] = time
      return True
       
  # TODO:
  # Rewrite to run asynchronously for all IDs
  def _streamer_exists(self, streamer_id: int) -> bool:
    result = self.bot.db.select_query(DB_CHECK_STREAMER_EXISTS % streamer_id)
    print(result)
    if len(result) > 0:
      if result[0][0] == 1:
        return True
    return False

  # TODO:
  # Allow subgroups of streamers based on a specific role
  # e.g. instead of @Twitch, there can be created categories for
  # a specific subgroup of streamers.
  def _add_streamer(self, streamer_name: str, user_id: int) -> bool:
    streamer_id = int(self.twitch_api.get_streamer_id(streamer_name))
    if streamer_id is not None and streamer_id not in self.streamer_ids:
      if not self._streamer_exists(streamer_id):
        self.bot.db.insert_query(DB_INSERT_NEW_STREAMER % (streamer_id, streamer_name))
        self.streamer_ids.append(streamer_id)
        return True
    return False

  def _remove_streamer(self, streamer_name: str) -> bool:
    streamer_id = int(self.twitch_api.get_streamer_id(streamer_name))
    if self._streamer_exists(streamer_id):
      self.bot.db.delete_query(DB_DELETE_TWITCH_STREAMER % streamer_id)
      self.streamer_ids.remove(streamer_id)
      return True
    else:
      return False
    

  # TODO:
  # parse [streamer_name] into values separated as spaces
  # to allow adding multiple streamers at once
  # ex: .p twitch add user1 user2 user3
  @checks.is_admin()
  @commands.guild_only()
  @commands.command(name='twitch')
  async def twitch(self, ctx, action="", streamer_name=""):
    if streamer_name == "":
      await ctx.send(SPECIFY_USERNAME_TO_ADD)
      return
    
    if action == USER_ADD:
      if self._add_streamer(streamer_name, ctx.author.id):
        await ctx.send(SUCCESSFULLY_ADDED_STREAMER % streamer_name)
      else:
        await ctx.send(ERROR_ADDING_STREAMER % streamer_name)
    elif action == USER_REMOVE:
      if self._remove_streamer(streamer_name):
        await ctx.send(SUCCESSFULLY_REMOVED_USER % streamer_name)
      else:
        await ctx.send(COULD_NOT_REMOVE_USER % streamer_name)

  # TODO:
  # Do error checking on missing values
  def _create_embed(self, data):
    width, height = 640, 480
    embed = Embed(color=Colour.purple())

    embed.title = "**%s** is now live!" % data['user_name']
    embed.description = TWITCH_URL % data['user_name'] 

    embed.add_field(name="Title", value=data['title'])
    embed.add_field(name="Playing", value=data['game_name'])

    url = data['thumbnail_url'].format(width=width, height=height)
    embed.set_image(url=url)

    time = datetime.datetime.strptime(data['started_at'][:len(data['started_at'])-1], '%Y-%m-%dT%H:%M:%S')
    self.streamer[data['user_name']] = time
    embed.set_footer(text=time.strftime("%I:%M %p - %B %d, %Y"))
    return embed

def setup(bot):
  bot.add_cog(Twitch(bot))
