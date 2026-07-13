function TypingIndicator() {
  return (
    <div
      style={{
        display: "flex",
        gap: "6px",
        alignItems: "center",
        padding: "10px 0"
      }}
    >
      <span className="dot"></span>
      <span className="dot"></span>
      <span className="dot"></span>
    </div>
  );
}

export default TypingIndicator;