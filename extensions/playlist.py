import json
import sqlite3
import pymysql
import discord
from discord.ext import commands
from discord import Option, SlashCommandGroup
from aiohttp import ClientSession
from components import PlForm

with open('config.json', encoding='utf-8-sig') as file:
    js = json.load(file)


class Playlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("재생목록", "추천 재생목록 관련 명령어")

    @staticmethod
    def check_perms(ctx):
        if 984724942702665758 in [r.id for r in ctx.author.roles]:
            return True
        else:
            return False

    @group.command(name='추가', description='추천 재생목록을 추가합니다.')
    async def pl_add(self, ctx):
        if self.check_perms(ctx):
            form = PlForm()
            return await ctx.interaction.response.send_modal(form)
        return await ctx.respond("권한이 없습니다.")

    @staticmethod
    def convert_str(v: int):
        if v == 0:
            return "비공개"
        return "공개"

    @group.command(name='목록', description='추천 재생목록을 모두 불러옵니다.')
    async def pl_list(self, ctx):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='like')
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM playlist')
            pls = cursor.fetchall()

            embed = discord.Embed(title=f"추천 재생목록")
            for pl in pls:
                embed.add_field(name=f"{pl[1]}(`{pl[0]}`)", value=f"`{self.convert_str(pl[3])}` | {len(pl[2].split(','))}곡", inline=False)

            cursor.close()
            conn.close()
            return await ctx.respond(embed=embed)
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='공개설정', description='재생목록 공개 여부를 전환합니다.')
    async def pl_pub(self, ctx, pid: Option(str, "재생목록 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='like')
            cursor = conn.cursor()

            cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"')
            current = cursor.fetchone()
            if not current:
                return await ctx.respond("존재하지 않는 재생목록입니다.")

            c, s = 0, "비공개"
            if current[3] == 0:
                c, s = 1, "공개"

            cursor.execute(f'UPDATE playlist SET public = "{c}" WHERE id = "{pid}"')
            conn.commit()

            cursor.close()
            conn.close()
            return await ctx.respond(f"{current[1]}(`{pid}`)(을)를 {s} 상태로 설정하였습니다.")
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='삭제', description='추천 재생목록을 삭제합니다.')
    async def pl_rem(self, ctx, pid: Option(str, "재생목록 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                                   password=js['database_user_password'], database='like')
            cursor = conn.cursor()

            cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"')
            current = cursor.fetchone()
            if not current:
                return await ctx.respond("존재하지 않는 재생목록입니다.")

            cursor.execute(f'DELETE FROM playlist WHERE id = "{pid}"')
            conn.commit()

            cursor.close()
            conn.close()
            return await ctx.respond(f"{current[1]}(`{pid}`)(을)를 삭제하였습니다.")
        return await ctx.respond("권한이 없습니다.")

    @group.command(name='곡추가', description='재생목록에 노래를 추가합니다.')
    async def pl_s_add(self, ctx, pid: Option(str, "재생목록 ID를 입력해 주세요"),
                       sid: Option(str, "추가할 노래의 ID를 입력해 주세요")):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        s_conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='charts')
        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='like')
        s_cursor = s_conn.cursor()
        cursor = conn.cursor()

        s_cursor.execute('SELECT * FROM total')
        songs = [s[0] for s in s_cursor.fetchall()]
        s_cursor.close()
        s_conn.close()

        if sid not in songs:
            return await ctx.respond("존재하지 않는 노래 ID입니다.")

        cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"')
        current = cursor.fetchone()
        if not current:
            return await ctx.respond("존재하지 않는 재생목록입니다.")

        ids = current[2].split(',')
        if sid in ids:
            return await ctx.respond("이미 재생목록에 추가된 노래입니다.")
        ids.append(sid)

        cursor.execute(f'UPDATE playlist SET song_ids = "{",".join(ids).strip(",")}" WHERE id = "{pid}"')
        conn.commit()

        cursor.close()
        conn.close()
        return await ctx.respond(f"{sid}(이)가 {current[1]}에 추가되었습니다.")

    @group.command(name='곡목록', description='재생목록의 노래 목록을 불러옵니다.')
    async def pl_s_list(self, ctx, pid: Option(str, "재생목록 ID를 입력해 주세요")):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        s_conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='charts')
        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='like')
        s_cursor = s_conn.cursor()
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"')
        current = cursor.fetchone()
        if not current:
            return await ctx.respond("존재하지 않는 재생목록입니다.")

        ids = '", "'.join(current[2].split(','))
        s_cursor.execute(f'SELECT * FROM total WHERE id IN ("{ids}")')
        results = s_cursor.fetchall()

        embed = discord.Embed(title=f"{current[1]} 곡 목록")
        for r in results:
            embed.add_field(name=f"{r[1]}(`{r[0]}`)", value=f"{r[2]} / {r[5]}", inline=False)

        s_cursor.close()
        cursor.close()

        s_conn.close()
        conn.close()
        try:
            return await ctx.respond(embed=embed)
        except discord.HTTPException:
            return await ctx.respond(current[2])

    @group.command(name='곡삭제', description='재생목록에서 노래를 삭제합니다.')
    async def pl_s_rem(self, ctx, pid: Option(str, "재생목록 ID를 입력해 주세요"),
                       sid: Option(str, "삭제할 노래의 ID를 입력해 주세요")):
        if not self.check_perms(ctx):
            return await ctx.respond("권한이 없습니다.")

        conn = pymysql.connect(host=js['database_host'], port=js['database_port'], user=js['database_user_id'],
                               password=js['database_user_password'], database='like')
        cursor = conn.cursor()

        cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"')
        current = cursor.fetchone()
        if not current:
            return await ctx.respond("존재하지 않는 재생목록입니다.")

        ids = current[2].split(',')
        try:
            ids.remove(sid)
        except ValueError:
            return await ctx.respond("재생목록에 추가되지 않은 노래입니다.")

        cursor.execute(f'UPDATE playlist SET song_ids = "{",".join(ids)}" WHERE id = "{pid}"')
        conn.commit()

        cursor.close()
        conn.close()
        return await ctx.respond(f"{sid}(이)가 {current[1]}에서 삭제되었습니다.")

    @staticmethod
    async def upload(url: str, root: str):
        try:
            async with ClientSession() as session:
                async with session.get(url) as res:
                    data = await res.read()

            with open(root, 'wb') as f:
                f.write(data)
        except:
            return False
        return True

    @group.command(name='원형아이콘', description='추천 재생목록 아이콘(원형)을 업로드합니다.')
    async def pl_icon_rd(self, ctx, url: Option(str, "이미지 URL을 입력해 주세요"),
                         pid: Option(str, "재생목록 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            result = await self.upload(url, f'../wakmusic/src/images/pl-icons/round/{pid}.png')
            if not result:
                return await ctx.respond("오류가 발생하였습니다.")
            return await ctx.respond("아이콘을 업로드하였습니다.")

        return await ctx.respond("권한이 없습니다.")

    @group.command(name='사각아이콘', description='추천 재생목록 아이콘(사각형)을 업로드합니다.')
    async def pl_icon_sq(self, ctx, url: Option(str, "이미지 URL을 입력해 주세요"),
                         pid: Option(str, "재생목록 ID를 입력해 주세요")):
        if self.check_perms(ctx):
            result = await self.upload(url, f'../wakmusic/src/images/pl-icons/square/{pid}.png')
            if not result:
                return await ctx.respond("오류가 발생하였습니다.")
            return await ctx.respond("아이콘을 업로드하였습니다.")

        return await ctx.respond("권한이 없습니다.")


def setup(bot):
    bot.add_cog(Playlist(bot))
