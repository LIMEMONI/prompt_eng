import os
from PyPDF2 import PdfReader
from fastapi import FastAPI
from datastore import Datastore
from models import Document, Query, File

db = Datastore("chatpdf")

app = FastAPI()


@app.post("/load")
async def load(file: File):
    # 파일 경로에서 파일 이름만 추출하여 변수에 저장
    filename = os.path.basename(file.path)  
    fulltext = ""

    with open(file.path, "rb") as f:
        pdf = PdfReader(f)

        for page in pdf.pages: # pdf chunk화 해서 db에 넣기
            text = page.extract_text() # 페이지에서 텍스트 추출
            # 텍스트를 900글자씩 나누어 리스트에 저장 (100자씩 오버랩 : 내용이 잘리지 않기 위함)
            chunks = [text[i:i+1000] for i in range(0, len(text), 900)] 
            pageNum = pdf.get_page_number(page) # 현재 페이지 번호 저장
            # 전체 텍스트에 현재 페이지의 텍스트 추가 (api 호출 클라이언트에 전체 text를 전달해주기 위함)
            fulltext += text 

            for i, chunk in enumerate(chunks):
                doc = Document(
                    id=f"{filename}-p{pageNum}-{i}", # id 설정
                    text=chunk,
                    metadata={"filename": filename, "page": pageNum} # metadata 설정
                )

                # 문서 ID 출력
                print("Upserting: ", doc.id)
                
                # 문서를 크로마 데이터베이스에 업서트
                db.upsert(doc)

    return {
        "filename": filename,
        "total_pages": len(pdf.pages),
        "text": fulltext
    }


@app.post("/query")
async def query(query: Query) -> list[Document]:
    result = db.query(query.filename, query.query, query.top_k)

    print(query.filename, query.query)
    # print(result)

    return result
