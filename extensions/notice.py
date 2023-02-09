import json
import sqlite3
from discord.ext import commands
from discord import Option, SlashCommandGroup
from components import NoticeForm

with open('config.json', encoding='utf-8-sig') as file:
    js = json.load(file)


class Notice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("공지", "공지 관련 명령어")

    @staticmethod
    def check_perms(ctx):
        if 984724942702665758 in [r.id for r in ctx.author.roles]:
            return True
        else:
            return False

    @group.command(name='등록', description='공지를 등록합니다.')
    async def not_add(self, ctx):
        if self.check_perms(ctx):
            return await ctx.interaction.response.send_modal(NoticeForm())
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='삭제', description='공지를 삭제합니다.')
    async def not_rem(self, ctx, nid: Option(int, "공지 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            conn = sqlite3.connect(js['database_src'] + 'static.db')
            cursor = conn.cursor()

            current = cursor.execute(f'SELECT * FROM notice WHERE id = "{nid}"').fetchone()
            if not current:
                return await ctx.respond("존재하지 않는 공지입니다.")

            cursor.execute(f'DELETE FROM notice WHERE id = "{nid}"')
            conn.commit()
            conn.close()
            return await ctx.respond(f"{current[2]}(`{nid}`)(을)를 삭제하였습니다.")
        return await ctx.respond("권한이 없습니다.")


def setup(bot):
    bot.add_cog(Notice(bot))
