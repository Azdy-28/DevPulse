import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import client from "../api/client";

export default function OAuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { setUser } = useAuth();

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      navigate("/login?error=OAuth login failed");
      return;
    }
    localStorage.setItem("devpulse_token", token);

    client
      .get("/api/auth/me")
      .then(({ data }) => {
        setUser(data);
        navigate("/");
      })
      .catch(() => navigate("/login?error=Could not complete sign-in"));
  }, [params, navigate, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink">
      <p className="text-sm text-muted">Signing you in...</p>
    </div>
  );
}
