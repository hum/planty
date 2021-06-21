from discord.ext import commands, tasks
from .utils import checks
from enum import IntEnum
from random import randint
from os import getenv
import struct
import asyncio

RCON_IP = getenv('RCON_IP')
RCON_PORT = getenv('RCON_PORT')
RCON_PASS = getenv('RCON_PASS')

class PacketType(IntEnum):
  LOGIN = 3
  COMMAND = 2
  COMMAND_RESPONSE = 0

class Rcon:
  def __init__(self, host:str = "", port:int = 0, password:str = ""):
    self.host = host
    self.port = port
    self.password = password
    self._reader = None
    self._writer = None

  async def __aexit__(self, exc_type, exc, b):
    await self.close()

  async def init(self, timeout=5):
    try:
      self._reader, self._writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout)
    except Exception as e:
      print(e)

    await self._send_payload(PacketType.LOGIN, self.password)

  async def create_listener(self, cmd, callback):
    loop = asyncio.get_event_loop()
    return loop.create_task(self.listen_to_messages(cmd, callback))

  async def _send_payload(self, packet_type, data):
    # random payload ID
    p_req_id = randint(0, 2147483647)

    # create packet
    p_data = struct.pack('<ii', p_req_id, packet_type) + data.encode('utf-8') + b'\x00\x00'
    p = struct.pack('<i', len(p_data)) + p_data

    # send packet
    self._writer.write(p)
    await self._writer.drain()

    r_len = struct.unpack('<i', (await self._reader.read(4)))[0]
    r_data = await self._reader.read(r_len)

    if not r_data.endswith(b'\x00\x00'):
      print('invalid data')

    r_req_id, r_type = struct.unpack('<ii', r_data[0:8])
    r_msg = r_data[8:-2].decode('utf-8')

    return r_msg, r_type

  async def send_cmd(self, cmd):
    return await self._send_payload(PacketType.COMMAND, cmd)



class Minecraft(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.rcon = None
    self.guild = None
    self.channel = None

  @commands.Cog.listener()
  async def on_ready(self):
    self.guild = self.bot.get_guild(638151136439959573)
    self.channel = self.bot.get_channel(783773941705080862)
    self.rcon = Rcon(RCON_IP, RCON_PORT, RCON_PASS)
    await self.rcon.init()

  @commands.Cog.listener()
  async def on_message(self, message): 
    if message.author.bot:
      return

    if not message.channel.id == self.channel.id:
      return

    if not self.check_messages.is_running():
      return

    msg = self.create_message_format(message.author.name, message.content)
    await self.rcon.send_cmd(msg)

  @tasks.loop(seconds=1.0)
  async def check_messages(self):
    cmd_name = "logloglogloglog"
    try:
      response, _ = await self.rcon.send_cmd(cmd_name)
      if not cmd_name in response:
        await self.channel.send(response)
    except RuntimeError as e:
      # TODO:
      # Log this properly, for now only print to test if it fails
      print(e)
      return
    except struct.error as e:
      print(e)
      return

  @checks.is_admin()
  @commands.guild_only()
  @commands.command(name="listen")
  async def listen(self, ctx):
    self.check_messages.start()

  @checks.is_admin()
  @commands.guild_only()
  @commands.command(name="stop")
  async def stop(self, ctx):
    if self.check_messages.is_running():
      self.check_messages.cancel()

  def create_message_format(self, author: str, message: str):
    payload = 'tellraw @a [{"text":"<"}, '
    payload +=  '{"text": "%s", "color":"blue"}, '
    payload +=  '{"text": ">"},'
    payload += '{"text": "%s"}]'
    return payload % (author, message)

  def cog_unload(self):
    if self.check_messages.is_running():
      self.check_messages.cancel()

def setup(bot):
  bot.add_cog(Minecraft(bot))
