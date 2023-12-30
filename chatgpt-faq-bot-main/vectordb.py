import os
import csv
import openai
from openai import OpenAI
import numpy as np
from pprint import pprint
import cos_search as cs 

openAIclient = OpenAI(
    api_key='sk-'
)

# openai.api_key = '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'


def load(filepath):
    faq_db = []  # FAQ 데이터베이스를 저장할 리스트 생성
    with open(filepath, 'r', encoding='utf-8') as fp:  # 파일을 읽기 모드로 열기
        cr = csv.reader(fp)  # csv.reader를 사용하여 파일 읽기
        next(cr)  # 첫 번째 행은 헤더이므로 건너뛰기

        for row in cr:  # 각 행에 대해 반복
            # row: id,question,answer
            text = "Question: " + row[1] + "\nAnswer: " + row[2] + "\n"  # 질문과 답변을 텍스트로 합치기
            vector = get_embedding(text)  # 텍스트의 임베딩 벡터 얻기
            doc = {'id': row[0], 'vector': vector, 
                   'question': row[1], 'answer': row[2]}  # 문서 딕셔너리 생성
            faq_db.append(doc)  # FAQ 데이터베이스에 문서 추가

    return faq_db  # FAQ 데이터베이스 반환

def get_embedding(content, model='text-embedding-ada-002'):
    # openAIclient를 사용하여 임베딩을 얻는 함수입니다.
    response = openAIclient.embeddings.create(input=content, model=model)
    # 응답에서 임베딩 벡터를 추출합니다.
    vector = response.data[0].embedding
    # 추출한 벡터를 반환합니다.
    return vector


def similarity(v1, v2):  # return dot product of two vectors
    return np.dot(v1, v2)


def search(vector, db):
    results = []  # 결과를 저장할 빈 리스트 생성

    for doc in db:  # db의 각 문서에 대해 반복
        score = similarity(vector, doc['vector'])  # 주어진 벡터와 문서의 벡터 간 유사도 계산
        results.append(  # 결과 리스트에 문서의 정보와 유사도를 딕셔너리 형태로 추가
            {'id': doc['id'], 'score': score, 'question': doc['question'], 'answer': doc['answer']})

    results = sorted(results, key=lambda e: e['score'], reverse=True)  # 유사도에 따라 결과 리스트를 내림차순으로 정렬

    return results  # 정렬된 결과 리스트 반환

def search_res(keyword,add):
    results = []
    result_df = cs.get_res_df(keyword,add)
    for index, row in result_df.head(10).iterrows():
        results.append({
            'rank': index + 1,
            'name': row['사업장명'],
            'address': row['지번주소'],
            'url': row['final_url'],
            'keyword_match_score': row['cnt_score'],
            'review_positive_ratio': row['pn_ratio'],
            'review_count': row['cnt'],
            'long_review_ratio': row['long_pos_ratio'],
        })
    return results

if __name__ == '__main__':
    faq_db = load('prompt-faq.csv')  # 'prompt-faq.csv' 파일을 로드하여 faq_db 변수에 저장
    # print(faq_db)

    question = "ReAct가 뭔가요?"  # 질문 변수에 "ReAct가 뭔가요?" 저장
    vector = get_embedding(question)  # get_embedding 함수를 사용하여 질문의 벡터를 얻어 vector 변수에 저장
    # print(question, vector)

    result = search(vector, faq_db)  # search 함수를 사용하여 벡터와 faq_db를 비교하여 결과를 얻어 result 변수에 저장
    pprint(result)  # result를 보기 좋게 출력
