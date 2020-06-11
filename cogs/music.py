import discord
import asyncio
import random
import json
import os
import re
import shutil
import youtube_dl
import queue

from discord.ext import commands
from discord.utils import get

class Music(commands.Cog, name="음악"):

	"""오픈이의 음악봇 기능을 담당하는 명령어들입니다!"""

	class URLNotFoundException(Exception):
		pass

	def __init__(self, bot):
		self.bot = bot
		self.queues = queue.Queue()
		if os.path.isdir("./Queue"):
			shutil.rmtree("./Queue")
		if os.path.isfile("song.mp3"):
			os.remove("song.mp3")

	def check_url(self, url : str):
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

	"""def check_queue(self, ctx): # Queue를 체크하는 함수
		Queue_infile = os.path.isdir("./Queue") # 만약 Queue 폴더가 있으면 True, 아니면 False

		if Queue_infile is True and not self.queues.empty(): # Queue 폴더가 있으면

			DIR = os.path.abspath(os.path.realpath("Queue")) # Queue 폴더의 경로
			length = len(os.listdir(DIR)) # Queue 폴더에 있는 노래 수(재생 중 포함)
			still_q = length - 1 # Queue에 폴더에 있는 노래 수(재생 중 제외)	
			try:
				first_file = self.queues.get_nowait() # Queue 폴더의 첫 번째 노래
				print(first_file)
			except: # 예외가 발생하면
				#await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("아무것도 안"))
				#await ctx.send("저장된 노래가 없습니다.")
				print("저장된 노래가 없습니다.\n")
				self.queues = queue.Queue() # queues를 비움
				return
				
			main_location = os.getcwd()
			song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file) #Queue 폴더에 있는 다음 노래 위치
			if length != 0:
				#await ctx.send(f"다음 노래를 재생합니다.\n플레이리스트에 있는 노래 수 : {still_q}")
				print("다음 노래를 재생합니다.\n")
				print(f"플레이리스트에 있는 노래 수 : {still_q}")
				song_there = os.path.isfile("song.mp3")
				if song_there: # 현재 위치에 song.mp3 노래가 있으면
					os.remove("song.mp3")  # song.mp3를 제거

				shutil.move(song_path, main_location) # 다음 노래를 현재 위치로 옮김	
				name = first_file.rsplit("-", 1)
				os.rename(first_file, "song.mp3")
				voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda: self.check_queue(voice)) # 노래를 재생
				voice.source = discord.PCMVolumeTransformer(voice.source)
				voice.source.volume = 0.07

				print(f"재생 중 : {name}")
			else:
				#await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("아무것도 안"))
				#await ctx.send("저장된 노래가 없습니다.")
				print("저장된 노래가 없습니다.")
				self.queues = queue.Queue()
				return
		else:
			os.mkdir("./Queue")
			self.queues = queue.Queue()
			#await ctx.send("저장된 노래가 없습니다.")
			print("저장된 노래가 없습니다.\n")"""

	def check_queue(self, ctx):
		Queue_infile = os.path.isdir("./Queue")
		if Queue_infile is True and not self.queues.empty(): # Queue 폴더가 있으면
			coro = self.play(ctx)
			future = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
			try:
				future.result()
			except:
				print("Error : Cannot play music")

		"""DIR = os.path.abspath(os.path.realpath("Queue")) # Queue 폴더의 경로
		length = len(os.listdir(DIR)) # Queue 폴더에 있는 노래 수(재생 중 포함)
		still_q = length - 1 # Queue에 폴더에 있는 노래 수(재생 중 제외)	
		try:
			first_file = self.queues.get_nowait() # Queue 폴더의 첫 번째 노래
			print(first_file)
		except: # 예외가 발생하면
			#await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("아무것도 안"))
			#await ctx.send("저장된 노래가 없습니다.")
			print("저장된 노래가 없습니다.\n")
			self.queues = queue.Queue() # queues를 비움
			return
		
		main_location = os.getcwd()
		print(os.getcwd())
		song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file) #Queue 폴더에 있는 다음 노래 위치
		if length != 0:
			#await ctx.send(f"다음 노래를 재생합니다.\n플레이리스트에 있는 노래 수 : {still_q}")
			print("다음 노래를 재생합니다.\n")
			print(f"플레이리스트에 있는 노래 수 : {still_q}")
			song_there = os.path.isfile("song.mp3")
			if song_there: # 현재 위치에 song.mp3 노래가 있으면
				os.remove("song.mp3")  # song.mp3를 제거
				shutil.move(song_path, main_location) # 다음 노래를 현재 위치로 옮김	
				name = first_file.rsplit("-", 1)
				os.rename(first_file, "song.mp3")
				voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e:check_queue()) # 노래를 재생
				voice.source = discord.PCMVolumeTransformer(voice.source)
				voice.source.volume = 0.07
					print(f"재생 중 : {name[0]}")
			else:
				#await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("아무것도 안"))
				#await ctx.send("저장된 노래가 없습니다.")
				print("저장된 노래가 없습니다.")
				self.queues = queue.Queue()
				return
		else:
			os.mkdir("./Queue")
			self.queues = queue.Queue()
			#await ctx.send("저장된 노래가 없습니다.")
			print("저장된 노래가 없습니다.\n")"""

	@commands.command(name="재생", help="명령어 뒤에 유튜브 링크를 붙이시면 음악을 틀어드려요!", usage="!재생 [유튜브 링크]")
	async def play_music(self, ctx):
		await self.play(ctx)

	async def play(self, ctx):
		# 명령이 들어왔을 때 예외 처리 부분
		user = ctx.author.voice # 사용자의 음성
		voice = get(self.bot.voice_clients, guild=ctx.guild) # 봇의 음성

		if not user: # 사용자가 음성 채널에 연결되어 있지 않으면
			await ctx.send("사용자가 음성 채널에 연결되어 있지 않습니다.")
			return
		elif not voice: # 오픈이가 음성 채널에 연결되어 있지 않으면
			await ctx.send("오픈이가 음성 채널에 연결되어 있지 않습니다.")
			return
		"""if (url is not None and self.check_url(url) is False) or url is None:
			embed = discord.Embed(title=":no_entry_sign: URLError!", description="URL을 제대로 입력해주세요!", colour=0x2EFEF7)
			embed.set_footer(text="Made by 201911218 천성필")
			await ctx.send(embed=embed)
			return"""

		#====================================================
		
			

		#====================================================

		song_there = os.path.isfile("./song.mp3") # 현재 위치에 song.mp3 노래가 있으면 True, 아니면 False
		try:
			if song_there: # 현재 위치에 song.mp3 노래가 있으면
				os.remove("./song.mp3") # song.mp3를 지우고
				#self.queues = queue.Queue() #플레이리스트를 지움
				#print("이전 노래를 삭제합니다.\n")
		except PermissionError: # 만약 노래가 재생 중이면
			print("이미 재생 중인 노래여서 삭제할 수 없습니다.")
			await ctx.send("ERROR : 노래가 재생 중입니다.")
			return

		Queue_infile = os.path.isdir("./Queue") # Queue 폴더가 있으면 True, 아니면 False
		try:
			Queue_folder = "./Queue" # Queue 폴더의 경로
			if Queue_infile is False or self.queues.empty(): # Queue 폴더가 있으면
				await ctx.send("플레이리스트가 비어있습니다. !추가 명령어를 통해 노래를 추가해주세요.")
				return
		except: # 예외가 발생되면
			print("오래된 재생 폴더가 없습니다.")
			os.mkdir("./Queue") # Queue 폴더를 만듦

		#========함수의 시작 | 재생 관련=========

		"""ydl_opts = {
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
				os.rename(file, "song.mp3")
				break"""
		first_file = self.queues.get_nowait()
		main_location = os.getcwd() + "\\" + first_file
		song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file) #Queue 폴더에 있는 다음 노래 위치

		for file in os.listdir("./Queue"):
			if file == first_file:
				song_there = os.path.isfile("song.mp3")
				if song_there: # 현재 위치에 song.mp3 노래가 있으면
					os.remove("song.mp3")  # song.mp3를 제거
				shutil.move(song_path, main_location) # 다음 노래를 현재 위치로 옮김	
				name = first_file.rsplit("-", 1)
				os.rename(first_file, "song.mp3")
				break
				

		await self.bot.change_presence(status=discord.Status.online, activity=discord.Game("노래를 재생"))

		voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e:self.check_queue(ctx))
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = 0.07

		#nname = name.rsplit("-", 1)
		await ctx.send(f"Playing : {name[0]}")
		print("재생 중\n")

	@commands.command(name="정지", help="만약 현재 음악이 재생 중이면 일시정지합니다!", usage="!정지")
	async def pause(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild) # 봇의 음성

		if voice and voice.is_playing(): # 봇이 음성 채널에 있고, 재생 중이면
			print("재생 정지")
			voice.pause() # 재생을 정지
			await ctx.send("재생을 정지합니다")
		else: # 아니면
			print("노래가 재생중이 아닙니다.")
			await ctx.send("노래가 재생중이 아닙니다.")

	@commands.command(name="다시재생", help="일시정지한 음악을 중단한 시점부터 다시 재생합니다!")
	async def resume(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild) # 봇의 음성

		if voice and voice.is_playing(): # 봇이 음성 채널에서 이미 재생 중이면
			print("이미 노래가 재생중입니다.")
			await ctx.send("이미 노래가 재생중입니다.")
		else: # 아니면
			print("다시 재생")
			voice.resume() # 다시 재생
			await ctx.send("노래를 다시 재생합니다")

	@commands.command(name="다음", help="플레이리스트에 있는 다음 음악으로 넘깁니다!", usage="!다음")
	async def skip(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild) # 봇의 음성

		if voice and voice.is_playing(): # 봇이 음성 채널에서 재생 중이면
			voice.stop() # 재생을 멈춤


	@commands.command(name="초기화", help="플레이리스트를 초기화합니다!", usage="!초기화")
	async def reset(self, ctx):

		voice = get(self.bot.voice_clients, guild=ctx.guild) # 봇의 음성

		self.queues = queue.Queue() # 플레이리스트를 비움

		if voice and voice.is_playing(): # 봇이 음성 채널에서 재생 중이면
			print("초기화")
			voice.stop() # 재생을 멈춤

		await ctx.send("플레이리스트를 초기화합니다.")
		
		is_song = os.path.isfile("song.mp3")
		if is_song is True:
			os.remove("./song.mp3")
		is_queue = os.path.isdir("Queue")
		if is_queue:
			shutil.rmtree("./Queue")
		

	@commands.command(name="추가", help="명령어 뒤에 유튜브 링크를 붙이시면 플레이리스트의 마지막에 음악을 추가합니다!", usage="!추가 [유튜브 링크]")
	async def add(self, ctx, url : str = None):
		# url 예외 처리 부분
		if (url is not None and self.check_url(url) is False) or url is None:
			embed = discord.Embed(title=":no_entry_sign: URLError!", description="URL을 제대로 입력해주세요!", colour=0x2EFEF7)
			embed.set_footer(text="Made by 201911218 천성필")
			await ctx.send(embed=embed)
			return
		#==================

		Queue_infile = os.path.isdir("./Queue") # Queue 폴더가 있다면 True, 아니면 False
		if Queue_infile is False: # Queue 폴더가 없다면
			os.mkdir("Queue") # 현재 위치에 Queue 폴더를 생성

		queue_path = os.path.abspath(os.path.realpath("Queue")) # Queue 폴더의 경로

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
		
		for file in os.listdir("./"): # 다운 받은 노래 중
			if file.endswith(".mp3") and file != "song.mp3": # 현재 재생 중이 아닌 노래 중에서
				name = file # 이름을 저장
				name = name.rsplit("-", 1)[0] # 그리고 제목만 추출

				main_location = os.path.abspath(os.path.realpath("") + "\\" + file) # 현재 위치
				DIR = os.path.abspath(os.path.realpath("Queue"))
				song_path = DIR + "\\" + file # Queue의 위치

				self.queues.put_nowait(file) # queues에 file을 넣어줌

				#print(f"{main_location}\n{song_path}")
				await ctx.send("\"" + name + "\"(을)를 추가합니다")
				shutil.move(main_location, song_path)
				break
				
		print("노래가 추가되었습니다.")
	
	
#========================================

def setup(bot):
    bot.add_cog(Music(bot))