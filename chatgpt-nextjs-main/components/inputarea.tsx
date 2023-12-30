
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";

export default function InputArea({
  handleSend,
  scrollToBottom,
}: {
  handleSend: Function; // handleSend 함수를 props로 받음
  scrollToBottom: Function; // scrollToBottom 함수를 props로 받음
}) {
  const [query, setQuery] = useState<string>(""); // query 상태와 setQuery 함수를 생성하고 초기값은 빈 문자열로 설정

  const send = () => {
    handleSend(query); // handleSend 함수에 query 값을 전달하여 호출
    scrollToBottom(); // scrollToBottom 함수 호출
    setQuery(""); // query 값을 초기화
  };

  return (
    <div className="relative block w-full items-end">
      <div className="flex w-full items-end space-x-0">
        <Input
          type="query"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value); // Input 컴포넌트의 값이 변경될 때마다 query 값을 업데이트
          }}
          onKeyPress={(e) => {
            if (e.key === "Enter") {
              send(); // Enter 키를 누르면 send 함수 호출
            }
          }}
          placeholder="Ask any question..."
          className="rounded-none rounded-l-md focus-visible:ring-0"
        />
        <Button
          type="submit"
          className="rounded-none rounded-r-md"
          onClick={send} // 버튼 클릭 시 send 함수 호출
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
            />
          </svg>
        </Button>
      </div>
    </div>
  );
}
