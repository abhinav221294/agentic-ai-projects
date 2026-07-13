type Props = {
  onSuggestionClick: (prompt: string) => void;
};

function WelcomeScreen({ onSuggestionClick }: Props) {
 

  const suggestions = [
    {
      title: "📝 Blog",
      prompt: "Write a detailed blog on "
    },
    {
      title: "💼 LinkedIn",
      prompt: "Write a professional LinkedIn post about "
    },
    {
      title: "✨ Ask Anything",
      prompt: ""
    },
    {
      title: "🎨 Image",
      prompt: "Generate an image of "
    }
  ];

  return (

    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: "30px"
      }}
    >

      <div
    style={{
        textAlign: "center"
    }}
>

    <h1
        style={{
            fontSize: "48px",
            marginBottom: "10px"
        }}
    >
        🚀 Welcome to Content Blitz AI
    </h1>

    <h2
        style={{
            fontSize: "28px",
            fontWeight: 400,
            marginBottom: "12px"
        }}
    >
        What would you like to create today?
    </h2>

    <p
        style={{
            color: "#94A3B8",
            fontSize: "18px"
        }}
    >
        Choose a starting point or type your own prompt below.
    </p>

</div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2,220px)",
          gap: "20px"
        }}
      >

        {suggestions.map((item) => (

          <button
            key={item.title}
            onClick={() => onSuggestionClick(item.prompt)}
            style={{
              padding: "24px",
              borderRadius: "14px",
              border: "1px solid #334155",
              background: "#1E293B",
              color: "white",
              cursor: "pointer",
              fontSize: "18px"
            }}
          >
            {item.title}
          </button>

        ))}

      </div>

    </div>

  );

}

export default WelcomeScreen;