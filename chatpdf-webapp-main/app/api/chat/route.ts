import { NextRequest } from "next/server"
import { OpenAIStream, StreamingTextResponse } from "ai"
import { Configuration, OpenAIApi } from "openai-edge"

const openAIConfiguration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
})

const openai = new OpenAIApi(openAIConfiguration)

export const runtime = "edge"

const systemPrompt =
  "당신은 PDF 문서 학습을 도와주는 AI Assistant 입니다. 사용자의 질문에 대해 문서의 내용을 참고하여 답변하세요."

export async function POST(req: NextRequest) {
  const { filename, messages } = await req.json()

  // 질문과 관련된 내용 검색
  const vectordb_response = await fetch("http://127.0.0.1:8000/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: messages[messages.length - 1].content, // 마지막 메시지의 내용을 쿼리로 사용
      top_k: 5, // 상위 5개 결과 반환
      filename: filename, // 파일 이름 전송
    }),
  })

  const search_result = await vectordb_response.json()

  // 검색한 결과를 컨텍스트 텍스트로 재구성
  let result_text = "--- PDF Content ---\n" // 검색 결과를 저장할 변수 초기화
  for (let i = 0; i < search_result.length; i++) { // 검색 결과 배열을 반복하여 순회
    result_text += // 결과 텍스트에 추가
      "page: " + // 페이지 번호 출력
      search_result[i].metadata.page + // 검색 결과의 페이지 번호
      "\n" + // 줄바꿈
      "snippet: " + // 스니펫 출력
      search_result[i].text + // 검색 결과의 스니펫
      "\n\n" // 빈 줄 추가
  }

  console.log([
    { role: "system", content: systemPrompt }, // 시스템 역할과 시스템 프롬프트를 출력합니다.
    ...messages.slice(0, -1), // 마지막 메시지를 제외한 모든 메시지를 출력합니다.
    { role: "user", content: result_text }, // 사용자 역할과 결과 텍스트를 출력합니다.
    messages[messages.length - 1], // 마지막 메시지를 출력합니다.
  ])

  // 검색한 결과를 바탕으로 답변 생성
  const response = await openai.createChatCompletion({
    model: "gpt-3.5-turbo-16k", // GPT-3.5 Turbo 모델 사용
    stream: true, // 스트림 모드로 설정하여 실시간으로 응답 받음
    temperature: 0.7, // 다양한 응답을 생성하기 위한 온도 설정
    max_tokens: 1024, // 최대 토큰 수 설정
    messages: [
      { role: "system", content: systemPrompt }, // 시스템 역할의 메시지로 시스템 프롬프트 사용
      ...messages.slice(0, -1), // 이전 메시지들을 추가
      { role: "user", content: result_text }, // 사용자 역할의 메시지로 검색 결과 텍스트 사용
      messages[messages.length - 1], // 마지막 메시지 추가
    ],
  })

  const stream = OpenAIStream(response)

  return new StreamingTextResponse(stream)
}
