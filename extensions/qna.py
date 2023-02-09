import json
import sqlite3
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

    @group.command(name='추가', description='추천 재생목록을 추가합니다.')
    async def qna_add(self, ctx):
        if self.check_perms(ctx):
            return await ctx.interaction.response.send_modal(QNAForm())
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='변경', description='뉴스 정보를 변경합니다.')
    async def qna_chg(self, ctx, qid: Option(int, "식별 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            return await ctx.interaction.response.send_modal(QNAForm(qid))
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='삭제', description='추천 재생목록을 삭제합니다.')
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


def setup(bot):
    bot.add_cog(QnA(bot))
