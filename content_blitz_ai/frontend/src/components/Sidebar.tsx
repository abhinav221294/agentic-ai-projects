import { useState } from "react";

type Conversation = {
  id: number;
  title: string;
  updatedAt: number;
};

type Props = {
  chats: Conversation[];
  chatId: number;
  onSelect: (id: number) => void;
  onNewChat: () => void;
  onDeleteChat: (id: number) => void;
  onRenameChat: (id: number, title: string) => void;
};



function Sidebar({
    chats,
    chatId,
    onSelect,
    onNewChat,
    onDeleteChat,
    onRenameChat
}: Props) {

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState("");

  const [search, setSearch] = useState("");

  const formatTime = (timestamp: number) => {

    const date = new Date(timestamp);

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

};

const filteredChats = chats.filter(chat =>
  chat.title
    .toLowerCase()
    .includes(search.toLowerCase())
);

const sortedChats = [...filteredChats].sort(
  (a, b) => b.updatedAt - a.updatedAt
);

  return (

    <div
      style={{
        width: "250px",
        background: "#111827",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "15px",
        color: "white"
      }}
    >

      <h2>Chats</h2>

    <button
    onClick={onNewChat}
    style={{
    background: "#2563EB",
    color: "white",
    border: "none",
    borderRadius: "10px",
    padding: "12px",
    cursor: "pointer"
    }}
    >
    + New Chat
  </button>
  
  <input
  type="text"
  placeholder="🔍 Search chats..."
  value={search}
  onChange={(e) => setSearch(e.target.value)}
  style={{
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #374151",
    background: "#1F2937",
    color: "white",
    outline: "none",
    fontSize: "14px"
    }}
    />    

     {sortedChats.map(chat => (

    <div
    key={chat.id}
    style={{
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px",
    borderRadius: "10px",

    background:
    chat.id === chatId
        ? "#1E293B"
        : "#1F2937",

    borderLeft:
    chat.id === chatId
        ? "4px solid #3B82F6"
        : "4px solid transparent",

    transition: "0.2s ease"
    }}
    >

  <div
  style={{
    flex: 1,
    cursor: "pointer"
  }}
  onClick={() => onSelect(chat.id)}
>

  {
    editingId === chat.id
      ? (
        <input
        value={editingTitle}
        autoFocus
        onChange={(e) => setEditingTitle(e.target.value)}
        onKeyDown={(e) => {
        if (e.key === "Enter") {
            onRenameChat(chat.id, editingTitle.trim());
            setEditingId(null);
        }
        }}
        onBlur={() => {
        onRenameChat(chat.id, editingTitle.trim());
        setEditingId(null);
        }}
        style={{
        width: "100%",
        maxWidth: "160px",
        padding: "4px 6px",
        borderRadius: "6px",
        border: "1px solid #3B82F6",
        background: "#111827",
        color: "white",
        fontSize: "14px",
        boxSizing: "border-box"
        }}
        />
      )
      : (
        <div
          onDoubleClick={() => {
            setEditingId(chat.id);
            setEditingTitle(chat.title);
          }}
        >
          {chat.title}
        </div>
      )
  }

  <div
    style={{
      fontSize: "12px",
      color: "#94A3B8",
      marginTop: "6px"
    }}
  >
    {formatTime(chat.updatedAt)}
  </div>

</div>

    {
    editingId !== chat.id && (

    <button
    onClick={() => onDeleteChat(chat.id)}
    style={{
        background: "transparent",
        border: "none",
        cursor: "pointer",
        color: "#CBD5E1"
      }}
>
      🗑️
    </button>

    )
    } 

  </div>

  ))}
    {sortedChats.length === 0 && (
    <div
    style={{
      color: "#94A3B8",
      textAlign: "center",
      marginTop: "20px"
      }}
    >
    No chats found.
  </div>
  )}
    </div>

  );
}


export default Sidebar;