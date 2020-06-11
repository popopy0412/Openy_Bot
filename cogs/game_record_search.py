#This code and description is written by Hoplin
#This code is written with API version 1.0.0(Rewrite-V)
#No matter to use it as non-commercial.

# To make a discord bot you need to download discord.py with pip
#-*- coding: utf-8 -*-
import discord
import asyncio
import os
import urllib
import re # Regex for youtube link
import warnings
import requests
import unicodedata
import time

from discord.ext import commands
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote

class Game_Record_Search(commands.Cog, name="전적검색"):

    """오픈이의 각종 게임 전적검색 기능을 담당하는 명령어들입니다!"""

    # for lolplayersearch
    def __init__(self, bot):
        self.bot = bot
        self.opggsummonersearch = 'https://www.op.gg/summoner/userName='
        self.tierScore = {
            'default' : 0,
            'iron' : 1,
            'bronze' : 2,
            'silver' : 3,
            'gold' : 4,
            'platinum' : 5,
            'diamond' : 6,
            'master' : 7,
            'grandmaster' : 8,
            'challenger' : 9
        }   
        
    def tierCompare(self, solorank, flexrank):
        tierScore = self.tierScore
        if tierScore[solorank] > tierScore[flexrank]:
            return 0
        elif tierScore[solorank] < tierScore[flexrank]:
            return 1

    def deleteTags(self, htmls):
        for a in range(len(htmls)):
            htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
        return htmls

        '''
        embed = discord.Embed(title="명령어 사용방법!", description="!전적 (소환사 이름 - 띄어쓰기 붙여쓰기 상관없습니다)", color=0x5CD1E5)
        embed.set_footer(text='Service provided by Hoplin.',
        icon_url='https://avatars2.githubusercontent.com/u/45956041?s=460&u=1caf3b112111cbd9849a2b95a88c3a8f3a15ecfa&v=4')
        '''

    def returnStatsTFT(self, bs):
        # 통계 정보
        InfoText = []
        statsInfo = bs.findAll('span', {'class': 'profile__tier__stat__value float-right'})
        for sI in statsInfo:
            InfoText.append(sI.text.strip())

        InfoText = InfoText[:5]
        # InfoText List value in place order
        # [Number of win,Win Rate,Top 4,Top4 Rate, Total Game,Average place]
        return InfoText

    def returnStatsPercentage(self, bs):
        InfoText = []
        statsPercentage = bs.findAll('span',{'class' : 'profile__tier__stat__text'})
        for sP in statsPercentage:
            InfoText.append(sP.text.strip())
        return InfoText

    @commands.command(name="롤전적", help="명령어 뒤에 리그 오브 레전드 한국 서버 닉네임을 붙이시면 전적을 검색해드립니다!"
    , usage="!명령어 [닉네임]")
    async def lol(self, ctx, *name):

        opggsummonersearch = self.opggsummonersearch
        try:
            if name == ():
                embed = discord.Embed(title="소환사 이름이 입력되지 않았습니다!", description="", color=0x5CD1E5)
                embed.add_field(name="Summoner name not entered",
                                value="To use command !롤전적 : !롤전적 (Summoner Nickname)", inline=False)
                embed.set_footer(text='Service provided by Hoplin. Edited by 201911218 천성필')
                await ctx.send("Error : Incorrect command usage ", embed=embed)
            else:
                playerNickname = ''.join(name[0:])
                # Open URL
                checkURLBool = urlopen(opggsummonersearch + quote(playerNickname))
                bs = BeautifulSoup(checkURLBool, 'html.parser')
                # 자유랭크 언랭은 뒤에 '?image=q_auto&v=1'표현이없다
                # Patch Note 20200503에서
                # Medal = bs.find('div', {'class': 'ContentWrap tabItems'}) 이렇게 바꾸었었습니다.
                # PC의 설정된 환경 혹은 OS플랫폼에 따라서 ContentWrap tabItems의 띄어쓰기가 인식이
                Medal = bs.find('div', {'class': 'SideContent'})
                RankMedal = Medal.findAll('img', {'src': re.compile('\/\/[a-z]*\-[A-Za-z]*\.[A-Za-z]*\.[A-Za-z]*\/[A-Za-z]*\/[A-Za-z]*\/[a-z0-9_]*\.png')})
                # Variable RankMedal's index 0 : Solo Rank
                # Variable RankMedal's index 1 : Flexible 5v5 rank
                # for mostUsedChampion
                mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                # 솔랭, 자랭 둘다 배치가 안되어있는경우 -> 사용된 챔피언 자체가 없다. 즉 모스트 챔피언 메뉴를 넣을 필요가 없다.
                # Scrape Summoner's Rank information
                # [Solorank,Solorank Tier]
                solorank_Types_and_Tier_Info = self.deleteTags(bs.findAll('div', {'class': {'RankType', 'TierRank'}}))
                # [Solorank LeaguePoint, Solorank W, Solorank L, Solorank Winratio]
                solorank_Point_and_winratio = self.deleteTags(
                    bs.findAll('span', {'class': {'LeaguePoints', 'wins', 'losses', 'winratio'}}))
                # [Flex 5:5 Rank,Flexrank Tier,Flextier leaguepoint + W/L,Flextier win ratio]
                flexrank_Types_and_Tier_Info = self.deleteTags(bs.findAll('div', {
                    'class': {'sub-tier__rank-type', 'sub-tier__rank-tier', 'sub-tier__league-point',
                              'sub-tier__gray-text'}}))
                # ['Flextier W/L]
                flexrank_Point_and_winratio = self.deleteTags(bs.findAll('span', {'class': {'sub-tier__gray-text'}}))
                # embed.set_imag()는 하나만 들어갈수 있다.
                # 솔랭, 자랭 둘다 배치 안되어있는 경우 -> 모스트 챔피언 출력 X
                if len(solorank_Point_and_winratio) == 0 and len(flexrank_Point_and_winratio) == 0:
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("소환사 " + playerNickname + "님의 전적", embed=embed)
                # 솔로랭크 기록이 없는경우
                elif len(solorank_Point_and_winratio) == 0:
                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()
                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name="Ranked Solo : Unranked", value="Unranked", inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("소환사 " + playerNickname + "님의 전적", embed=embed)
                # 자유랭크 기록이 없는경우
                elif len(flexrank_Point_and_winratio) == 0:
                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()
                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Flex 5:5 Rank : Unranked", value="Unranked", inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + "WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("소환사 " + playerNickname + "님의 전적", embed=embed)
                # 두가지 유형의 랭크 모두 완료된사람
                else:
                    # 더 높은 티어를 thumbnail에 안착
                    solorankmedal = RankMedal[0]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')
                    flexrankmedal = RankMedal[1]['src'].split('/')[-1].split('?')[0].split('.')[0].split('_')
                    # Make State
                    SoloRankTier = solorank_Types_and_Tier_Info[0] + ' : ' + solorank_Types_and_Tier_Info[1]
                    SoloRankPointAndWinRatio = solorank_Point_and_winratio[0] + "/ " + solorank_Point_and_winratio[
                        1] + " " + solorank_Point_and_winratio[2] + " /" + solorank_Point_and_winratio[3]
                    FlexRankTier = flexrank_Types_and_Tier_Info[0] + ' : ' + flexrank_Types_and_Tier_Info[1]
                    FlexRankPointAndWinRatio = flexrank_Types_and_Tier_Info[2] + " /" + flexrank_Types_and_Tier_Info[-1]
                    # most Used Champion Information : Champion Name, KDA, Win Rate
                    mostUsedChampion = bs.find('div', {'class': 'ChampionName'})
                    mostUsedChampion = mostUsedChampion.a.text.strip()
                    mostUsedChampionKDA = bs.find('span', {'class': 'KDA'})
                    mostUsedChampionKDA = mostUsedChampionKDA.text.split(':')[0]
                    mostUsedChampionWinRate = bs.find('div', {'class': "Played"})
                    mostUsedChampionWinRate = mostUsedChampionWinRate.div.text.strip()
                    cmpTier = self.tierCompare(solorankmedal[0], flexrankmedal[0])
                    embed = discord.Embed(title="소환사 전적검색", description="", color=0x5CD1E5)
                    embed.add_field(name="Summoner Search From op.gg", value=opggsummonersearch + playerNickname,
                                    inline=False)
                    embed.add_field(name=SoloRankTier, value=SoloRankPointAndWinRatio, inline=False)
                    embed.add_field(name=FlexRankTier, value=FlexRankPointAndWinRatio, inline=False)
                    embed.add_field(name="Most Used Champion : " + mostUsedChampion,
                                    value="KDA : " + mostUsedChampionKDA + " / " + " WinRate : " + mostUsedChampionWinRate,
                                    inline=False)
                    if cmpTier == 0:
                        embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    elif cmpTier == 1:
                        embed.set_thumbnail(url='https:' + RankMedal[1]['src'])
                    else:
                        if solorankmedal[1] > flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        elif solorankmedal[1] < flexrankmedal[1]:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                        else:
                            embed.set_thumbnail(url='https:' + RankMedal[0]['src'])
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("소환사 " + playerNickname + "님의 전적", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await ctx.send("Wrong Summoner Nickname")
        except UnicodeEncodeError as e:
            embed = discord.Embed(title="소환사 전적검색 실패", description="", color=0x5CD1E5)
            embed.add_field(name="???", value="올바르지 않은 소환사 이름입니다. 다시 확인해주세요!", inline=False)
            await ctx.send("Wrong Summoner Nickname", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="존재하지 않는 소환사", description="", color=0x5CD1E5)
            embed.add_field(name="해당 닉네임의 소환사가 존재하지 않습니다.", value="소환사 이름을 확인해주세요", inline=False)
            embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
            await ctx.send("Error : Non existing Summoner ", embed=embed)

    @commands.command(name="롤체전적", help="명렁어 뒤에 전략적 팀 전투(TFT) 한국 서버 닉네임을 붙이시면 전적을 확인해드립니다!", usage="!롤체전적 [닉네임]")
    async def TFT(self, ctx, *name):
        try:
            krTFTProfileURL = 'https://lolchess.gg/profile/kr/'
            playerNickname = ''.join(name[0:])
            playerNicknameShow = ' '.join(name[0:])
            playerInfoURL = krTFTProfileURL + quote(playerNickname)
            html = urlopen(playerInfoURL)
            bs = BeautifulSoup(html, 'html.parser')

            # 닉네임이 입력되지 않은 경우
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !롤체전적 : !롤체전적 (Nickname)", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)


            elif bs.find('div', {'class': 'profile__tier__icon'}).img['alt'] == 'Unranked':
                # 티어 아이콘 URL
                tierIcon = 'https:' + bs.find('div', {'class': 'profile__tier__icon'}).img[
                    'src']  # Unranked -> 배치안된경우 필터링

                # 티어 정보
                tierInfo = bs.find('div', {'class': 'profile__tier__icon'}).img['alt']

                #Most Syergy
                embedSynergy = True
                mostSyn = bs.find('div', {'class': 'profile__recent__trends__traits'})
                synergyInfo = []
                if mostSyn == None:
                    embedSynergy = False
                    pass
                else:
                    mostSyn = mostSyn.table.tbody.findAll('tr')[0].findAll('td')
                    for sf in mostSyn:
                        synergyInfo.append(sf.text.strip())


                statsli = self.returnStatsTFT(bs)
                embed = discord.Embed(title="Team Fight Tactics player stats from lolchess.gg", description="", color=0x5CD1E5)
                embed.add_field(name="Click on the link below to view more information",
                                value=playerInfoURL,
                                inline=False)
                embed.add_field(name="Rank Information",
                                value=tierInfo + "(Unable to find Raiting & Ranking Info)",
                                inline=False)
                if mostSyn:
                    embed.add_field(name="Most used Synergy : " + synergyInfo[0],
                                    value="Use : " + synergyInfo[4] + " time(s) | " + "1st place Ratio : " +
                                          synergyInfo[-2] + " | Top4 Ratio : " + synergyInfo[-1],
                                    inline=False)
                else:
                    pass
                embed.add_field(name="Number of Win(#1)",
                                value=statsli[0] + "/Top 0.00%",
                                inline=True)
                embed.add_field(name="Win Ratio",
                                value=statsli[1] + "/Top 0.00%",
                                inline=True)
                embed.add_field(name="Number of Top 4(#4)",
                                value=statsli[2] + "/Top 0.00%",
                                inline=True)
                embed.add_field(name="Top 4 Ratio",
                                value=statsli[3] + "/Top 0.00%",
                                inline=True)
                embed.add_field(name="Number of game",
                                value=statsli[4] + "/Top 0.00%",
                                inline=True)
                embed.add_field(name="Average Place",
                                value="NaN",
                                inline=True)
                embed.set_thumbnail(url=tierIcon)
                embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
                await ctx.send("TFT player " + playerNicknameShow + "'s information search", embed=embed)


            else:
                # 티어 정보
                tierInfo = bs.find('div', {'class': 'profile__tier__icon'}).img['alt']
                # 티어 아이콘 URL
                tierIcon = 'https:' + bs.find('div', {'class': 'profile__tier__icon'}).img[
                    'src']  # Unranked -> 배치안된경우 필터링

                # 티어 정보
                tierInfo = bs.find('div', {'class': 'profile__tier__icon'}).img['alt']
                # lp
                lpInfo = bs.find('span', {'class': 'profile__tier__summary__lp'}).text
                # 상위 백분율
                toppercent = bs.find('span', {'class': 'top-percent'}).text.strip()
                # 전체 등수
                rankplace = bs.find('span', {'class': 'rank-region'}).text.strip()
                statsli = self.returnStatsTFT(bs)
                satatsPercentage = self.returnStatsPercentage(bs)

                #Most used Synergy

                mostSyn = bs.find('div',{'class' : 'profile__recent__trends__traits'}).table.tbody.findAll('tr')[0]
                synergyName = mostSyn.findAll('td')
                synergyInfo = []
                for sf in synergyName:
                    synergyInfo.append(sf.text.strip())

                #[Synergy Name , 1성조합횟수,2성조합횟수,3성조합횟수,게임수,승률(=1등),Top비율 (=Top4비율)]


                AveragePlace = bs.find('dl', {'class': re.compile('average average-[0-9]*')}).dd.text
                recentNumberofGame = bs.find('div', {'class': 'profile__placements'}).h4.text.strip()
                embed = discord.Embed(title="Team Fight Tactics player stats from lolchess.gg", description="", color=0x5CD1E5)
                embed.add_field(name="Click on the link below to view more information",
                                value=playerInfoURL,
                                inline=False)
                embed.add_field(name="Rank Information",
                                value=tierInfo + "(" + lpInfo + ")" + " | " + toppercent + " | " + "Ranking : " + rankplace,
                                inline=False)
                embed.add_field(name="Most used Synergy : "+synergyInfo[0],
                                value="Use : "+synergyInfo[4] + " time(s) | " + "1st place Ratio : " + synergyInfo[-2] + " | Top4 Ratio : " + synergyInfo[-1],
                                inline=False)
                embed.add_field(name="Number of Win(#1)",
                                value=statsli[0] + "/" + satatsPercentage[0],
                                inline=True)
                embed.add_field(name="Win Ratio",
                                value=statsli[1] + "/" + satatsPercentage[1],
                                inline=True)
                embed.add_field(name="Number of Top 4(#4)",
                                value=statsli[2] + "/" + satatsPercentage[2],
                                inline=True)
                embed.add_field(name="Top 4 Ratio",
                                value=statsli[3] + "/" + satatsPercentage[3],
                                inline=True)
                embed.add_field(name="Number of game",
                                value=statsli[4] + "/" + satatsPercentage[4],
                                inline=True)
                embed.add_field(name="Average Place",
                                value=AveragePlace,
                                inline=True)
                embed.set_thumbnail(url=tierIcon)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("TFT player " + playerNicknameShow + "'s information search", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Nick name not exist", description="", color=0x5CD1E5)
            embed.add_field(name="해당 닉네임의 플레이어가 존재하지 않습니다.",value="플레이어 이름을 확인해 주세요",inline=False)
            embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
            await ctx.send("Error : Not existing nickname", embed=embed)

    @commands.command(name="배그솔로T", help="명령어 뒤에 배그 닉네임을 붙이시면 솔로큐(TPP) 전적을 보여드립니다!", usage="!배그솔로T [닉네임]")
    async def soloT(self, ctx, *name):
        print(name)
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로T : !배그솔로T [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section tpp"})
                if soloQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Solo que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s TPP solo que information", embed=embed)
                else:
                    # print(soloQueInfo)
                    # Get total playtime
                    soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = soloQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    print(tierImage)
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in soloQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in soloQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server / Total playtime : " +soloQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier / Top Rate / Average Rank",
                                    value=tier + " ("+rankPoint+"p)" +" / " + comInfopercentage[0] + " / " + comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s TPP solo que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer", description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="배그듀오T", help="명령어 뒤에 배그 닉네임을 붙이시면 듀오(TPP) 전적을 보여드립니다!", usage="!배그듀오T [닉네임]")
    async def duoT(self, ctx, *name):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그듀오T : !배그듀오T [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                duoQueInfo = bs.find('section',{'class' : "duo modeItem"}).find('div',{'class' : "mode-section tpp"})
                if duoQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Duo que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s TPP duo que information", embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = duoQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in duoQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in duoQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server and total playtime", value=seasonInfo[2] + " Server / Total playtime : " +duoQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier(Rank Point) / Top Rate / Average Rank",
                                    value=tier + " ("+rankPoint+"p)" +" / " + comInfopercentage[0] + " / " + comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s TPP duo que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="배그스쿼드T", help="명령어 뒤에 배그 닉네임을 붙이시면 스쿼드(TPP) 전적을 보여드립니다!", usage="!배그스쿼드T [닉네임]")
    async def squadT(self, ctx, *name):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그스쿼드T : !배그스쿼드T [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                squadQueInfo = bs.find('section',{'class' : "squad modeItem"}).find('div',{'class' : "mode-section tpp"})
                if squadQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Squad que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s TPP squad que information", embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = squadQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in squadQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in squadQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server", value=seasonInfo[2] + " Server / Total playtime : " +squadQueTotalPlayTime, inline=False)
                    embed.add_field(name="Tier(Rank Point) / Top Rate / Average Rank",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s TPP squad que information", embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="배그솔로F", help="명령어 뒤에 배그 닉네임을 붙이시면 솔로큐(FPP) 전적을 보여드립니다!", usage="!배그솔로F [닉네임]")
    async def soloF(self, ctx, *name):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그솔로F : !배그솔로F [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                soloQueInfo = bs.find('section', {'class': "solo modeItem"}).find('div', {'class': "mode-section fpp"})
                if soloQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Solo que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s FPP solo que information",
                                               embed=embed)
                else:
                    # print(soloQueInfo)
                    # Get total playtime
                    soloQueTotalPlayTime = soloQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    soloQueGameWL = soloQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = soloQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = soloQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    print(tierImage)
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in soloQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in soloQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server",
                                    value=seasonInfo[2] + " Server / Total playtime : " + soloQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="Tier / Top Rate / Average Rank",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s FPP solo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="배그듀오F", help="명령어 뒤에 배그 닉네임을 붙이시면 듀오(FPP) 전적을 보여드립니다!", usage="!배그듀오F [닉네임]")
    async def duoF(self, ctx, *name):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그듀오F : !배그듀오F [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                duoQueInfo = bs.find('section', {'class': "duo modeItem"}).find('div', {'class': "mode-section fpp"})
                if duoQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Duo que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s FPP duo que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    duoQueTotalPlayTime = duoQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    duoQueGameWL = duoQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = duoQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = duoQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in duoQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in duoQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server and total playtime",
                                    value=seasonInfo[2] + " Server / Total playtime : " + duoQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="Tier(Rank Point) / Top Rate / Average Rank",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s FPP duo que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="배그스쿼드F", help="명령어 뒤에 배그 닉네임을 붙이시면 스쿼드(FPP) 전적을 보여드립니다!", usage="!배그스쿼드F [닉네임]")
    async def squadF(self, ctx, *name):
        baseURL = "https://dak.gg/profile/"
        playerNickname = ''.join(name)
        URL = baseURL + quote(playerNickname)
        try:
            if name == ():
                embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
                embed.add_field(name="Player nickname not entered",
                                value="To use command !배그스쿼드F : !배그스쿼드F [닉네임]", inline=False)
                embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                await ctx.send("Error : Incorrect command usage ", embed=embed)

            else:
                html = urlopen(URL)
                bs = BeautifulSoup(html, 'html.parser')
                accessors = bs.findAll('a', {'href': re.compile('\/statistics\/[A-Za-z]')})

                # Season Information : ['PUBG',(season info),(Server),'overview']
                seasonInfo = []
                for si in bs.findAll('li', {'class': "active"}):
                    seasonInfo.append(si.text.strip())
                serverAccessorAndStatus = []
                # To prevent : Parsing Server Status, Make a result like Server:\nOnline. So I need to delete '\n'to get good result
                for a in accessors:
                    serverAccessorAndStatus.append(re.sub(pattern='[\n]', repl="", string=a.text.strip()))

                # Varaible serverAccessorAndStatus : [(accessors),(ServerStatus),(Don't needed value)]

                squadQueInfo = bs.find('section', {'class': "squad modeItem"}).find('div',
                                                                                    {'class': "mode-section fpp"})
                if squadQueInfo == None:
                    embed = discord.Embed(title="Record not found", description="Squad que record not found.",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    await ctx.send("PUBG player " + playerNickname + "'s FPP squad que information",
                                               embed=embed)
                else:
                    # print(duoQueInfo)
                    # Get total playtime
                    squadQueTotalPlayTime = squadQueInfo.find('span', {'class': "time_played"}).text.strip()
                    # Get Win/Top10/Lose : [win,top10,lose]
                    squadQueGameWL = squadQueInfo.find('em').text.strip().split(' ')
                    # RankPoint
                    rankPoint = squadQueInfo.find('span', {'class': 'value'}).text
                    # Tier image url, tier
                    tierInfos = squadQueInfo.find('img', {
                        'src': re.compile('\/\/static\.dak\.gg\/images\/icons\/tier\/[A-Za-z0-9_.]')})
                    tierImage = "https:" + tierInfos['src']
                    tier = tierInfos['alt']

                    # Comprehensive info
                    comInfo = []
                    # [K/D,승률,Top10,평균딜량,게임수, 최다킬수,헤드샷,저격거리,생존,평균순위]
                    for ci in squadQueInfo.findAll('p', {'class': 'value'}):
                        comInfo.append(ci.text.strip())
                    comInfopercentage = []
                    # [전체 상위 %, K/D,승률,Top10,평균딜량,게임수,최다킬수,헤드샷,저격,생존,None]
                    for cif in squadQueInfo.findAll('span', {'class': 'top'}):
                        comInfopercentage.append((cif.text))

                    embed = discord.Embed(title="PlayerUnknown BattleGround player search from dak.gg", description="",
                                          color=0x5CD1E5)
                    embed.add_field(name="Player search from dak.gg", value=URL, inline=False)
                    embed.add_field(name="Real Time Accessors and Server Status",
                                    value="Accessors : " + serverAccessorAndStatus[0] + " | " "Server Status : " +
                                          serverAccessorAndStatus[1].split(':')[-1], inline=False)
                    embed.add_field(name="Player located server",
                                    value=seasonInfo[2] + " Server / Total playtime : " + squadQueTotalPlayTime,
                                    inline=False)
                    embed.add_field(name="Tier(Rank Point) / Top Rate / Average Rank",
                                    value=tier + " (" + rankPoint + "p)" + " / " + comInfopercentage[0] + " / " +
                                          comInfo[-1], inline=False)
                    embed.add_field(name="K/D", value=comInfo[0] + "/" + comInfopercentage[1], inline=True)
                    embed.add_field(name="승률", value=comInfo[1] + "/" + comInfopercentage[2], inline=True)
                    embed.add_field(name="Top 10 비율", value=comInfo[2] + "/" + comInfopercentage[3], inline=True)
                    embed.add_field(name="평균딜량", value=comInfo[3] + "/" + comInfopercentage[4], inline=True)
                    embed.add_field(name="게임수", value=comInfo[4] + "판/" + comInfopercentage[5], inline=True)
                    embed.add_field(name="최다킬수", value=comInfo[5] + "킬/" + comInfopercentage[6], inline=True)
                    embed.add_field(name="헤드샷 비율", value=comInfo[6] + "/" + comInfopercentage[7], inline=True)
                    embed.add_field(name="저격거리", value=comInfo[7] + "/" + comInfopercentage[8], inline=True)
                    embed.add_field(name="평균생존시간", value=comInfo[8] + "/" + comInfopercentage[9], inline=True)
                    embed.set_thumbnail(url=tierImage)
                    embed.set_footer(text="Service provided by Hoplin, Edited by 201911218 천성필")
                    await ctx.send("PUBG player " + playerNickname + "'s FPP squad que information",
                                               embed=embed)
        except HTTPError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)
        except AttributeError as e:
            embed = discord.Embed(title="Not existing plyer",
                                  description="Can't find player " + playerNickname + "'s information.\nPlease check player's nickname again",
                                  color=0x5CD1E5)
            await ctx.send("Error : Not existing player", embed=embed)

    @commands.command(name="메이플", help="명령어 뒤에 메이플스토리 닉네임을 붙이시면 캐릭터 정보를 알려드려요!", usage="!메이플 [닉네임]")
    async def maple(self, ctx, name : str = None):
        # Maplestroy base link
        mapleLink = "https://maplestory.nexon.com"
        # Maplestory character search base link
        mapleCharacterSearch = "https://maplestory.nexon.com/Ranking/World/Total?c="
        mapleUnionLevelSearch = "https://maplestory.nexon.com/Ranking/Union?c="

        playerNickname = name
        html = urlopen(mapleCharacterSearch + quote(playerNickname))  # Use quote() to prevent ascii error
        bs = BeautifulSoup(html, 'html.parser')

        html2 = urlopen(mapleUnionLevelSearch + quote(playerNickname))
        bs2 = BeautifulSoup(html2,'html.parser')

        if name is None:
            embed = discord.Embed(title="닉네임이 입력되지 않았습니다", description="", color=0x5CD1E5)
            embed.add_field(name="Player nickname not entered",
                            value="To use command !메이플 : !메이플 (Nickname)", inline=False)
            embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
            await ctx.send("Error : Incorrect command usage ", embed=embed)

        elif bs.find('tr', {'class': 'search_com_chk'}) == None:
            embed = discord.Embed(title="Nickname not exist", description="", color=0x5CD1E5)
            embed.add_field(name="해당 닉네임의 플레이어가 존재하지 않습니다.", value="플레이어 이름을 확인해주세요", inline=False)
            embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
            await ctx.send("Error : Non existing Summoner ", embed=embed)

        else:
            # Get to the character info page
            characterRankingLink = bs.find('tr', {'class': 'search_com_chk'}).find('a', {'href': re.compile('\/Common\/Character\/Detail\/[A-Za-z0-9%?=]*')})['href']
            #Parse Union Level
            characterUnionRanking = bs2.find('tr', {'class': 'search_com_chk'})
            if characterUnionRanking == None:
                pass
            else:
                characterUnionRanking = characterUnionRanking.findAll('td')[2].text
            html = urlopen(mapleLink + characterRankingLink)
            bs = BeautifulSoup(html, 'html.parser')

            # Find Ranking page and parse page
            personalRankingPageURL = bs.find('a', {'href': re.compile('\/Common\/Character\/Detail\/[A-Za-z0-9%?=]*\/Ranking\?p\=[A-Za-z0-9%?=]*')})['href']
            html = urlopen(mapleLink + personalRankingPageURL)
            bs = BeautifulSoup(html, 'html.parser')
            #Popularity

            popularityInfo = bs.find('span',{'class' : 'pop_data'}).text.strip()
            ''' Can't Embed Character's image. Gonna fix it after patch note
            #Character image
            getCharacterImage = bs.find('img',{'src': re.compile('https\:\/\/avatar\.maplestory\.nexon\.com\/Character\/[A-Za-z0-9%?=/]*')})['src']
            '''
            infoList = []
            # All Ranking information embeded in <dd> elements
            RankingInformation = bs.findAll('dd')  # [level,job,servericon,servername,'-',comprehensiveRanking,'-',WorldRanking,'-',JobRanking,'-',Popularity Ranking,'-',Maple Union Ranking,'-',Achivement Ranking]
            for inf in RankingInformation:
                infoList.append(inf.text)
            embed = discord.Embed(title="Player " + playerNickname + "'s information search from nexon.com", description=infoList[0] + " | " +infoList[1] + " | " + "Server : " + infoList[2], color=0x5CD1E5)
            embed.add_field(name="Click on the link below to view more information.", value = mapleLink + personalRankingPageURL, inline=False)
            embed.add_field(name="Overall Ranking",value=infoList[4], inline=True)
            embed.add_field(name="World Ranking", value=infoList[6], inline=True)
            embed.add_field(name="Job Ranking", value=infoList[8], inline=True)
            embed.add_field(name="Popularity Ranking", value=infoList[10] + "( " +popularityInfo + " )", inline=True)
            if characterUnionRanking == None:
                embed.add_field(name="Maple Union", value=infoList[12],inline=True)
            else:
                embed.add_field(name="Maple Union", value=infoList[12] + "( LV." + characterUnionRanking + " )", inline=True)
            embed.add_field(name="Achivement Ranking", value=infoList[14], inline=True)
            embed.set_thumbnail(url='https://ssl.nx.com/s2/game/maplestory/renewal/common/logo.png')
            embed.set_footer(text='Service provided by Hoplin, Edited by 201911218 천성필')
            await ctx.send("Player " + playerNickname +"'s information search", embed=embed)

def setup(bot):
    bot.add_cog(Game_Record_Search(bot))