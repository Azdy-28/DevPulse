import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function OAuthButtons() {
  return (
    <div className="space-y-2">
      <a
        href={`${API_BASE}/api/auth/google/login`}
        className="flex items-center justify-center gap-2 w-full border border-line rounded px-3 py-2 text-sm text-paper hover:bg-panel2 transition-colors"
      >
        <svg width="16" height="16" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.07 5.07 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.25 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.85A11 11 0 0 0 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09A6.6 6.6 0 0 1 5.5 12c0-.73.12-1.43.34-2.09V7.06H2.18A11 11 0 0 0 1 12c0 1.77.43 3.45 1.18 4.94z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1a11 11 0 0 0-9.82 6.06l3.66 2.85c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Continue with Google
      </a>
      <a
        href={`${API_BASE}/api/auth/microsoft/login`}
        className="flex items-center justify-center gap-2 w-full border border-line rounded px-3 py-2 text-sm text-paper hover:bg-panel2 transition-colors"
      >
        <svg width="16" height="16" viewBox="0 0 24 24">
          <path fill="#F35325" d="M1 1h10v10H1z"/>
          <path fill="#81BC06" d="M13 1h10v10H13z"/>
          <path fill="#05A6F0" d="M1 13h10v10H1z"/>
          <path fill="#FFBA08" d="M13 13h10v10H13z"/>
        </svg>
        Continue with Microsoft
      </a>
    </div>
  );
}

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register(email, password, fullName);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-mono text-2xl text-amber tracking-tight">DevPulse</div>
          <div className="text-sm text-muted mt-1">Create your workspace</div>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          {error && (
            <div className="text-sm text-alert bg-alert/10 border border-alert/30 rounded px-3 py-2">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm text-muted mb-1">Full name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>
          <div>
            <label className="block text-sm text-muted mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>
          <button
            type="submit"
            disabled={busy}
            className="w-full bg-amber text-ink font-medium rounded px-3 py-2 text-sm hover:opacity-90 disabled:opacity-50"
          >
            {busy ? "Creating..." : "Create account"}
          </button>
        </form>

        <div className="flex items-center gap-3 my-4">
          <div className="h-px bg-line flex-1" />
          <span className="text-xs text-muted">or</span>
          <div className="h-px bg-line flex-1" />
        </div>

        <OAuthButtons />

        <p className="text-center text-sm text-muted mt-4">
          Already have an account?{" "}
          <Link to="/login" className="text-amber hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
