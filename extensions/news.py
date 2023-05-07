import json
import sqlite3
from discord.ext import commands
from discord import Option, SlashCommandGroup
from aiohttp import ClientSession
from components import NewsForm
import pymysql

with open('config.json', encoding='utf-8-sig') as file:
    js = json.load(file)


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("뉴스", "뉴스 관련 명령어")

    @staticmethod
    def check_perms(ctx):
        if 984724942702665758 in [r.id for r in ctx.author.roles]:
            return True
        else:
            return False

    @group.command(name='추가', description='뉴스를 추가합니다.')
    async def news_add(self, ctx):
        if self.check_perms(ctx):
            form = NewsForm()
            return await ctx.interaction.response.send_modal(form)
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='삭제', description='뉴스를 삭제합니다.')
    async def news_rem(self, ctx, news: Option(str, "삭제할 뉴스의 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='static')
            cursor = conn.cursor()
            # conn = sqlite3.connect(js['database_src'] + 'static.db')
            # cursor = conn.cursor()

            cursor.execute(f'DELETE FROM news WHERE id = "{news}"')
            conn.commit()

            cursor.close()
            conn.close()
            return await ctx.respond(f"`{news}`(을)를 삭제하였습니다.")
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='변경', description='뉴스 정보를 변경합니다.')
    async def news_chg(self, ctx, news: Option(str, "변경할 뉴스의 URL을 입력해 주세요")):
        if self.check_perms(ctx):
            form = NewsForm(news)
            return await ctx.interaction.response.send_modal(form)
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='이미지', description='뉴스 썸네일을 업로드합니다.')
    async def news_img(self, ctx, url: Option(str, "이미지 URL을 입력해 주세요"),
                       time: Option(str, "시간을 입력해 주세요(2022061 = 22년 6월 1주차)")):
        if self.check_perms(ctx):
            async with ClientSession() as session:
                async with session.get(url) as res:
                    data = await res.read()

            with open(f'../wakmusic/src/images/news/{time}.png', 'wb') as f:
                f.write(data)

            return await ctx.respond(f"이미지를 업로드하였습니다.")
        return await ctx.respond("권한이 없습니다.")


def setup(bot):
    bot.add_cog(News(bot))
