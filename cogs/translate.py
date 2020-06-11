#This code and description is written by Hoplin
#This code is written with API version 1.0.0(Rewirte-V)
#No matter to use it as non-commercial.
#Papago API Reference : https://developers.naver.com/docs/nmt/reference/

import discord
import asyncio
import os
import urllib
import re # Regex for youtube link
import warnings
import requests
import unicodedata
import json

from discord.ext import commands
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote

#Naver Open API application ID
client_id = ""
#Naver Open API application token
client_secret = ""

class Papago(commands.Cog, name="번역"):

    """오픈이의 파파고를 이용한 한 <-> 미, 일, 중 번역 기능을 담당하는 명령어들입니다!"""

    def __init__(self, bot):
        global client_id
        global client_secret

        self.bot = bot
        file = open("./init/config.ini")
        client_id = file.readline()[11:].strip()
        client_secret = file.readline()[15:].strip()

    @commands.command(name="한영번역", help="명령어 뒤에 번역하고 싶은 한국어를 입력하시면 영어로 번역해드립니다!", usage="!한영번역 [번역하고 싶은 한국어]")
    async def ko_en(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                print(combineword)
                # Make Query String.
                dataParmas = "source=ko&target=en&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | Korean -> English", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated English", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")


    @commands.command(name="영한번역", help="명령어 뒤에 번역하고 싶은 영어를 입력하시면 한국어로 번역해드립니다!", usage="!영한번역 [번역하고 싶은 영어]")
    async def en_ko(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=en&target=ko&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | English -> Korean", description="", color=0x5CD1E5)
                    embed.add_field(name="English to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")

    @commands.command(name="한일번역", help="명령어 뒤에 번역하고 싶은 한국어를 입력하시면 일본어로 번역해드립니다!", usage="!한일번역 [번역하고 싶은 한국어]")
    async def ko_jp(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=ko&target=ja&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | Korean -> Japanese", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Japanese", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")

    @commands.command(name="일한번역", help="명령어 뒤에 번역하고 싶은 일본어를 입력하시면 한국어로 번역해드립니다!", usage="!일한번역 [번역하고 싶은 일본어]")
    async def jp_ko(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                dataParmas = "source=ja&target=ko&text=" + combineword
                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')

                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | Japanese -> Korean", description="", color=0x5CD1E5)
                    embed.add_field(name="Japanese to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")

    @commands.command(name="한중번역", help="명령어 뒤에 번역하고 싶은 한국어를 입력하시면 중국어로 번역해드립니다!", usage="!한중번역 [번역하고 싶은 한국어]")
    async def ko_cn(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.

                #Simplified Chinese
                dataParmas = "source=ko&target=zh-CN&text=" + combineword

                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | Korean -> Chinese(Simplified Chinese)", description="", color=0x5CD1E5)
                    embed.add_field(name="Korean to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Chinese(Simplified)", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")

    @commands.command(name="중한번역", help="명령어 뒤에 번역하고 싶은 중국어를 입력하시면 한국어로 번역해드립니다!", usage="!중한번역 [번역하고 싶은 중국어]")
    async def cn_ko(self, ctx, *texts):
        baseurl = "https://openapi.naver.com/v1/papago/n2mt"

        try:
            if texts is None:
                await ctx.send("단어 혹은 문장이 입력되지 않았어요. 다시한번 확인해주세요.")
                return
            else:
                trsText = texts
                combineword = ""
                for word in trsText:
                    combineword += " " + word
                # if entered value is sentence, assemble again and strip blank at both side
                savedCombineword = combineword.strip()
                combineword = quote(savedCombineword)
                # Make Query String.
                # Simplified Chinese
                dataParmas = "source=zh-CN&target=ko&text=" + combineword


                # Make a Request Instance
                request = Request(baseurl)
                # add header to packet
                request.add_header("X-Naver-Client-Id", client_id)
                request.add_header("X-Naver-Client-Secret", client_secret)
                response = urlopen(request, data=dataParmas.encode("utf-8"))

                responsedCode = response.getcode()
                if (responsedCode == 200):
                    response_body = response.read()
                    # response_body -> byte string : decode to utf-8
                    api_callResult = response_body.decode('utf-8')
                    # JSON data will be printed as string type. So need to make it back to type JSON(like dictionary)
                    api_callResult = json.loads(api_callResult)
                    # Final Result
                    translatedText = api_callResult['message']['result']["translatedText"]
                    embed = discord.Embed(title="Translate | Chinese -> Korean", description="", color=0x5CD1E5)
                    embed.add_field(name="Chinese to translate", value=savedCombineword, inline=False)
                    embed.add_field(name="Translated Korean", value=translatedText, inline=False)
                    embed.set_thumbnail(url="https://papago.naver.com/static/img/papago_og.png")
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필. API provided by Naver Open API")
                    await ctx.send("Translate complete", embed=embed)
                else:
                    await ctx.send("Error Code : " + responsedCode)
        except HTTPError as e:
            await ctx.send("HTTPError : 번역에 실패했습니다.")

def setup(bot):
    bot.add_cog(Papago(bot))


