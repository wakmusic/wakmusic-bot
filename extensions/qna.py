import json
import sqlite3
import pymysql
import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup
from components import QNAForm

with open('config.json', encoding='utf-8-sig') as file:
    js = json.load(file)


class QnA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("질문", "자주 묻는 질문 관련 명령어")

    @staticmethod
    def check_perms(ctx):
        if 984724942702665758 in [r.id for r in ctx.author.roles]:
            return True
        else:
            return False

    @group.command(name='추가', description='질문을 추가합니다.')
    async def qna_add(self, ctx):
        if self.check_perms(ctx):
            return await ctx.interaction.response.send_modal(QNAForm())
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='변경', description='질문을 변경합니다.')
    async def qna_chg(self, ctx, qid: Option(int, "식별 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            return await ctx.interaction.response.send_modal(QNAForm(qid))
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='삭제', description='질문을 삭제합니다.')
    async def qna_rem(self, ctx, qid: Option(str, "식별 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='static')
            cursor = conn.cursor()

            cursor.execute(f'SELECT * FROM qna WHERE id = "{qid}"')
            current = cursor.fetchone()
            if not current:
                return await ctx.respond("존재하지 않는 질문입니다.")

            cursor.execute(f'DELETE FROM qna WHERE id = "{qid}"')
            conn.commit()

            cursor.close()
            conn.close()
            return await ctx.respond(f"{current[2]}(`{qid}`)(을)를 삭제하였습니다.")
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='목록', description='질문 목록을 확인합니다.')
    async def qna_list(self, ctx):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='static')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM qna')
            data = cursor.fetchall()

            embed = discord.Embed(title="질문 목록")
            for d in data:
                embed.add_field(name=f"{d[2]}(`{d[0]}`)", value=f"생성 시각: <t:{d[4]}>\n카테고리: {d[1]}\n답변:\n```{d[3]}```", inline=False)

            cursor.close()
            conn.close()
            return await ctx.respond(embed=embed)

        return await ctx.respond("권한이 없습니다.")

    @group.command(name='카테고리목록', description='Q&A 카테고리목록을 가져옵니다.')
    async def not_categories(self, ctx):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='static')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM categories WHERE type="qna"')
        data = cursor.fetchall()

        embed = discord.Embed(title='Q&A 카테고리 목록')
        embed.add_field(name='카테고리', value=data[0][2])

        cursor.close()
        conn.close()
        return await ctx.respond(embed=embed)

    @group.command(name='카테고리추가', description='Q&A 카테고리를 추가합니다.')
    async def not_categories(self, ctx, category: Option(str, '카테고리를 입력해주세요.')):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='static')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM categories WHERE type="qna"')
        data = cursor.fetchall()

        categories = data[0][2].split(',')
        if category in categories:
            return await ctx.respond("이미 존재하는 카테고리 입니다.")

        categories.append(category)

        cursor.execute(f'UPDATE categories SET categories="{",".join(categories)}" WHERE type="qna"')
        conn.commit()

        cursor.close()
        conn.close()
        return await ctx.respond(f"`{category}` 가 Q&A 카테고리에 추가되었습니다.")

    @group.command(name='카테고리삭제', description='Q&A 카테고리를 삭제합니다.')
    async def not_categories(self, ctx, category: Option(str, '카테고리를 입력해주세요.')):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='static')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM categories WHERE type="qna"')
        data = cursor.fetchall()

        categories = data[0][2].split(',')
        if category not in categories:
            return await ctx.respond("존재하지 않는 카테고리 입니다.")

        categories.remove(category)

        cursor.execute(f'UPDATE categories SET categories="{",".join(categories)}" WHERE type="qna"')
        conn.commit()

        cursor.close()
        conn.close()
        return await ctx.respond(f"`{category}` 가 Q&A 카테고리에서 삭제되었습니다.")


def setup(bot):
    bot.add_cog(QnA(bot))
