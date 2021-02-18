import requests
import datetime

from discord.ext import commands
from discord import Embed, Colour

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
NEWS_URL = "https://hacker-news.firebaseio.com/v0/item/%s.json"
COMMENTS_LINK = "https://news.ycombinator.com/item?id=%s"
EMBED_DESC_FORMAT = "**[link](%s)** • **[%d comments](%s)**"

class Hn:
	def get_posts(self, count: int):
		posts = []

		with requests.session() as session:
			response = session.get(TOP_STORIES_URL).json()

			for i in range(0, count):
				post, err = self.create_post(response[i])
				if err:
					continue

				post.description = EMBED_DESC_FORMAT % (post.site_link, post.comments_count, post.comments_link)
				posts.append(post)
		return posts

	def create_post(self, _id: int):
		url = NEWS_URL % str(_id)

		with requests.session() as session:
			response = session.get(url).json()
			err = False

			post = Post()
			try:
				post.title = response['title']
				post.score = int(response['score'])
				post.site_link = response['url']
				post.comments_count = int(response['descendants'])
				post.comments_link = COMMENTS_LINK % str(_id)
				post.timestamp = datetime.datetime.fromtimestamp(int(response['time'])).strftime("%B %d, %Y")
			except Exception as e:
				print("ERROR: ", e)
				err = True

			return post, err

class Post:
	def __init__(self, title="", score=0, site_link="", comments_count=0, comments_link="", timestamp=""):
		self.title = title
		self.site_link = site_link
		self.comments_link = comments_link
		self.score = score
		self.timestamp = timestamp
		self.description = "" 

class Hackernews(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.hn = Hn()

	@commands.command(name='hn')
	async def get_news(self, ctx, news_count=10):
		posts = self.hn.get_posts(news_count)

		for post in posts:
			embed = self._create_embed(post)
			await ctx.send(embed=embed)

	def _create_embed(self, post):
		embed = Embed(title=post.title, description=post.description, color=Colour.orange())
		embed.add_field(name="Score:", value=post.score, inline=True)
		embed.set_footer(text=post.timestamp)
		return embed

def setup(bot):
	bot.add_cog(Hackernews(bot))
