import json
import sqlite3
import time
import discord


class QNAForm(discord.ui.Modal):
    def __init__(self, qna: int = None):
        self.qna = qna
        with open('config.json', encoding='utf-8-sig') as file:
            self.js = json.load(file)

        if qna:
            cursor = sqlite3.connect(self.js['database_src'] + 'static.db').cursor()
            data = cursor.execute(f'SELECT * FROM qna WHERE id = "{qna}"').fetchone()
            category = data[1]
            question = data[2]
            answer = data[3]
        else:
            category, question, answer = None, None, None

        super().__init__(title='QnA 등록', custom_id="qna-create")
        self.add_item(discord.ui.InputText(placeholder="카테고리를 입력해 주세요.", label="카테고리",
                                           style=discord.InputTextStyle.short, required=True, value=category))
        self.add_item(discord.ui.InputText(placeholder="질문을 입력해 주세요.", label="질문",
                                           style=discord.InputTextStyle.long, required=True, value=question))
        self.add_item(discord.ui.InputText(placeholder="답변을 입력해 주세요.", label="답변",
                                           style=discord.InputTextStyle.long, required=True, value=answer))

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect(self.js['database_src'] + 'static.db')
        cursor = conn.cursor()

        category = self.children[0].value
        question = self.children[1].value
        answer = self.children[2].value

        if self.qna:
            cursor.execute(f'UPDATE qna SET category = "{category}", question = "{question}", '
                           f'description = "{answer}" WHERE id = "{self.qna}"')
            conn.commit()
            conn.close()
            return await interaction.response.send_message(f'{question}(`{self.qna}`)(이)가 변경되었습니다.')

        created = int(time.time())
        cursor.execute('INSERT INTO qna (category, question, description, create_at) VALUES (?, ?, ?, ?)', (category, question, answer, created))
        conn.commit()
        added = cursor.execute(f'SELECT * FROM qna WHERE create_at = {created}').fetchone()
        conn.close()

        return await interaction.response.send_message(f'{question}(`{added[0]}`) 질문이 추가되었습니다.')
