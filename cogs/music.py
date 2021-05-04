from discord.ext import commands
from discord import Embed, Colour, FFmpegPCMAudio
from googleapiclient.discovery import build
from asyncio.exceptions import TimeoutError
import youtube_dl

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Audio:
  def __init__(self):
    self.ydl = youtube_dl.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'})
    self.service = build('youtube', 'v3', developerKey='')

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
    self.voice = None   
    self.queue = Queue()

  def cog_unload(self):
    self.audio.close()

  @commands.guild_only()
  @commands.command(name='join')
  async def join_vc(self, ctx):
    if ctx.author.voice:
      channel = ctx.author.voice.channel
      self.voice = await channel.connect()
    else:
      print('not in vc')

  @commands.guild_only()
  @commands.command(name='leave')
  async def leave_vc(self, ctx):
    if self.voice:
      await self.voice.disconnect()

  # TODO:
  # Rewrite
  # 1. Better user input handling
  # 2. Error handling
  # 3. YDL error handling
  # 4. Less magical values
  # 5. Prettier output to Discord channels -- embeds 
  # 5. Refactor
  @commands.guild_only()
  @commands.command(name='play')
  async def play_audio(self, ctx, query):
    if not ctx.author.voice:
      # TODO:
      # Give error to the user
      return

    if not self.voice:
      await self.join_vc(ctx)

    if not self.is_link(query):
      items = self.audio.get_youtube_search(query)["items"]
      choice = 0

      try:
        choice = await self.show_menu(ctx, items)

        if choice < 1 or choice > len(items):
          raise ValueError('`You did not pick a value between 1 and %d. Cancelling.`' % (len(items)))

        query = 'https://youtube.com/watch?v=%s' % (items[choice-1]["id"]["videoId"]) 
      except TimeoutError:
        await menu.edit(content='`User did not provide any input. Search cancelled.`')
        return
      except ValueError as e:
        await ctx.send(e)
        return

    if self.voice.is_playing():
      await ctx.send('`Adding %s to the queue.`')
      self.queue.enqueue(query)
    else:
      self.play_audio_from_url(query)

  async def show_menu(self, ctx, items):
    menu = await self.show_options(ctx, items)
    response = await self.bot.wait_for('message', check=lambda msg: msg.author.id == ctx.author.id, timeout=15)
    return int(response.content)

  def play_audio_from_url(self, url: str):
    data = self.audio.get_audio_info(url)
    self.voice.play(FFmpegPCMAudio(data["url"], **FFMPEG_OPTS), after=lambda e: self.play_next(e))

  def play_next(self, _):
    if not self.queue.is_empty():
      url = self.queue.dequeue()
      self.play_audio_from_url(url)
      
  @commands.guild_only()
  @commands.command(name='skip')
  async def skip_audio(self, ctx):
    if not self.voice:
      return

    if not self.voice.is_playing():
      return

    self.play_next()

  @commands.guild_only()
  @commands.command(name='pause')
  async def pause_audio(self, ctx):
    if not self.voice:
      return

    if not self.voice.is_playing():
      return
    
    # TODO:
    # Show message in channel
    self.voice.pause()

  @commands.guild_only()
  @commands.command(name='resume')
  async def resume_audio(self, ctx):
    if not self.voice:
      return

    if self.voice.is_playing():
      return

    # TODO:
    # Show message in channel
    self.voice.resume()

  async def show_options(self, ctx, items):
    result = ""
    count = 0

    for item in items:
      count += 1
      result += '%d. %s\n' % (count, item["snippet"]["title"])

    return await ctx.send(result)

  # TODO:
  # Rewrite - figure out a way to tell a link apart from a search query
  # AVOID REGEX
  def is_link(self, _input: str) -> bool:
    return "http" in _input or "youtube" in _input

def setup(bot):
  bot.add_cog(Music(bot))
