from discord.ext import commands
from discord import Embed, Colour, FFmpegPCMAudio

from googleapiclient.discovery import build
from asyncio.exceptions import TimeoutError

import youtube_dl

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

class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.audio = Audio()
		self.voice = None		

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
	async def play_audio(self, ctx, _input):
		if not self.voice:
			await self.join_vc(ctx)

		if self.is_link(_input):
			# play song from the provided url
			print('its a link bro', _input)
		else:
			data = self.audio.get_youtube_search(_input)
			menu = await self.show_options(ctx, data["items"])
			msg = None

			try:
				msg = await self.bot.wait_for('message', check=lambda message: message.author.id == ctx.author.id, timeout=15)
			except TimeoutError:
				await menu.edit(content='`User did not provide any input. Search cancelled.`')
				return

			val = 0
			try:
				val = int(msg.content) 
				if val <= 0 or val > 5:
					raise ValueError('value is not between 1-5.')
			except ValueError:
				await ctx.send('`Invalid input. Try again.`')
				return

			item = data["items"][val-1]
			print('User chose %d, which is %s' % (val, item["snippet"]["title"]))
			await ctx.send('%d. %s' % (val, item["snippet"]["title"]))

			info = self.audio.get_audio_info('https://youtube.com/watch?v=%s' % (item["id"]["videoId"]))
			print(info["url"])

			FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

			self.voice.play(FFmpegPCMAudio(info["url"], **FFMPEG_OPTS), after=lambda e: print('done', e))
			self.voice.is_playing()

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
