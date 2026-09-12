import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, ArrowRight } from "lucide-react";
import { api, errorText } from "./api";

export default function GuardianLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { data } = await api.post("/auth/login", { username, password });
      sessionStorage.setItem("guardrails-token", data.access_token);
      setPassword("");
      navigate("/", { replace: true });
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <main className="panel w-full max-w-md !p-8">
        <ShieldCheck size={32} className="mb-5" />
        <h1 className="!text-3xl">Guardian sign in</h1>
        <p className="subtle my-4">
          Use the guardian account configured for this workspace.
        </p>
        <form onSubmit={submit} className="space-y-5">
          <label>
            Username
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              maxLength={80}
            />
          </label>
          <label>
            Password
            <input
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              maxLength={256}
            />
          </label>
          {error && (
            <p role="alert" className="error-box">
              {error}
            </p>
          )}
          <button
            type="submit"
            className="primary magnetic w-full justify-center"
            disabled={busy}
            onPointerMove={(event) => {
              if (
                event.pointerType !== "mouse" ||
                matchMedia("(prefers-reduced-motion: reduce)").matches
              )
                return;
              const rect = event.currentTarget.getBoundingClientRect();
              event.currentTarget.style.setProperty(
                "--mx",
                `${(event.clientX - rect.left - rect.width / 2) * 0.05}px`,
              );
              event.currentTarget.style.setProperty(
                "--my",
                `${(event.clientY - rect.top - rect.height / 2) * 0.08}px`,
              );
            }}
            onPointerLeave={(event) => {
              event.currentTarget.style.setProperty("--mx", "0px");
              event.currentTarget.style.setProperty("--my", "0px");
            }}
          >
            {busy ? "Signing in…" : "Sign in"}
            <ArrowRight size={16} />
          </button>
        </form>
        <Link to="/help" className="text-link mt-7">
          Looking for support? No login needed.
        </Link>
        <Link to="/" className="text-link mt-4">
          Return to workspace
        </Link>
      </main>
    </div>
  );
}
