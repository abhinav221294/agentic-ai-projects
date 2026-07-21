import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../services/auth";

function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegister = async (e: React.SyntheticEvent<HTMLFormElement>) => {
  e.preventDefault();

  setError("");

  try {
    setLoading(true);

    await register({
      username,
      email,
      password,
    });

    navigate("/login");

  } catch (err: any) {
    console.error(err);
    console.error(err?.response);

    setError(
      JSON.stringify(err?.response?.data) ||
      err.message ||
      "Registration failed."
    );

  } finally {
    setLoading(false);
  }
};

  return (
    <div className="auth-container">
      <form className="auth-card" onSubmit={handleRegister}>

        <h1>Content Blitz AI</h1>

        <h2>Create Account</h2>

        {error && (
          <p className="error">
            {error}
          </p>
        )}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading ? "Creating Account..." : "Register"}
        </button>

        <p>
          Already have an account?{" "}
          <Link to="/login">
            Login
          </Link>
        </p>

      </form>
    </div>
  );
}
export default Register;