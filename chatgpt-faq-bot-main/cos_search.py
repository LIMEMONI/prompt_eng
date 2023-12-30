import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt 
import numpy as np

okt = Okt() 

test_df = pd.read_csv('./cos_search_data/231229_okt_add_df.csv')

df_test = test_df[['사업장명','지번주소','final_url','kkm','pos_low',	'pos_high',	'neg_low',	'neg_high']]
pn_cnt_df = df_test.pivot_table(index=['사업장명','지번주소','final_url'], values=['pos_low','pos_high','neg_low','neg_high'], aggfunc='sum')
pn_cnt_df['pn_ratio'] = (pn_cnt_df['pos_high'] / (pn_cnt_df['neg_high'] + pn_cnt_df['pos_high'])).round(3)
pn_cnt_df['cnt'] = pn_cnt_df['neg_high'] + pn_cnt_df['neg_low'] + pn_cnt_df['pos_high'] + pn_cnt_df['pos_low']
pn_cnt_df['long_pos_ratio'] = (pn_cnt_df['pos_high'] / (pn_cnt_df['pos_low'] + pn_cnt_df['pos_high'])).round(3)
pn_cnt_df = pn_cnt_df.sort_values('cnt',ascending=False)
pn_cnt_df.reset_index(inplace=True)
pn_cnt_df = pn_cnt_df[(pn_cnt_df['long_pos_ratio'].notnull()) & (pn_cnt_df['pn_ratio'].notnull())]

def get_res_df(keyword:str,add=''):
    tmp_df = test_df[test_df['지번주소'].fillna('').str.contains(add)]
    
    # 데이터 준비
    target_nouns = okt.nouns(keyword)
    sentence1 = ' '.join(target_nouns)
    print(target_nouns)
    print(sentence1)

    samples = tmp_df.loc[(tmp_df['review_content_cleaned'].notnull()),'okt']
    sentences = samples.fillna("").values.tolist()
    indexes = list(samples.index)

    # sentence1을 문장 목록의 첫 번째 요소로 추가
    sentences.insert(0, sentence1)
    indexes.insert(0, 0)

    # TF-IDF 벡터라이저 생성 및 변환
    vectorizer = TfidfVectorizer(vocabulary=target_nouns)
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # Cosine 유사도 계산
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

    # Cosine 유사도가 1 이상인 문장들의 인덱스 추출
    filtered_indexes = [indexes[i] for i in np.where(cosine_sim >= 1)[1]]
    filtered_indexes.pop(0)

    filtered_df = tmp_df.loc[filtered_indexes]
    filtered_df['cnt_score'] = 0
    filtered_df.loc[filtered_df['predict'] == '긍정','cnt_score'] = 1
    filtered_df.loc[filtered_df['predict'] == '부정','cnt_score'] = -1

    df_test = filtered_df[['사업장명','지번주소','final_url','cnt_score']]
    cnt_score_df = df_test.pivot_table(index=['사업장명','지번주소','final_url'], values=['cnt_score'], aggfunc='sum')
    cnt_score_df.sort_values('cnt_score',ascending=False).reset_index()

    total_df = pd.merge(cnt_score_df,pn_cnt_df, on=['사업장명','지번주소','final_url'], how='left')
    total_df = total_df.sort_values(['cnt_score','cnt','pn_ratio'],ascending=[False,False,False]).reset_index(drop=True)
    return total_df