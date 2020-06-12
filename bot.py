import discord
import asyncio
import os
import sys

from discord.ext import commands

bot = commands.Bot(command_prefix='!')
token = ""
cog_list = []

@bot.command(pass_context=True, name="명령어", aliases=["도움말"])
async def info(ctx, func=None):
	if func is None:
		embed = discord.Embed(title="오픈이 명렁어", description="오픈이 명렁어입니다! 접두사는 '!' 입니다!", color=0x1d9c36)
		embed.set_thumbnail(url="https://kung.kr/files/attach/images/7132158/947/374/007/d411bfb49f5b8af7cde11fd2980d2a54.png")

		for i in cog_list:
			cog_data = bot.get_cog(i) # i에 대해 Cog 데이터 구하기
			command_list = cog_data.get_commands() # cog_data에서 명령어 리스트 구하기
			embed.add_field(name=i, value=", ".join([c.name for c in command_list]), inline=False)
		
		embed.set_footer(text="by 201911218 천성필")
		await ctx.send(embed=embed)
	else:
		command_notfound = True
		for _title, cog in bot.cogs.items():
			if not command_notfound:
				break
			else:
				for title in cog.get_commands(): # 명령어를 아까와 같이 구하고 그를 title에 넣어줌
					if title.name == func: # title.name이 func과 같다면
						cmd = bot.get_command(title.name) # title의 명령어를 구함
						embed = discord.Embed(title=f"명령어 : {cmd}", description=cmd.help) # Embed 만들기
						embed.add_field(name="사용법", value=cmd.usage) # 사용법 추가
						await ctx.send(embed=embed)
						command_notfound = False
						break
					else:
						command_notfound = True
	
		if command_notfound:
			if func in cog_list:
				cog_data = bot.get_cog(func) #cog 데이터 구하기
				command_list = cog_data.get_commands() # 명령어 리스트 구하기
				embed = discord.Embed(title=f"카테고리 : {cog_data.qualified_name}", description=cog_data.description) # 카테고리 이름과 설명 추가
				embed.add_field(name="명령어들", value=", ".join([c.name for c in command_list])) # 명령어 리스트 join
				await ctx.send(embed=embed)
			else:
				await ctx.send("그런 이름의 명령어나 카테고리는 없습니다.") # 에러 메시지

@bot.event
async def on_ready():
	print("===================")
	print("로그인")
	print("===================")
	print(bot.user.name)
	print("연결 성공")
	game = discord.Game("아무것도 안")
	print("===================")
	await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_messages(message):
	if message.author.bot:
		return None

def main():
	global token
	file_path = os.path.isdir("./cogs")
	print(file_path)
	if file_path is True:
		DIR = os.path.abspath(os.path.realpath("./cogs"))
		for filename in os.listdir(DIR):
			if filename.endswith(".py"):
				bot.load_extension(f"cogs.{filename[:-3]}")
		for title, cog in bot.cogs.items():
			cog_list.append(title)

	has_bin = os.path.isdir("./bin")
	if has_bin is True:
		bin_path = os.path.abspath(os.path.realpath("./bin"))
		print(bin_path)
	file = open("./init/config.ini")
	token = file.readlines()[2][7:].strip()
	bot.remove_command("help")
	bot.run(token)

if __name__ == "__main__":
	main()
