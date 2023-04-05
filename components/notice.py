import json
import sqlite3
import time
import discord
from aiohttp import ClientSession
from datetime import datetime, timedelta
from pytz import timezone


class NoticeForm(discord.ui.Modal):
    def __init__(self):
        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        super().__init__(title='공지 등록', custom_id="notice-create")
        self.add_item(discord.ui.InputText(placeholder="카테고리를 입력해 주세요.", label="카테고리",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="제목을 입력해 주세요.", label="제목",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="이미지 URL을 입력해 주세요.(줄바꿈으로 여러 이미지 등록)", label="이미지 URL",
                                           style=discord.InputTextStyle.long, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="시작 날짜를 적어주세요 (ex: 2023-04-05)", label="시작 날짜",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="노출 기간을 일 단위로 적어주세요 (ex: 10)", label="노출 기간",
                                           style=discord.InputTextStyle.short, required=True, value=None))

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.js['database_src'] + 'static.db')
        cursor = conn.cursor()

        category = self.children[0].value
        title = self.children[1].value
        images = self.children[2].value.split('\n')
        start_date = self.children[3].value
        period = self.children[4].value

        current_time = int(datetime.now(tz=timezone('Asia/Seoul')).timestamp() * 1000)

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').astimezone(timezone('Asia/Seoul'))
        end_date_obj = start_date_obj + timedelta(days=int(period))

        start_time = int(start_date_obj.timestamp() * 1000)
        end_time = int(end_date_obj.timestamp() * 1000)

        image_count = 1
        added = []
        for image in images:
            async with ClientSession() as session:
                async with session.get(image) as res:
                    data = await res.read()

            with open(f'../wakmusic/src/images/notice/{current_time}-{image_count}.png', 'wb') as f:
                f.write(data)
            added.append(f'{current_time}-{image_count}.png')
            image_count += 1

        cursor.execute(
            'INSERT INTO notice (category, title, images, create_at, start_at, end_at) VALUES (?, ?, ?, ?, ?, ?)',
            (category, title, ','.join(added), current_time, start_time, end_time))
        conn.commit()
        added = cursor.execute(f'SELECT * FROM notice WHERE create_at = {current_time}').fetchone()
        conn.close()

        return await interaction.response.send_message(f'{title}(`{added[0]}`) 공지가 추가되었습니다.')
