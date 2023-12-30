import { NextRequest, NextResponse } from "next/server";

const CHAT_SERVER_URL = "https://e51e-34-132-85-177.ngrok-free.app";

export async function POST(req: NextRequest) {
  const { message } = await req.json(); // 요청에서 message를 추출하여 변수에 할당

  const response = await fetch(CHAT_SERVER_URL + "/chat", { // CHAT_SERVER_URL에 "/chat" 경로를 추가하여 fetch 요청을 보냄
    method: "POST", // POST 메서드 사용
    headers: {
      "Content-Type": "application/json", // 요청 헤더에 "Content-Type"을 "application/json"으로 설정
    },
    body: JSON.stringify({
      content: message, // 요청의 본문에 message를 포함하여 JSON 문자열로 변환
    }),
  });

  const completion = await response.json(); // 응답을 JSON 형식으로 변환하여 변수에 할당
  console.log(completion); // completion을 콘솔에 출력
  completion.content; // completion 객체의 content 속성에 접근

  return NextResponse.json({
    success: true,
    content: completion.content, // completion 객체의 content 속성을 응답의 본문으로 설정
  });
}
