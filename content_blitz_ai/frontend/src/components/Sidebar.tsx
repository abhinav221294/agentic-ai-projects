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
  onDeleteChat: (id: number) => void;   // NEW
};



function Sidebar({
  chats,
  chatId,
  onSelect,
  onNewChat,
  onDeleteChat
}: Props) {

  const formatTime = (timestamp: number) => {

    const date = new Date(timestamp);

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

};

  const sortedChats = [...chats].sort(
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
    <div>
    {formatTime(chat.updatedAt)}
    </div>
      <div>
        {chat.title}
      </div>

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

    <button
    onClick={() => onDeleteChat(chat.id)}
    style={{
    background: "transparent",
    border: "none",
    cursor: "pointer",
    fontSize: "14px",
    color: "#CBD5E1"
    }}
    >
    🗑️
  </button>

  </div>

  ))}

    </div>

  );

}

export default Sidebar;