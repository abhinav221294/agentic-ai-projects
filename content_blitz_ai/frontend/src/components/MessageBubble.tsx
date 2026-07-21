import TypingIndicator from "./TypingIndicator";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";

type Props = {
  role: string;
  text: string;
};

function MessageBubble({ role, text }: Props) {
  const isUser = role === "User";

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "24px",
      }}
    >
      <div
        style={{
          maxWidth: isUser ? "55%" : "100%",
          background: isUser ? "#2563EB" : "#1E293B",
          color: "white",
          borderRadius: "16px",
          padding: "24px",
          lineHeight: "1.7",
          wordBreak: "break-word",
          boxShadow: "0 2px 10px rgba(0,0,0,.25)",
        }}
      >
        <div
          style={{
            fontSize: "13px",
            fontWeight: 600,
            marginBottom: "10px",
            opacity: 0.8,
          }}
        >
          {isUser ? "🙂 You" : "🤖 Content Blitz AI"}
        </div>

        {role === "Assistant" && text === "Thinking..." ? (
          <TypingIndicator />
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
          >
            {text}
          </ReactMarkdown>
        )}
      </div>
    </div>
  );
}

export default MessageBubble;