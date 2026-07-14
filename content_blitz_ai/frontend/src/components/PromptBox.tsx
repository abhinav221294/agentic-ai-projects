type Props = {

  query: string;

  setQuery: React.Dispatch<React.SetStateAction<string>>;

  onSend: (query: string) => void;

  loading: boolean;

}

function PromptBox({

  query,

  setQuery,

  onSend,

  loading

}: Props) {

  const handleClick = () => {

    if (!query.trim()) return;

    onSend(query);

    setQuery("");

  };

  return (

    <div

      style={{

        display: "flex",

        gap: "12px",

        paddingBottom: "20px"

      }}

    >

      <input

        style={{

          flex: 1,

          padding: "14px",

          borderRadius: "10px",

          border: "1px solid #333",

          background: "white",

          color: "black",

          fontSize: "16px"

        }}

        value={query}

        disabled={loading}

        onChange={(e) => setQuery(e.target.value)}

        onKeyDown={(e) => {

          if (e.key === "Enter") {

            handleClick();

          }

        }}

        placeholder="Ask Content Blitz"

      />

      <button

        disabled={loading}

        onClick={handleClick}

        style={{

          padding: "14px 20px",

          borderRadius: "10px",

          color: "white",

          background: loading ? "#4B5563" : "#2563EB",

          border: "none",

          cursor: loading ? "not-allowed" : "pointer"

        }}

      >

        Send

      </button>

    </div>

  );

}

export default PromptBox;