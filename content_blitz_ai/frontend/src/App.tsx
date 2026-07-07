import { useState } from "react";

import ChatWindow from "./components/ChatWindow";
import PromptBox from "./components/PromptBox";

import api from "./services/api";

type Message = {
  role: string;
  text: string;
};

function App() {

  const [messages, setMessages] = useState<Message[]>([
    {
      role: "User",
      text: "Write a blog on Agentic AI"
    },
    {
      role: "Assistant",
      text: "Agentic AI is transforming..."
    }
  ]);

  const handleSend = async (query: string) => {

    try {

      setMessages(prev => [
        ...prev,
        {
          role: "User",
          text: query
        }
      ]);

      const response = await api.post(
        "/generate",
        {
          query
        }
      );

      const data = response.data;

      setMessages(prev => [
        ...prev,
        {
          role: "Assistant",
          text:
            data.response ??
            data.answer ??
            "Response received."
        }
      ]);

    }

    catch (error) {

      console.error(error);

    }

  };

  return (

    <div

style={{

width:"1000px",

height:"100vh",

margin:"0 auto",

display:"flex",

flexDirection:"column",

padding:"20px",

boxSizing:"border-box"

}}

>

      <h1

        style={{

          fontSize: "42px",

          textAlign: "center",

          marginBottom: "20px"

        }}

      >

        Content Blitz AI

      </h1>

      <ChatWindow

        messages={messages}

      />

      <PromptBox

        onSend={handleSend}

      />

    </div>

  );

}

export default App;