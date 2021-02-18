import requests

from discord.ext import commands
from discord.ext import tasks
from random import randint

LINK_LATEST = 'http://xkcd.com/info.0.json'
LINK_SPECIFIC = 'http://xkcd.com/%s/info.0.json'

class XkcdCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.xkcd = Xkcd()

	@tasks.loop(minutes=60.0)
	async def refresh_newest(self):
		self.xkcd.update_latest()

	@commands.command(name='xkcd')
	async def get_xkcd(self, ctx):
		title, picture = self.xkcd.get_random_picture()
		if title is None or picture is None:
			return

		await ctx.send(title)
		await ctx.send(picture)

class Xkcd():
	def __init__(self):
		self.latest_num = self.update_latest()

	def get_random_picture(self) -> (str, str):
		with requests.session() as session:
			link = LINK_SPECIFIC % str(self.random_num())
			response = session.get(link).json()
			if response["img"]:
				return response["title"], response["img"]
			return None, None

	def update_latest(self):
		with requests.session() as session:
			response = session.get(LINK_LATEST).json()
			if response["num"]:
				self.latest_num = int(response["num"])

	def random_num(self) -> int:
		return randint(1, self.latest_num)

def setup(bot):
	bot.add_cog(XkcdCog(bot))
