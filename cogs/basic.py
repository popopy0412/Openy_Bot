import discord
import asyncio

from discord.ext import commands
from discord.utils import get

class Basic(commands.Cog, name="기본"):

	"""오픈이의 기본적인 명령어들입니다!"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="잘자", help="오픈이를 종료합니다!", usage="!잘자")
	async def bye(self, ctx):
		await ctx.send("잘 있어!!!!")
		await self.bot.change_presence(status=discord.Status.offline)
		await self.bot.close()
		return

	@commands.command(name="이리와", help="현재 사용자님이 접속해계신 음성 채널에 접속합니다!", usage="!이리와")
	async def join(self, ctx):
		user = ctx.author.voice
		voice = get(self.bot.voice_clients, guild=ctx.guild)

		if not user:
			await ctx.send("사용자가 음성 채널에 연결되어 있지 않습니다.")
			return

		channel = ctx.author.voice.channel
		if voice and voice.is_connected():
			await voice.move_to(channel)
		else:
			await channel.connect()

	@commands.command(name="나가", help="현재 오픈이가 접속해있는 음성 채널에서 접속을 종료합니다!", usage="!나가")
	async def leave(self, ctx):
		await self.bot.voice_clients[0].disconnect()

def setup(bot):
	bot.add_cog(Basic(bot))