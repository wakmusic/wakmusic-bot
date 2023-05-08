import json
import sqlite3
import time
import discord
from aiohttp import ClientSession
from datetime import datetime, timedelta, timezone
import pymysql


# from pytz import timezone


class NoticeForm(discord.ui.Modal):
    def __init__(self):
        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        super().__init__(title='공지 등록', custom_id="notice-create")
        self.add_item(discord.ui.InputText(placeholder="카테고리를 입력해 주세요.", label="카테고리",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="제목을 입력해 주세요.", label="제목",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="본문을 입력해 주세요.", label="본문",
                                           style=discord.InputTextStyle.long, required=True, value=None))
        self.add_item(
            discord.ui.InputText(placeholder="이미지 URL을 입력해 주세요.(첫번째 이미지는 썸네일로 등록, 줄바꿈으로 여러 이미지 등록)", label="이미지 URL",
                                 style=discord.InputTextStyle.long, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="시작 날짜를 적어주세요 (ex: 2023-04-05)", label="시작 날짜",
                                           style=discord.InputTextStyle.short, required=True, value=None))

    async def callback(self, interaction: discord.Interaction):
        conn = pymysql.connect(host=self.js['database_host'], port=self.js['database_port'],
                               user=self.js['database_user_id'],
                               password=self.js['database_user_password'], database='static')
        cursor = conn.cursor()
        timezone_kst = timezone(timedelta(hours=9))

        category = self.children[0].value
        title = self.children[1].value
        main_text = self.children[2].value
        thumbnail = None
        images = self.children[3].value.split('\n')
        start_date = self.children[4].value
        period = 7

        current_time = int(datetime.utcnow().astimezone(timezone_kst).timestamp() * 1000)
        # current_time = int(datetime.utcnow().timestamp() * 1000)

        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=timezone_kst)
        # start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
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

            if image_count == 1:
                thumbnail = f'{current_time}-{image_count}.png'
            else:
                added.append(f'{current_time}-{image_count}.png')
            image_count += 1

        cursor.execute(
            'INSERT INTO notice (category, title, main_text, thumbnail, images, create_at, start_at, end_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
            (category, title, main_text, thumbnail, ','.join(added), current_time, start_time, end_time))
        conn.commit()

        cursor.execute(f'SELECT * FROM notice WHERE create_at = {current_time}')
        added = cursor.fetchone()

        cursor.close()
        conn.close()
        return await interaction.response.send_message(f'{title}(`{added[0]}`) 공지가 추가되었습니다.')
