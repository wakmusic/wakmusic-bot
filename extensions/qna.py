import json
import sqlite3

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
            conn = sqlite3.connect(js['database_src'] + 'static.db')
            cursor = conn.cursor()

            current = cursor.execute(f'SELECT * FROM qna WHERE id = "{qid}"').fetchone()
            if not current:
                return await ctx.respond("존재하지 않는 질문입니다.")

            cursor.execute(f'DELETE FROM qna WHERE id = "{qid}"')
            conn.commit()
            conn.close()
            return await ctx.respond(f"{current[2]}(`{qid}`)(을)를 삭제하였습니다.")
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='목록', description='질문 목록을 확인합니다.')
    async def qna_list(self, ctx):
        if self.check_perms(ctx):
            cursor = sqlite3.connect(js['database_src'] + 'static.db').cursor()
            data = cursor.execute('SELECT * FROM qna').fetchall()

            embed = discord.Embed(title="질문 목록")
            for d in data:
                embed.add_field(name=f"{d[2]}(`{d[0]}`)", value=f"생성 시각: <t:{d[4]}>\n카테고리: {d[1]}\n답변:\n```{d[3]}```", inline=False)
            return await ctx.respond(embed=embed)

        return await ctx.respond("권한이 없습니다.")


def setup(bot):
    bot.add_cog(QnA(bot))
