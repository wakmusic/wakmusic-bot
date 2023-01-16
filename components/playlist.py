import json
import sqlite3
import discord


class PlForm(discord.ui.Modal):
    def __init__(self):
        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        super().__init__(title='재생목록 생성', custom_id="pl-create")
        self.add_item(discord.ui.InputText(placeholder="재생목록 ID를 입력해 주세요.", label="재생목록 ID",
                                           style=discord.InputTextStyle.short, required=True, value=None))
        self.add_item(discord.ui.InputText(placeholder="재생목록 제목을 입력해 주세요.", label="재생목록 제목",
                                           style=discord.InputTextStyle.short, required=True, value=None))

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.js['database_src'] + 'like.db')
        cursor = conn.cursor()

        pid = self.children[0].value
        title = self.children[1].value

        exist = cursor.execute(f'SELECT * FROM playlist WHERE id = "{pid}"').fetchone()
        if exist:
            return await interaction.response.send_message('이미 동일한 ID를 가진 재생목록이 존재합니다.')

        cursor.execute('INSERT INTO playlist VALUES (?, ?, ?, ?)', (pid, title, "", 1))
        conn.commit()
        conn.close()

        return await interaction.response.send_message(f'{title}(`{pid}`) 재생목록이 추가되었습니다.\n'
                                                       f'`/재생목록 아이콘` 명령어를 사용해 아이콘을 업로드해 주세요.')
