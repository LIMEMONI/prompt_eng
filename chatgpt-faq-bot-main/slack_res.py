import os
import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import vectordb

import openai


openAIclient = openai.OpenAI(
    api_key='sk-'
)
# openai.api_key = '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'

SLACK_SIGNING_SECRET = "91fa80b0f2c9545d70ed9c74d5329c7b"
SLACK_BOT_TOKEN = "xoxb-6406636975201-6393916344787-q0cEjiSYD4hWwdfaOmY5LrwX"
SLACK_APP_TOKEN = "xapp-1-A06BKSCNYE7-6387376822374-49c2676cb319b236126c126686ea6b2223409cbd4f42e1c8b65cf0259b4606c9"

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

faq_db = vectordb.load("run_qna.csv")


@app.event("message")
def message_handler(message, say):
    if '맛집' in message['text']:
        splited = message['text'].split('맛집')[0].strip()
        target = splited.split('지역')[1].strip() if '지역' in splited else splited
        add = splited.split('지역')[0].strip() if '지역' in splited else ''
        if target == '':
            cnt_df = vectordb.cs.pn_cnt_df
            cnt_df = cnt_df[(cnt_df['지번주소'].fillna('').str.contains(add)) & (cnt_df['cnt'] >= 100)].sample(10).sort_values(['cnt','pn_ratio','long_pos_ratio'], ascending=[False,False,False]).reset_index(drop=True)
            context = "--- CONTEXT ---\n"
            for i in range(len(cnt_df.head(10))):
                context += f" rank: {i+1}\n name: {cnt_df.loc[i,'사업장명']}\n address: {cnt_df.loc[i,'지번주소']}\n url: {cnt_df.loc[i,'final_url']}\n review_count: {cnt_df.loc[i,'cnt']}\n review_positive_ratio: {cnt_df.loc[i,'pn_ratio']}\n long_review_ratio: {cnt_df.loc[i,'long_pos_ratio']}\n\n"
            print([
                {"role": "user", "content": context},
                {"role": "user", "content": "CONTEXT를 기반으로 다음 질문에 답변해.\n" +
                message['text']}
            ])
        else:
            result = vectordb.search_res(target,add) 
            context = "--- CONTEXT ---\n"
            for i in range(len(result)):
                context += f" rank: {result[i]['rank']}\n name: {result[i]['name']}\n address: {result[i]['address']}\n url: {result[i]['url']}\n keyword_match_score: {result[i]['keyword_match_score']}\n review_count: {result[i]['review_count']}\n review_positive_ratio: {result[i]['review_positive_ratio']}\n long_review_ratio: {result[i]['long_review_ratio']}\n\n"
            print([
                {"role": "user", "content": context},
                {"role": "user", "content": "CONTEXT를 기반으로 다음 질문에 답변해.\n" +
                message['text']}
            ])

    # 질문에 대해 벡터 서치로 답변을 찾아서 context에 저장
    else: 
        # vector = vectordb.get_embedding(message['text'])
        # result = vectordb.search(vector, faq_db)

        context = "--- CONTEXT ---\n"
        # for i in range(3):
        #     context += f"질문: {result[i]['question']}\n답변: {result[i]['answer']}\n\n"

        # print([
        #     {"role": "user", "content": context},
        #     {"role": "user", "content": "CONTEXT를 기반으로 다음 질문에 답변해.\n" +
        #     message['text']}
        # ])

    # context에 담긴 질문과 답변을 기반으로 대화 생성
    completion = openAIclient.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": context},
            {"role": "user", "content": "CONTEXT를 기반으로 다음 질문에 답변해.\n" +
                message['text']}
        ],
        temperature=0,
        max_tokens=2048,
    )

    say(completion.choices[0].message.content)


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
