from pydantic import BaseModel  # pydantic 모듈에서 BaseModel 클래스를 import


class Metadata(BaseModel):
    filename: str  # 파일 이름을 나타내는 문자열 변수
    page: int  # 페이지 번호를 나타내는 정수 변수


class Document(BaseModel):
    id: str  # 문서의 고유 식별자를 나타내는 문자열 변수
    text: str  # 문서의 텍스트 내용을 나타내는 문자열 변수
    metadata: Metadata  # 문서의 chunk를 담고 있는 Metadata 객체


class File(BaseModel):
    path: str  # 파일의 경로를 나타내는 문자열 변수


class Query(BaseModel):
    filename: str  # 검색할 파일 이름을 나타내는 문자열 변수
    query: str  # 검색할 쿼리를 나타내는 문자열 변수
    top_k: int  # 상위 k개의 결과를 반환하기 위한 정수 변수
