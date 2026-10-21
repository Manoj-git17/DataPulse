import { useState, useRef } from "react";
import "./AuthPage.css";

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');


export default function AuthPage({ onAuthenticated, onBack, theme }) {
  const [mode, setMode] = useState("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const isSubmitting = useRef(false);

  const isRegister = mode === "register";

  async function handleSubmit(event) {
    event.preventDefault();

    if (isSubmitting.current || loading) {
      return;
    }

    setError("");
    setSuccess("");

    if (isRegister && fullName.trim().length < 2) {
      setError("Please enter your full name.");
      return;
    }

    if (password.length < (isRegister ? 8 : 1)) {
      setError(
        isRegister
          ? "Password must contain at least 8 characters."
          : "Please enter your password."
      );
      return;
    }

    isSubmitting.current = true;
    setLoading(true);

    try {
      const endpoint = isRegister ? "/api/auth/register" : "/api/auth/login";

      const payload = isRegister
        ? {
            full_name: fullName.trim(),
            email: email.trim().toLowerCase(),
            password,
          }
        : {
            email: email.trim().toLowerCase(),
            password,
          };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message =
          typeof result.detail === "string"
            ? result.detail
            : Array.isArray(result.detail)
              ? result.detail.map((item) => item.msg).join(", ")
              : "Authentication failed. Please try again.";

        throw new Error(message);
      }

      // Registration creates the account, then asks the user to sign in.
      if (isRegister) {
        setMode("login");
        setPassword("");
        setSuccess("Account created successfully! Please sign in.");
        return;
      }

      if (!result.access_token) {
        throw new Error("The server did not return an access token.");
      }

      // Keep the session for this browser tab.
      sessionStorage.setItem("datapulse_access_token", result.access_token);

      try {
        await onAuthenticated(result.access_token, result.user);
      } catch (authError) {
        sessionStorage.removeItem("datapulse_access_token");
        throw authError;
      }
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Cannot connect to DataPulse. Check whether the backend is running."
          : err.message || "Something went wrong."
      );
    } finally {
      isSubmitting.current = false;
      setLoading(false);
    }
  }

  function changeMode(nextMode) {
    setMode(nextMode);
    setError("");
    setSuccess("");
    setPassword("");
  }

  return (
    <main className={`auth-page ${theme === "dark" ? "auth-dark" : ""}`}>
      <div className="auth-background auth-background-one" />
      <div className="auth-background auth-background-two" />

      <header className="auth-header">
        <button
          type="button"
          className="auth-brand"
          onClick={onBack}
          aria-label="Return to DataPulse home"
        >
          <span className="auth-brand-icon">D</span>
          <span>
            Data<span className="auth-brand-accent">Pulse</span>
          </span>
        </button>

        <button type="button" className="auth-back-button" onClick={onBack}>
          ← Back to home
        </button>
      </header>

      <section className="auth-layout">
        <div className="auth-intro">
          <span className="auth-eyebrow">
            <span className="auth-live-dot" />
            YOUR DATA. YOUR INSIGHTS.
          </span>

          <h1>
            Make your data
            <br />
            work <span>smarter.</span>
          </h1>

          <p>
            Turn your business data into clear insights, meaningful trends,
            and better decisions with DataPulse.
          </p>

          <div className="auth-feature-list">
            <div className="auth-feature">
              <span className="auth-feature-icon">↗</span>
              <div>
                <strong>Analytics dashboard</strong>
                <span>Understand your business performance.</span>
              </div>
            </div>

            <div className="auth-feature">
              <span className="auth-feature-icon">✳</span>
              <div>
                <strong>AI-powered assistance</strong>
                <span>Explore your data using natural language.</span>
              </div>
            </div>

            <div className="auth-feature">
              <span className="auth-feature-icon">⌁</span>
              <div>
                <strong>Protected account</strong>
                <span>Sign in to access your analytics workspace.</span>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-card">
          <div className="auth-card-heading">
            <span className="auth-card-kicker">
              {isRegister ? "CREATE YOUR ACCOUNT" : "WELCOME BACK"}
            </span>

            <h2>{isRegister ? "Get started" : "Sign in"}</h2>

            <p>
              {isRegister
                ? "Create your DataPulse account in a few seconds."
                : "Enter your details to access your workspace."}
            </p>
          </div>

          <div className="auth-tabs">
            <button
              type="button"
              className={!isRegister ? "active" : ""}
              onClick={() => changeMode("login")}
              disabled={loading}
            >
              Sign in
            </button>

            <button
              type="button"
              className={isRegister ? "active" : ""}
              onClick={() => changeMode("register")}
              disabled={loading}
            >
              Create account
            </button>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {isRegister && (
              <label className="auth-field">
                <span>Full name</span>
                <input
                  type="text"
                  name="full_name"
                  autoComplete="name"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  minLength={2}
                  maxLength={100}
                  required
                  disabled={loading}
                />
              </label>
            )}

            <label className="auth-field">
              <span>Email address</span>
              <input
                type="email"
                name="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                disabled={loading}
              />
            </label>

            <label className="auth-field">
              <span>Password</span>

              <div className="auth-password-wrapper">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  autoComplete={
                    isRegister ? "new-password" : "current-password"
                  }
                  placeholder={
                    isRegister ? "At least 8 characters" : "Enter your password"
                  }
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  minLength={isRegister ? 8 : 1}
                  maxLength={128}
                  required
                  disabled={loading}
                />

                <button
                  type="button"
                  className="auth-show-password"
                  onClick={() => setShowPassword((current) => !current)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </label>

            {error && (
              <div className="auth-message auth-error" role="alert">
                <span>!</span>
                {error}
              </div>
            )}

            {success && (
              <div className="auth-message auth-success" role="status">
                <span>✓</span>
                {success}
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Please wait..."
                : isRegister
                  ? "Create account"
                  : "Sign in to DataPulse"}

              {!loading && <span>→</span>}
            </button>
          </form>

          <div className="auth-card-footer">
            {isRegister ? (
              <>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => changeMode("login")}
                  disabled={loading}
                >
                  Sign in
                </button>
              </>
            ) : (
              <>
                New to DataPulse?{" "}
                <button
                  type="button"
                  onClick={() => changeMode("register")}
                  disabled={loading}
                >
                  Create an account
                </button>
              </>
            )}
          </div>

          <p className="auth-security-note">
            <span>◆</span> Your password is never stored in your browser.
          </p>
        </div>
      </section>

      <footer className="auth-footer">
        <span>© {new Date().getFullYear()} DataPulse</span>
        <span>Analytics made clearer.</span>
      </footer>
    </main>
  );
}