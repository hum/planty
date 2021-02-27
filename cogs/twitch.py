import os
import requests
import datetime
import discord.utils

from discord.ext import commands, tasks
from discord import Embed, Colour

# TODO:
# Handle this through a webhook before generalizing the code
# This is only a proof of concept
TWITCH_URL = "https://twitch.tv/%s"
GET_STREAMER_ID_URL = "https://api.twitch.tv/helix/users?login=%s"
GET_STREAM_DATA_URL = "https://api.twitch.tv/helix/streams?user_id=%s"
GET_USER_FROM_ID = "https://api.twitch.tv/helix/users?id=%s"

TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_AUTHORIZATION = os.getenv('TWITCH_AUTHORIZATION')
TWITCH_HEADERS = {"Client-Id": TWITCH_CLIENT_ID, "Authorization": TWITCH_AUTHORIZATION}

USER_ADD = "add"
USER_REMOVE = "remove"
LIST = "list"

class TwitchAPI:
  def __init__(self):
    # TODO:
    # Save streamer IDs to DB to avoid having to add them after bot's restart
    self.streamer_ids = [] # temporary

  def add_streamer(self, name: str) -> bool:
    if not name in self.streamer_ids:
      streamer_id = self.get_streamer_id(name)

      if streamer_id is not None:
        self.streamer_ids.append(streamer_id)
        return True
      else:
        return False
    return False

  def remove_streamer(self, name) -> bool:
    streamer_id = get_streamer_id

    if streamer_id is not None:
      self.streamer_ids.remove(streamer_id)
      return True
    return False

  def get_streamer_id(self, name: str) -> str:
    with requests.session() as session:
      response = session.get(GET_STREAMER_ID_URL % name, headers=TWITCH_HEADERS).json()
      if len(response['data']) > 0:
        return response['data'][0]['id']
      return None
        

class Twitch(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.twitch_api = TwitchAPI()

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
    self.check_is_live.start()

  # TODO:
  # Completely rewrite this
  @tasks.loop(minutes=5.0)
  async def check_is_live(self):
    for streamer_id in self.twitch_api.streamer_ids:
      data, ok = self.isLive(streamer_id)
      if ok and self.is_different_stream(data):
        embed = self._create_embed(data)
        channel = self.bot.get_channel(self.channel_id)

        await channel.send("🌱 " + self.twitch_role)
        await channel.send(embed=embed)
  
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

  # only a testing function to see it work
  # will be deleted after it's completely working
  @commands.command(name='test')
  async def test(self, ctx):
    for streamer_id in self.twitch_api.streamer_ids:
      data, ok = self.isLive(streamer_id)
      if ok:
        embed = self._create_embed(data)
        await ctx.send(embed=embed)
        
  # TODO:
  # Rewrite to run asynchronously for all IDs
  def isLive(self, streamer_id: str):
    with requests.session() as session:
      response = session.get(GET_STREAM_DATA_URL % streamer_id, headers=TWITCH_HEADERS).json()
      if len(response['data']) > 0:
        return response['data'][0], True
      else:
        return None, False

  # TODO:
  # parse [streamer_name] into values separated as spaces
  # to allow adding multiple streamers at once
  # ex: .p twitch add user1 user2 user3
  @commands.command(name='twitch')
  async def twitch(self, ctx, action="", streamer_name=""):
    # TODO:
    # Rewrite all of this messages as static vars, inline text looks ugly
    if action == USER_ADD:
      if not streamer_name == "":
        if self.twitch_api.add_streamer(streamer_name):
          await ctx.send("🌱 Added **%s** to the list." % streamer_name)
        else:
          await ctx.send("🌱 Could not add **%s** to the list.\nEither the user is already added or does not exist.")
      else:
        await ctx.send("🌱 Please specify the user's name to add.")
    elif action == USER_REMOVE:
      if not streamer_name == "":
        if self.twitch_api.remove_streamer(streamer_name):
          await ctx.send("🌱 Successfully removed **%s** from the list.")
        else:
          await ctx.send("🌱 Could not remove user **%s** from the list.")
      else:
        await ctx.send("🌱 Please specify the user's name to remove.")

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
