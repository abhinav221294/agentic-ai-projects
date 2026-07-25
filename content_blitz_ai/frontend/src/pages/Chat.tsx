import { useState, useEffect } from "react";

import ChatWindow from "../components/ChatWindow";
import PromptBox from "../components/PromptBox";
import Sidebar from "../components/Sidebar";
import WelcomeScreen from "../components/WelcomeScreen";

import api from "../services/api";

import {
    generateContentStream,
} from "../services/contentService";

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

const processingSteps =  [
    "🧠 Understanding your request...",
    "🔍 Researching...",
    "📋 Planning content...",
    "✍️ Writing response..."
];

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
        messages: chat.messages.filter(message => {
        if (message.role !== "Assistant") return true;

        return ![
        THINKING_MESSAGE,
        ...processingSteps,
        ].includes(message.text);
        })
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

    setConversations(prev => [newChat, ...prev]);
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
    let interval: ReturnType<typeof setInterval> | undefined;
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
    title:
        chat.title === "New Chat"
            ? trimmedQuery.slice(0, 30)
            : chat.title,
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

    // Show the first processing step immediately
    updateConversation(currentChatId, chat => {
    const updated = [...chat.messages];

    updated[updated.length - 1] = {
        role: "Assistant",
        text: processingSteps[0],
    };

    return {
        ...chat,
        messages: updated,
    };
    });

    let step = 1;

    // Rotate through the remaining processing steps
    interval = setInterval(() => {

    updateConversation(currentChatId, chat => {

        const updated = [...chat.messages];

        updated[updated.length - 1] = {
            role: "Assistant",
            text: processingSteps[step],
        };

        return {
            ...chat,
            messages: updated,
        };
    });

    step = (step + 1) % processingSteps.length;

    }, 2000);

    let assistantText = "";
    let firstChunk = true;

    await generateContentStream(
    {
        query: trimmedQuery,
        conversation_id: currentChatId,
    },
    (chunk) => {
         if (firstChunk) {
        clearInterval(interval);
        firstChunk = false;
        }

        assistantText += chunk;

        updateConversation(currentChatId, chat => {
            const updatedMessages = [...chat.messages];

            updatedMessages[updatedMessages.length - 1] = {
                role: "Assistant",
                text: assistantText,
            };

            return {
                ...chat,
                updatedAt: Date.now(),
                messages: updatedMessages,
            };
        });
    }
    );

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

    if (interval) {
        clearInterval(interval);
    }

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
    flex: 1,
    maxWidth: "100%",
    width: "100%",
    margin: "0 auto",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    background: "#0f172a",
    color: "white",
    padding: "0 20px",
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

<div
  style={{
    maxWidth: "900px",
    width: "100%",
    marginLeft: "80px",   // match ChatWindow
    marginRight: "auto",
    margin: "0 auto",
    transform: "translateX(20px)",
  }}
>
  <PromptBox
    query={prompt}
    setQuery={setPrompt}
    onSend={handleSend}
    loading={loading}
  />
</div>

</div>

</div>

);

}

export default App;