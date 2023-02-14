import json
import sqlite3
import discord
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

    @group.command(name='목록', description='공지 목록을 확인합니다.')
    async def not_list(self, ctx):
        if self.check_perms(ctx):
            cursor = sqlite3.connect(js['database_src'] + 'static.db').cursor()
            data = cursor.execute('SELECT * FROM notice').fetchall()

            embed = discord.Embed(title="공지 목록")
            for d in data:
                embed.add_field(name=f"{d[2]}(`{d[0]}`)", value=f"생성 시각: <t:{d[4]}>\n카테고리: {d[1]}", inline=False)
            return await ctx.respond(embed=embed)

        return await ctx.respond("권한이 없습니다.")

    @group.command(name='카테고리목록', description='공지 카테고리목록을 가져옵니다.')
    async def not_categories(self, ctx):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        cursor = sqlite3.connect(js['database_src'] + 'static.db').cursor()
        data = cursor.execute('SELECT * FROM categories WHERE type="notice"').fetchall()

        embed = discord.Embed(title='공지 카테고리 목록')
        embed.add_field(name='카테고리', value=data[0][2])

        return await ctx.respond(embed=embed)

    @group.command(name='카테고리추가', description='공지 카테고리를 추가합니다.')
    async def not_categories(self, ctx, category: Option(str, '카테고리를 입력해주세요.')):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = sqlite3.connect(js['database_src'] + 'static.db')
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM categories WHERE type="notice"').fetchall()

        categories = data[0][2].split(',')
        if category in categories:
            return await ctx.respond("이미 존재하는 카테고리 입니다.")

        categories.append(category)

        cursor.execute(f'UPDATE categories SET categories="{",".join(categories)}" WHERE type="notice"')
        conn.commit()
        conn.close()

        return await ctx.respond(f"`{category}` 가 공지 카테고리에 추가되었습니다.")

    @group.command(name='카테고리삭제', description='공지 카테고리를 삭제합니다.')
    async def not_categories(self, ctx, category: Option(str, '카테고리를 입력해주세요.')):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = sqlite3.connect(js['database_src'] + 'static.db')
        cursor = conn.cursor()
        data = cursor.execute('SELECT * FROM categories WHERE type="notice"').fetchall()

        categories = data[0][2].split(',')
        if category not in categories:
            return await ctx.respond("존재하지 않는 카테고리 입니다.")

        categories.remove(category)

        cursor.execute(f'UPDATE categories SET categories="{",".join(categories)}" WHERE type="notice"')
        conn.commit()
        conn.close()

        return await ctx.respond(f"`{category}` 가 공지 카테고리에서 삭제되었습니다.")


def setup(bot):
    bot.add_cog(Notice(bot))
