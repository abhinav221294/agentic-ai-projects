import { useState, useEffect } from "react";

import ChatWindow from "./components/ChatWindow";
import PromptBox from "./components/PromptBox";
import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";

import api from "./services/api";

const THINKING_MESSAGE = "Thinking...";
const ERROR_MESSAGE = "❌ Failed to generate response.";

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

    const chats: Conversation[] = JSON.parse(savedChats);

    return chats.map(chat => ({
        ...chat,
        messages: chat.messages.filter(
            message =>
                !(
                    message.role === "Assistant" &&
                    message.text === THINKING_MESSAGE
                )
        )
    }));

    }

    return [];

});

const updateConversation = (
    id: number,
    updater: (chat: Conversation) => Conversation
) => {
    setConversations(prev =>
        prev.map(chat =>
            chat.id === id ? updater(chat) : chat
        )
    );
};

const createConversationWithMessage = async (firstMessage?: string) => {
    const response = await api.post("/conversation");

    const newChat : Conversation  = {
        id: response.data.conversation_id,
        title: firstMessage
            ? firstMessage.slice(0, 30)
            : "New Chat",
        messages: firstMessage
            ? [
                {
                    role: "User",
                    text: firstMessage
                },
                {
                    role: "Assistant",
                    text: THINKING_MESSAGE
                }
            ]
            : [],
        updatedAt: Date.now()
    };

    setConversations(prev => [...prev, newChat]);
    setActiveChatId(newChat.id);

    return newChat;
};

const [chatId, setActiveChatId] = useState(() => {
    const savedChatId = localStorage.getItem(
        "content-blitz-active-chat"
    );

    return savedChatId ? Number(savedChatId) : 0;
});

useEffect(() => {
    localStorage.setItem(
        "content-blitz-active-chat",
        chatId.toString()
    );
}, [chatId]);

const currentConversation =
    conversations.find(chat => chat.id === chatId);

const messages = currentConversation?.messages ?? [];

  useEffect(() => {

    localStorage.setItem(
        "content-blitz-chats",
        JSON.stringify(conversations)
    );

}, [conversations]);


const [prompt, setPrompt] = useState("");
const handleSend = async (query: string) => {
    const trimmedQuery = query.trim();

    if (!trimmedQuery) return;

    setPrompt("");

    let currentChatId = chatId;

    if (!currentConversation) {
    const newChat = await createConversationWithMessage(trimmedQuery);
    currentChatId = newChat.id;
    }
    else {

 updateConversation(currentChatId, chat => ({
    ...chat,
    updatedAt: Date.now(),
    messages: [
        ...chat.messages,
        {
            role: "User",
            text: trimmedQuery
        },
        {
            role: "Assistant",
            text: THINKING_MESSAGE
        }
    ]
}));

}
  try {

    setLoading(true);

    const response = await api.post("/generate", {
    query: trimmedQuery,
    conversation_id: currentChatId
    });

    const data = response.data;
    console.log("Response:", data);

    // Replace the Thinking... message
    updateConversation(currentChatId, chat => {

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
        messages: updatedMessages
        };
    });

  }

  catch (error) {

    console.error(error);

   updateConversation(currentChatId, chat => {

    const updatedMessages = [...chat.messages];

    updatedMessages[updatedMessages.length - 1] = {
        role: "Assistant",
        text: ERROR_MESSAGE
    };

    return {
        ...chat,
        messages: updatedMessages
    };
});

}

  finally {

    setLoading(false);

  }

};


  const handleNewChat = async () => {
    try {
        await createConversationWithMessage();
    } catch (error) {
        console.error(error);
    }
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