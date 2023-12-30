import os

import chromadb
from chromadb.utils import embedding_functions

from models import Document
from dotenv import load_dotenv

# .env.local 파일에서 환경 변수를 로드합니다.
load_dotenv(dotenv_path='.env.local')  

client = chromadb.PersistentClient(path="./chromadb")  # chromadb 클라이언트 생성

# 임베딩을 자동으로 해주기 위한 function 설정
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ["OPENAI_API_KEY"],  # OpenAI API 키 설정
    model_name="text-embedding-ada-002"  # 사용할 모델 이름 설정
)


class Datastore:
    def __init__(self, collection_name):
        self.collection_name = collection_name

        try:
            self.collection = client.get_collection(
                name=collection_name, embedding_function=openai_ef)  # 컬렉션 이름과 임베딩 함수를 사용하여 컬렉션을 가져옴
        except ValueError as e:
            self.collection = client.create_collection(
                name=collection_name, embedding_function=openai_ef)  # 컬렉션이 없을 경우 컬렉션을 생성함

    def upsert(self, doc: Document):
        self.collection.add(
            ids=[doc.id],  # 문서의 ID를 추가
            documents=[doc.text],  # 문서의 텍스트를 추가
            metadatas=[doc.metadata.dict()],  # 문서의 메타데이터를 추가
        )

        return doc

    def delete(self, id: str):
        self.collection.delete(ids=[id])

    def query(self, filename: str, query: str, top_k: int) -> list[Document]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"filename": filename},
        )

        docs = []
        for i in range(len(results["ids"][0])):
            doc = Document(
                id=results["ids"][0][i],
                text=results["documents"][0][i],
                metadata=results["metadatas"][0][i],
                distance=results["distances"][0][i],
            )

            docs.append(doc)

        return docs
