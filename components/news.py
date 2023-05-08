import json
import sqlite3
import discord
import pymysql


class NewsForm(discord.ui.Modal):
    def __init__(self, news=None):
        self.news = news

        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        if news:
            conn = pymysql.connect(host=self.js['database_host'], port=self.js['database_port'],
                                   user=self.js['database_user_id'],
                                   password=self.js['database_user_password'], database='static')
            cursor = conn.cursor()

            cursor.execute(f'SELECT * FROM news WHERE id = "{news}"')
            data = cursor.fetchone()

            cursor.close()
            conn.close()

            article = data[0]
            subject = data[1]
            time = data[2]
        else:
            article, subject, time = None, None, None

        super().__init__(title='뉴스', custom_id="news")
        self.add_item(discord.ui.InputText(placeholder="카페 게시글 ID를 입력해 주세요", label="게시글 ID",
                                           style=discord.InputTextStyle.short, required=True, value=article))
        self.add_item(discord.ui.InputText(placeholder="뉴스 제목을 입력해 주세요", label="뉴스 제목",
                                           style=discord.InputTextStyle.short, required=True, value=subject))
        self.add_item(discord.ui.InputText(placeholder="뉴스 주차를 입력해 주세요(20220610 = 22년 6월 1주차 이세돌포커스)",
                                           label="뉴스 주차", style=discord.InputTextStyle.short, required=True, value=time))

    async def callback(self, interaction: discord.Interaction):
        conn = pymysql.connect(host=self.js['database_host'], port=self.js['database_port'],
                               user=self.js['database_user_id'],
                               password=self.js['database_user_password'], database='static')
        cursor = conn.cursor()

        article = self.children[0].value.split('/')[-1]
        subject = self.children[1].value
        time = self.children[2].value

        if self.news:
            cursor.execute(f'UPDATE news SET id = "{article}", title = "{subject}", time = "{time}"'
                           f' WHERE id = "{article}"')
            conn.commit()

            cursor.close()
            conn.close()
            return await interaction.response.send_message(f'{subject}(`{article}`)(이)가 변경되었습니다.')

        cursor.execute(f'SELECT * FROM news WHERE id = "{article}"')
        exist = cursor.fetchone()
        if exist:
            return await interaction.response.send_message('이미 추가된 기사입니다.')

        cursor.execute('INSERT INTO news VALUES (%s, %s, %s)', (article, subject, f'{time}'))
        conn.commit()

        cursor.close()
        conn.close()

        root = '../wakmusic/src/images/news'
        with open(f'{root}/default.png', 'rb') as f:
            default = f.read()
        with open(f'{root}/{time}.png', 'wb') as f:
            f.write(default)

        return await interaction.response.send_message(f'{subject}(`{article}`) 기사가 추가되었습니다.')
