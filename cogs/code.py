import requests

from discord.ext import commands

COMMAND_WRAPPER = "@commands.command(name='%s')"
SEARCH_KEYWORDS = [
  " def ", 
  "@commands"
]

class FileParser:
  def __init__(self):
    self.source_url = "https://github.com/hum/planty/blob/main/cogs/%s"
    self.raw_url = "https://raw.githubusercontent.com/hum/planty/main/cogs/%s"

  def get_code_from_url(self, cog_filename: str = ""):
    if len(cog_filename) > 0:
      with requests.session() as session:
        result = session.get(self.raw_url % (cog_filename))
        if result.status_code == requests.codes.ok:
          return result.text
        else:
          return None
    else:
      return None

  def find_cog_code(self, cog_filename, cog_name):
    text = self.get_code_from_url(cog_filename)
    find = COMMAND_WRAPPER % cog_name

    result = []
    found = False
    if text is not None:
      text = text.splitlines()

      for i in range(0, len(text)):
        if not found and not find in text[i]:
          continue

        if find in text[i]:
          found = True
          result.append(find)
        else:
          if found:
            if text[i+1] in SEARCH_KEYWORDS:
              return result
            else:
              result.append(text[i])
    else:
      return None

class Code(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.parser = FileParser()

  @commands.command(name='source')
  async def code(self, ctx, cmd_name: str = ""):
    obj = self.bot.get_command(cmd_name)
    if obj is None:
      return await ctx.send("Could not find the command.")
    
    filename = obj.callback.__code__.co_filename.rsplit('/', 1)[1]
    cog_code = self.parser.find_cog_code(filename, cmd_name)

    if cog_code is not None:
      result = "\n".join(cog_code)
      await ctx.send("```python\n%s\n```URL: <%s>" % (result, self.parser.source_url % (filename)))
    else:
      await ctx.send("🌱 Could not find the command.")
   
def setup(bot):
  bot.add_cog(Code(bot))
