import json
import sqlite3
import time
import discord
from aiohttp import ClientSession


class NoticeForm(discord.ui.Modal):
    def __init__(self):
        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        super().__init__(title='공지 등록', custom_id="notice-create")
        self.add_item(discord.ui.InputText(placeholder="공지 ID를 입력해 주세요(숫자).", label="공지 ID",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="카테고리를 입력해 주세요.", label="카테고리",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="제목을 입력해 주세요.", label="제목",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="이미지 URL을 입력해 주세요.(줄바꿈으로 여러 이미지 등록)", label="이미지 URL",
                                           style=discord.InputTextStyle.long, required=True, value=None))

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.js['database_src'] + 'static.db')
        cursor = conn.cursor()

        nid = self.children[0].value
        category = self.children[1].value
        title = self.children[2].value
        images = self.children[3].value.split('\n')

        exist = cursor.execute(f'SELECT * FROM notice WHERE id = "{nid}"').fetchone()
        if exist:
            return await interaction.response.send_message('이미 추가된 공지입니다.')

        added = []
        for image in images:
            image_time = time.time()
            async with ClientSession() as session:
                async with session.get(image) as res:
                    data = await res.read()

            with open(f'../wakmusic/src/images/notice/{image_time}.png', 'wb') as f:
                f.write(data)
            added.append(f'{image_time}.png')

        created = int(time.time())
        cursor.execute('INSERT INTO notice VALUES (?, ?, ?, ?, ?)', (nid, category, title, ','.join(added), created))
        conn.commit()
        conn.close()
        return await interaction.response.send_message(f'{title}(`{nid}`) 공지가 추가되었습니다.')
