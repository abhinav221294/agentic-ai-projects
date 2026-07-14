import { useState, useEffect } from "react";

import ChatWindow from "./components/ChatWindow";
import PromptBox from "./components/PromptBox";
import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";

import api from "./services/api";

type Message = {
  role: string;
  text: string;
};

type Conversation = {
  id: number;
  title: string;
  messages: Message[];
  updatedAt: number
};

function App() {
  const [loading,setLoading] = useState(false)

  const [conversations, setConversations] = useState<Conversation[]>(() => {

    const savedChats = localStorage.getItem(
        "content-blitz-chats"
    );

    if (savedChats) {
        return JSON.parse(savedChats);
    }

    return [
    {
        id: 1,
        title: "New Chat 1",
        messages: [],
        updatedAt: Date.now()
    }
    ];

});

const [chatId, setActiveChatId] = useState(() => {

    const savedChatId = localStorage.getItem(
        "content-blitz-active-chat"
    );

    return savedChatId ? Number(savedChatId) : 1;

});

const currentConversation =
    conversations.find(chat => chat.id === chatId);

const messages = currentConversation?.messages ?? [];

  useEffect(() => {

    localStorage.setItem(
        "content-blitz-chats",
        JSON.stringify(conversations)
    );

}, [conversations]);

useEffect(() => {

    localStorage.setItem(
        "content-blitz-active-chat",
        chatId.toString()
    );

}, [chatId]);

const [prompt, setPrompt] = useState("");
const handleSend = async (query: string) => {

  let currentChatId = chatId;

  // If there is no active chat, create one automatically
 if (!currentConversation) {

    const newChat = {
        id: Date.now(),
        title: query.trim().slice(0, 30),
        updatedAt: Date.now(),
        messages: [
            {
                role: "User",
                text: query
            },
            {
                role: "Assistant",
                text: "Thinking..."
            }
        ]
    };

    setConversations(prev => [...prev, newChat]);

    setActiveChatId(newChat.id);

    currentChatId = newChat.id;
  }

  try {

    setLoading(true);

    // Add user message + thinking placeholder
    if (currentConversation) {
    setConversations(prev =>
        prev.map(chat =>
            chat.id === currentChatId
                ? {
                    ...chat,
                    updatedAt: Date.now(),
                    title:
                        chat.messages.length === 0
                            ? query.trim().slice(0, 30)
                            : chat.title,
                    messages: [
                        ...chat.messages,
                        {
                            role: "User",
                            text: query
                        },
                        {
                            role: "Assistant",
                            text: "Thinking..."
                        }
                    ]
                }
                : chat
        )
    );
    }

    const response = await api.post("/generate", {
      query
    });

    const data = response.data;

    // Replace the Thinking... message
    setConversations(prev =>
      prev.map(chat => {

        if (chat.id !== currentChatId) return chat;

        const updatedMessages = [...chat.messages];

        updatedMessages[updatedMessages.length - 1] = {
          role: "Assistant",
          text:
            data.response ??
            data.answer ??
            "Response received."
        };

        return {
          ...chat,
          updatedAt: Date.now(),

          title:
          chat.messages.length === 0
          ? query.trim().slice(0,30)
          : chat.title,
          messages: updatedMessages
        };

      })
    );

  }

  catch (error) {

    console.error(error);

  }

  finally {

    setLoading(false);

  }

};
  const handleNewChat = () => {
    

    const newChat = {

        id: Date.now(),

        title: "New Chat",

        messages: [],

        updatedAt: Date.now()
    };


    setConversations(prev => [

        ...prev,
        
        newChat

    ]);

    setActiveChatId(newChat.id);

};


const handleDeleteChat = (id: number) => {


    const confirmed = window.confirm(
        "Are you sure you want to delete this chat?"
    );

    if (!confirmed) return;

    setConversations(prev => {

        const updated = prev.filter(chat => chat.id !== id);

        if (updated.length === 0) {
          setActiveChatId(0);
        } else if (chatId === id) {
          setActiveChatId(updated[0].id);
        }

        return updated;

    });

};

  const handleRenameChat = (id: number, title: string) => {

    setConversations(prev =>
        prev.map(chat =>
            chat.id === id
                ? {
                    ...chat,
                    title: title.trim() || chat.title
                }
                : chat
        )
    );

};

  return (

<div

style={{

display:"flex",

height:"100vh",

overflow:"hidden"

}}

>
  
<Sidebar
    chats={conversations}
    chatId={chatId}
    onSelect={setActiveChatId}
    onNewChat={handleNewChat}
    onDeleteChat={handleDeleteChat}
    onRenameChat={handleRenameChat}
/>

<div

style={{

width:"1000px",

margin:"0 auto",

display:"flex",

flexDirection:"column",

overflow:"hidden"

}}

>

{messages.length > 0 && (
    <h1
        style={{
            textAlign: "center",
            margin: "20px 0"
        }}
    >
        Content Blitz AI
    </h1>
)}

{
  messages.length === 0
  ? (
      <WelcomeScreen
        onSuggestionClick={setPrompt}
      />
    )
  : (
      <ChatWindow
        messages={messages}
      />
    )
}

<PromptBox
    query={prompt}
    setQuery={setPrompt}
    onSend={handleSend}
    loading={loading}
/>

</div>

</div>

);

}

export default App;