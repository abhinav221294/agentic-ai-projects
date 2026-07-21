import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

type Message = {
  role: string;
  text: string;
};

type Props = {
  messages: Message[];
};

function ChatWindow({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  return (
    <div
      style={{
        flex: 1,
        overflowY: "auto",
        padding: "24px",
      }}
    >
      <div
        style={{
          maxWidth: "900px",
          width: "100%",
          margin: "0 auto",
          marginLeft: "140px",
          display: "flex",
          marginRight: "auto",
          flexDirection: "column",
          gap: "16px",
        }}
      >
        {messages.map((msg, index) => (
          <MessageBubble       
            key={index}
            role={msg.role}
            text={msg.text}
          />
        ))}

        <div ref={bottomRef}></div>
      </div>
    </div>
  );
}

export default ChatWindow;