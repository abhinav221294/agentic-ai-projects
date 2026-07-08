import { useState } from "react";

import ChatWindow from "./components/ChatWindow";
import PromptBox from "./components/PromptBox";

import api from "./services/api";

type Message = {
  role: string;
  text: string;
};

function App() {
  const [loading,setLoading] = useState(false)

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
      setLoading(true)
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
  
  finally{
    setLoading(false)

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

overflow:"hidden"

}}

>

<h1>

Content Blitz AI

</h1>

<ChatWindow

messages={messages}

/>

<PromptBox

onSend={handleSend}

loading={loading}

/>

</div>

  );

}

export default App;