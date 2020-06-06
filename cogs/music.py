import discord
import asyncio
import random
import json
import os
import re
import shutil
import youtube_dl

from discord.ext import commands
from discord.utils import get

class Music(commands.Cog):
	class URLNotFoundException(Exception):
		pass

	def __init__(self, bot):
		self.bot = bot
		self.queues = {}
        
	@commands.command(name="출력")
	async def printlf(self, ctx):
		await ctx.send("adfafsd")

	@commands.command(name="명령어")
	async def help(self, ctx):
		embed = discord.Embed(title="오픈이 명렁어", description="오픈이 명렁어입니다!", color=0x1d9c36)
		embed.set_thumbnail(url="https://kung.kr/files/attach/images/7132158/947/374/007/d411bfb49f5b8af7cde11fd2980d2a54.png")
		embed.add_field(name="!음악", value="뒤에 유튜브 링크를 붙이시면 음악을 틀어드립니다!", inline=True)
		embed.set_footer(text="by 201911218 천성필")
		await ctx.send(embed=embed)

	"""@commands.command(name="안녕")
	async def hi(self, ctx):
		await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("아무것도 안"))
		await ctx.send("안녕~~~")"""

	@commands.command(name="잘자", help="봇을 종료")
	async def bye(self, ctx):
		await ctx.send("잘 있어!!!!")
		await self.bot.change_presence(status=discord.Status.offline)
		await self.bot.close()
		return
	@commands.command(name="이리와")
	async def join(self, ctx):
		global voice
		channel = ctx.author.voice.channel
		voice = get(self.bot.voice_clients, guild=ctx.guild)

		if voice and voice.is_connected():
			await voice.move_to(channel)
		else:
			#voice_channel = ctx.author.voice.channel # voice_channel = 보이스 채널
			await channel.connect()
		"""elif not voice and not voice.is_connected():
			await ctx.send("사용자가 음성 채널에 연결되어 있지 않습니다.")"""
		"""else:
			await ctx.send("사용자가 음성 채널에 연결되어 있지 않습니다.")"""

	@commands.command(name="재생")
	async def play(self, ctx, url : str = None):
		user = ctx.author.voice
		voice = get(self.bot.voice_clients, guild=ctx.guild)
		if not user:
			await ctx.send("사용자가 음성 채널에 연결되어 있지 않습니다.")
			return
		elif not voice:
			await ctx.send("오픈이가 음성 채널에 연결되어 있지 않습니다.")
			return
		if await check_url(url) is False:
			await ctx.send(embed=discord.Embed(title=":no_entry_sign: url을 제대로 입력해주세요.", colour=0x2EFEF7))
			return
		
		def check_queue():
			Queue_infile = os.path.isdir("./Queue")
			if Queue_infile is True:
				DIR = os.path.abspath(os.path.realpath("Queue"))
				length = len(os.listdir(DIR))
				still_q = length - 1
				try:
					first_file = os.listdir(DIR)[0]
				except:
					print("저장된 노래가 없습니다.\n")
					self.queues.clear()
					return
				main_location = os.path.dirname(os.path.realpath(__file__))
				song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
				if length != 0:
					print("노래가 끝났습니다. 다음 노래를 재생합니다.\n")
					print(f"노래가 아직 있습니다 : {still_q}")
					if song_there:
						os.remove("song.mp3")
					shutil.move(song_path, main_location)
					for file in os.listdir("./"):
						if file.endswith(".mp3"):
							os.rename(file, "song.mp3")

					voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
					voice.source = discord.PCMVolumeTransformer(voice.source)
					voice.source.volume = 0.07

				else:
					self.queues.clear()
					return

			else:
				self.queues.clear()
				print("저장된 노래가 업습니다.\n")

		song_there = os.path.isfile("song.mp3")
		try:
			if song_there:
				os.remove("song.mp3")
				self.queues.clear()
				print("이전 노래를 삭제합니다.\n")
		except PermissionError:
			print("이미 재생 중인 노래여서 삭제할 수 없습니다.")
			await ctx.send("ERROR : 노래가 재생 중입니다.")
			return

		Queue_infile = os.path.isdir("./Queue")
		try:
			Queue_folder = "./Queue"
			if Queue_infile is True:
				print("오래된 재생 폴더를 삭제합니다.")
				shutil.rmtree(Queue_folder)
		except:
			print("오래된 재생 폴더가 없습니다.")

		await ctx.send("준비 완료!")
		await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("노래를 재생"))

		voice = get(self.bot.voice_clients, guild=ctx.guild)

		ydl_opts = {
			'format' : 'bestaudio/best',
			'quiet' : True,
			'postprocessors' : [{
				'key' : 'FFmpegExtractAudio',
				'preferredcodec' : 'mp3',
				'preferredquality' : '192'
			}],
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			print("노래를 다운중입니다.\n")
			ydl.download([url])

		for file in os.listdir("./"):
			if file.endswith(".mp3"):
				name = file
				print(f"파일 이름을 변경합니다 : {file}\n")
				os.rename(file, "song.mp3")

		voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e:check_queue())
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = 0.07

		nname = name.rsplit("-", 2)
		await ctx.send(f"Playing : {nname[0]}")
		print("재생 중\n")

	@commands.command(name="정지")
	async def pause(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild)

		if voice and voice.is_playing():
			print("재생 정지")
			voice.pause()
			await ctx.send("재생을 정지합니다")
		else:
			print("노래가 재생중이 아닙니다.")
			await ctx.send("노래가 재생중이 아닙니다.")

	@commands.command(name="다시재생")
	async def resume(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild)

		if voice and voice.is_playing():
			print("이미 노래가 재생중입니다.")
			await ctx.send("이미 노래가 재생중입니다.")
		else:
			print("다시 재생")
			voice.resume()
			await ctx.send("노래를 다시 재생합니다")


	@commands.command(name="다음")
	async def skip(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild)

		self.queues.clear()

		if voice and voice.is_playing():
			print("노래 스킵")
			voice.stop()
			await ctx.send("노래를 스킵합니다")
		else:
			print("노래가 재생중이 아닙니다.")
			await ctx.send("노래가 재생중이 아닙니다.")

	@commands.command(name="추가")
	async def add(self, ctx, url : str):

		if await check_url(url):
			await ctx.send(embed=discord.Embed(title=":no_entry_sign: url을 입력해주세요.", colour=0x2EFEF7))
		else:
			await ctx.send(embed=discord.Embed(title=":no_entry_sign: url을 제대로 입력해주세요.", colour=0x2EFEF7))

		Queue_infile = os.path.isdir("./Queue")
		if Queue_infile is False:
			os.mkdir("Queue")
		DIR = os.path.abspath(os.path.realpath("Queue"))
		q_num = len(os.listdir(DIR))
		q_num += 1
		add_queue = True
		while add_queue:
			if q_num in self.queues:
				q_num += 1
			else:
				add_queue = False
				self.queues[q_num] = q_num

		queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

		ydl_opts = {
			'format' : 'bestaudio/best',
			'quiet' : True,
			'postprocessors' : [{
				'key' : 'FFmpegExtractAudio',
				'preferredcodec' : 'mp3',
				'preferredquality' : '192'
			}],
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			print("노래를 다운중입니다.\n")
			ydl.download([url])
		await ctx.send("\"" + str(q_num) + "\" 노래를 추가합니다")
		print("노래가 추가되었습니다.")
	
	@commands.command(name="나가")
	async def leave(self, ctx):
		await self.bot.voice_clients[0].disconnect()
#========================================
async def check_url(url : str):
	try:
		if url == None:
			raise Music.URLNotFoundException
		# 정규 표현식을 사용해 url 검사
		url1 = re.match('(https?://)?(www\.)?((youtube\.(com))/watch\?v=([-\w]+)|youtu\.be/([-\w]+))', url)
		if url1 == None:
			return False
		return True
	except Music.URLNotFoundException:
		return False

def setup(bot):
    bot.add_cog(Music(bot))