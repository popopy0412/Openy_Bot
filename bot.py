import discord
import asyncio
import os

from discord.ext import commands

#client = discord.Client()
bot = commands.Bot(command_prefix='!')
token = ""
userID = ""

'''@bot.event
async def on_message(message):
	if(message.author.bot):
		return None
	await bot.process_commands(message)'''


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

def main():
	file_path = os.path.isdir("./cogs")
	if file_path is True:
		DIR = os.path.abspath(os.path.realpath("./cogs"))
		for filename in os.listdir(DIR):
			if filename.endswith(".py"):
				bot.load_extension(f"cogs.{filename[:-3]}")
	bot.run(token)

if __name__ == "__main__":
	main()
