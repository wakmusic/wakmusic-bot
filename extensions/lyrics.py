import os
import shutil
import webvtt
from discord.ext import commands
from discord import Option, SlashCommandGroup
from aiohttp import ClientSession


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = SlashCommandGroup("가사", "가사 관련 명령어")

    @group.command(name='업로드', description='가사를 테스트 서버에 업로드합니다.')
    async def upload(self, ctx, url: Option(str, "파일 URL을 입력해 주세요"),
                     fid: Option(str, "노래 아이디를 입력해 주세요")):
        async with ClientSession() as session:
            async with session.get(url) as res:
                data = await res.read()

        if url.endswith('.srt'):
            filename = f'../wakmusic-lyrics/lyrics/{fid}.srt'
            with open(filename, 'wb') as f:
                f.write(data)

            try:
                webvtt.from_srt(filename).save()
            except:
                os.remove(filename)
                return await ctx.respond(".srt -> .vtt 변환에 실패하였습니다. 다시 시도해 주세요.")
            os.remove(filename)
        else:
            with open(f'../wakmusic-lyrics/lyrics/{fid}.srt', 'wb') as f:
                f.write(data)

        return await ctx.respond(f"가사가 테스트 서버에 업로드되었습니다.\n"
                                 f"검수 URL: <https://lyrics.wakmusic.xyz/{fid}>")

    @group.command(name='배포', description='검수 완료된 가사를 배포합니다.')
    async def publish(self, ctx, fid: Option(str, "노래 아이디를 입력해 주세요")):
        try:
            shutil.move(f"../wakmusic-lyrics/lyrics/{fid}.vtt", f"../wakmusic/src/lyrics/{fid}.vtt")
        except Exception as e:
            print(e)
            return await ctx.respond("오류가 발생하였습니다.")
        return await ctx.respond("가사를 성공적으로 배포하였습니다.")


def setup(bot):
    bot.add_cog(Lyrics(bot))
