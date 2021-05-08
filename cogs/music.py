from discord.ext import commands
from discord import Embed, Colour, FFmpegPCMAudio
from googleapiclient.discovery import build
import asyncio
import youtube_dl
from os import getenv

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YOUTUBE_VIDEO_URL = "https://youtube.com/watch?v="

YOUTUBE_API_KEY = getenv('YOUTUBE_API_KEY')

class Audio:
  def __init__(self):
    self.ydl = youtube_dl.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'})
    self.service = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

  def get_youtube_search(self, q: str):
    return self.service.search().list(
      part='snippet', 
      order='relevance', 
      q=q,
      videoDimension="2d",
      videoDuration="short",
      type="video"
    ).execute()

  def get_audio_info(self, youtube_link: str):
    return self.ydl.extract_info(youtube_link, download=False)

  def close(self):
    self.service.close()
    self.ydl.close()

class Queue:
  def __init__(self):
    self.items = []

  def enqueue(self, data: str):
    self.items.append(data)

  def dequeue(self) -> str:
    return self.items.pop(0)

  def is_empty(self) -> bool:
    return len(self.items) == 0

class Music(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.audio = Audio()
    self.queue = Queue()
    self.voice = {}   
    self.current_song = {}

  def cog_unload(self):
    self.audio.close()

  @commands.guild_only()
  @commands.command(name='join')
  async def join_vc(self, ctx):
    if not ctx.author.voice:
      embed = Embed(colour=Color.gold())
      embed.description = '**You are not in a voice channel.**'
      await ctx.send(embed=embed)
      return False

    channel = ctx.author.voice.channel
    self.voice[ctx.guild.id] = await channel.connect()
    return True
      
  @commands.guild_only()
  @commands.command(name='leave')
  async def leave_vc(self, ctx):
    if ctx.guild.id in self.voice:
      await self.voice[ctx.guild.id].disconnect()

  # TODO:
  # Rewrite
  # 1. YDL error handling
  # 2. Refactor
  @commands.guild_only()
  @commands.command(name='play')
  async def play_audio(self, ctx, *, query):
    if not ctx.guild.id in self.voice:
      if not await self.join_vc(ctx):
        return

    if not self.is_link(query):
      items = self.audio.get_youtube_search(query)["items"]
      choice, menu = 0, None
      youtube_url = ""

      try:
        choice, menu = await self.show_menu(ctx, items)

        if choice < 1 or choice > len(items):
          raise ValueError('`You did not pick a value between 1 and %d. Cancelling.`' % (len(items)))

        youtube_url = YOUTUBE_VIDEO_URL + items[choice-1]["id"]["videoId"]
      except asyncio.exceptions.TimeoutError:
        embed = Embed(color=Colour.gold())
        embed.description = '🕐 User [%s] did not provide any input. Search cancelled.' % (ctx.author.mention)
        await ctx.send(embed=embed)
        return
      except ValueError as e:
        embed = Embed(color=Colour.gold())
        embed.description = '❌ User [%s] did not provide a value in the specified range. Search cancelled.' % (ctx.author.mention)
        await ctx.send(embed=embed)
        return

    result = items[choice-1]

    item = {
      'id': result["id"]["videoId"],
      'title': result["snippet"]["title"],
      'url': youtube_url,
      'img': result["snippet"]["thumbnails"]["default"]["url"],
      'channel': ctx.channel,
      'author': ctx.author,
      'guildId': ctx.guild.id,
    }

    if self.voice[ctx.guild.id].is_playing():
      await ctx.send(embed=self.create_embed(item, queue=True))
      self.queue.enqueue(item)
    else:
      self.play_audio_from_url(item)

  async def show_menu(self, ctx, items):
    menu = await self.show_options(ctx, items)
    response = await self.bot.wait_for('message', check=lambda msg: msg.author.id == ctx.author.id, timeout=15)
    return int(response.content), menu

  def play_audio_from_url(self, item):
    data = self.audio.get_audio_info(item["url"])
    self.bot.loop.create_task(item["channel"].send(embed=self.create_embed(item)))
    self.voice[item["guildId"]].play(FFmpegPCMAudio(data["url"], **FFMPEG_OPTS), after=lambda e: self.play_next(e))

  def play_next(self, e=None):
    if not self.queue.is_empty():
      item = self.queue.dequeue()
      self.play_audio_from_url(item)
      
  @commands.guild_only()
  @commands.command(name='skip')
  async def skip_audio(self, ctx):
    if not ctx.guild.id in self.voice:
      return

    if not self.voice[ctx.guild.id].is_playing():
      return

    if self.queue.is_empty():
      embed = Embed(color=Colour.gold())
      embed.description = '**No more items in the queue.**'
      await ctx.send(embed=embed)

    self.voice[ctx.guild.id].stop()
    self.play_next()

  @commands.guild_only()
  @commands.command(name='queue')
  async def show_queue(self, ctx):
    return

  @commands.guild_only()
  @commands.command(name='pause')
  async def pause_audio(self, ctx):
    if not ctx.guild.id in self.voice:
      return

    if not self.voice[ctx.guild.id].is_playing():
      return
    
    # TODO:
    # Show message in channel
    self.voice[ctx.guild.id].pause()

  @commands.guild_only()
  @commands.command(name='resume')
  async def resume_audio(self, ctx):
    if not ctx.guild.id in self.voice:
      return

    if self.voice[ctx.guild.id].is_playing():
      return

    # TODO:
    # Show message in channel
    self.voice[ctx.guild.id].resume()

  async def show_options(self, ctx, items):
    result = ""
    count = 0

    for item in items:
      count += 1
      url = YOUTUBE_VIDEO_URL + item["id"]["videoId"]
      result += '%d. [%s](%s)\n' % (count, item["snippet"]["title"], url)

    embed = Embed(color=Colour.gold())
    embed.description = result

    return await ctx.send(embed=embed)

  def create_embed(self, item, queue=False):
    embed = Embed(color=Colour.gold())
    if queue:
      embed.description = '**Added** [%s](%s) **to the queue.** Requested by [%s]' % (item["title"], item["url"], item["author"].mention) 
      return embed

    embed.title = '**Now playing**'
    embed.description = '[%s](%s)' % (item["title"], item["url"])
    embed.set_author(name=item["author"].name, icon_url=item["author"].avatar_url)
    embed.set_image(url=item["img"])
    embed.set_footer(text='YouTube')
    return embed

  # TODO:
  # Rewrite - figure out a way to tell a link apart from a search query
  # AVOID REGEX
  def is_link(self, _input: str) -> bool:
    return "http" in _input or "youtube" in _input

def setup(bot):
  bot.add_cog(Music(bot))
