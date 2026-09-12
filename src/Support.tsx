import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  Link,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  HeartHandshake,
  LockKeyhole,
  MapPin,
  MessageCircle,
  Phone,
  ShieldCheck,
} from "lucide-react";
import axios from "axios";

// Deliberately separate from the guardian client: no guardian credential interceptor.
const supportApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 30000,
});
const receiptKey = "guardrails-youth-receipt";
const choices = [
  {
    id: "secrets",
    title: "Someone is asking me to keep secrets",
    hint: "About chats, gifts, photos, or meeting up.",
  },
  {
    id: "uncomfortable",
    title: "Someone is making me uncomfortable",
    hint: "You don't have to explain why.",
  },
  {
    id: "bullying",
    title: "I'm being bullied or harassed",
    hint: "Hurtful messages, threats, or being targeted.",
  },
  {
    id: "unfamiliar-person",
    title: "This involves someone I don't know well online",
    hint: "Even if they seem friendly or helpful.",
  },
  {
    id: "talk",
    title: "I just want to talk to someone",
    hint: "It's okay to be unsure.",
  },
];
type DetectionContext = {
  linked_alert_id: string;
  pattern_type: string;
  risk_level: string;
  suggested_context: string;
};
type Receipt = {
  id: string;
  status: string;
  urgency_level: string;
  created_at: string;
  expires_at: string;
  context_shared: boolean;
  simulated: boolean;
  human_contacted: boolean;
  aid_route: {
    aid_channel_name: string;
    status: string;
    routed_at: string;
  } | null;
};
type PrivateReceipt = { id: string; token: string };

function supportError(error: unknown) {
  if (
    axios.isAxiosError(error) &&
    typeof error.response?.data?.detail === "string"
  )
    return error.response.data.detail;
  return "We couldn't complete that just now. Your choices are still here. You can try again or use the help numbers above.";
}
function readReceipt(): PrivateReceipt | null {
  try {
    const value = JSON.parse(sessionStorage.getItem(receiptKey) || "null");
    return value &&
      typeof value.id === "string" &&
      typeof value.token === "string"
      ? value
      : null;
  } catch {
    return null;
  }
}
function randomToken() {
  return Array.from(crypto.getRandomValues(new Uint8Array(32)), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

export default function Support() {
  const [crisis, setCrisis] = useState(false);
  const crisisHeading = useRef<HTMLHeadingElement>(null);
  const location = useLocation();
  const mainHeading = useRef<HTMLElement>(null);
  useEffect(() => {
    document.title = "Your support space · Digital Guardrails";
    mainHeading.current?.focus();
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    if (crisis) crisisHeading.current?.focus();
  }, [crisis]);
  return (
    <div className="youth-shell">
      <a href="#youth-main" className="skip-link">
        Skip to support
      </a>
      <header className="youth-header">
        <Link to="/help" className="youth-brand">
          <span>
            <HeartHandshake size={24} />
          </span>
          <div>
            digital guardrails<small>Your support space</small>
          </div>
        </Link>
        <span className="youth-private">
          <LockKeyhole size={15} /> No account needed
        </span>
      </header>
      <div className="youth-crisis-wrap">
        <button
          className="youth-crisis-button magnetic"
          aria-expanded={crisis}
          aria-controls="immediate-help"
          onClick={() => setCrisis(!crisis)}
          onPointerMove={(event) => {
            if (
              event.pointerType !== "mouse" ||
              matchMedia("(prefers-reduced-motion: reduce)").matches
            )
              return;
            const rect = event.currentTarget.getBoundingClientRect();
            event.currentTarget.style.setProperty(
              "--mx",
              `${(event.clientX - rect.left - rect.width / 2) * 0.04}px`,
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
          <Phone size={18} /> I'm in immediate danger / Talk to someone now{" "}
          <ArrowRight size={17} />
        </button>
        <section
          id="immediate-help"
          hidden={!crisis}
          className="youth-crisis-panel"
        >
          <h2 ref={crisisHeading} tabIndex={-1}>
            You can reach out right now.
          </h2>
          <p>
            You don't need to finish a report. If you can, move somewhere safer
            and reach a trusted person nearby.
          </p>
          <div className="youth-phone-grid">
            <a href="tel:112">
              <strong>112</strong>
              <span>Emergency assistance in India</span>
              <Phone size={19} />
            </a>
            <a href="tel:1098">
              <strong>1098</strong>
              <span>Child Helpline in India</span>
              <Phone size={19} />
            </a>
          </div>
          <p>
            These are real phone numbers. Calling opens your phone's dialler;
            this website does not place a call or send your report. A helpline
            may ask for details to help you.
          </p>
          <div className="youth-source-links">
            <a href="https://112.gov.in/" target="_blank" rel="noreferrer">
              About 112
            </a>
            <a
              href="https://www.spniwcd.wcd.gov.in/child-helpline"
              target="_blank"
              rel="noreferrer"
            >
              About Child Helpline 1098
            </a>
          </div>
        </section>
      </div>
      <main
        id="youth-main"
        ref={mainHeading}
        tabIndex={-1}
        className="youth-main"
      >
        <Routes>
          <Route index element={<Welcome />} />
          <Route path="report" element={<ReportForm />} />
          <Route path="confirmation/:id" element={<Confirmation />} />
          <Route path="status" element={<Confirmation />} />
          <Route
            path="*"
            element={
              <div className="youth-card">
                <h1>Let's find your support space.</h1>
                <Link to="/help" className="youth-action">
                  Go to support
                </Link>
              </div>
            }
          />
        </Routes>
      </main>
      <footer className="youth-footer">
        <ShieldCheck size={18} />
        <p>
          No names or contact details required. Your report is separate from the
          guardian dashboard. This demo is not monitored by a support worker.
        </p>
        <Link to="/">Guardian workspace</Link>
      </footer>
    </div>
  );
}

function Welcome() {
  return (
    <div className="youth-welcome youth-enter">
      <section>
        <span className="youth-kicker">A LITTLE SPACE TO BE HEARD</span>
        <h1>
          You don't have to figure
          <br className="hidden sm:block" /> it out alone.
        </h1>
        <p className="youth-lead">
          Feeling unsafe or unsure about something online? You can tell us — no
          names needed.
        </p>
        <Link to="/help/report" className="youth-action">
          Tell us what's on your mind <ArrowRight size={18} />
        </Link>
        <Link to="/help/status" className="youth-text-link">
          I already have a private receipt <ArrowRight size={15} />
        </Link>
      </section>
      <aside className="youth-card youth-promise">
        <span className="youth-emblem">
          <HeartHandshake size={34} />
        </span>
        <h2>At your pace. In your words.</h2>
        <ul>
          <li>
            <Check size={17} /> Start with a choice, no typing needed.
          </li>
          <li>
            <Check size={17} /> Share as much or as little as you want.
          </li>
          <li>
            <Check size={17} /> You can ask for help without an alert.
          </li>
        </ul>
        <div className="youth-demo-note">
          <strong>A practice support space</strong>
          <p>
            Reports stay in this local demo for 7 days and go to a simulated aid
            channel. No helpline or person receives them. Use “Talk to someone
            now” for real help options.
          </p>
        </div>
      </aside>
    </div>
  );
}

function ReportForm() {
  const location = useLocation();
  const navigate = useNavigate();
  const [contextToken] = useState<string | null>(() =>
    typeof location.state?.supportContext === "string"
      ? location.state.supportContext
      : null,
  );
  const [context, setContext] = useState<DetectionContext | null>(null);
  const [contextNotice, setContextNotice] = useState("");
  const [selection, setSelection] = useState("talk");
  const [step, setStep] = useState(1);
  const [notes, setNotes] = useState("");
  const [urgency, setUrgency] = useState("Medium");
  const [locality, setLocality] = useState("South Delhi");
  const [customLocality, setCustomLocality] = useState("");
  const [availableLocalities, setAvailableLocalities] = useState<string[]>([
    "South Delhi",
    "North Delhi",
    "Mumbai Suburban",
    "Bengaluru Urban",
    "Kolkata Central",
    "Other",
  ]);
  const [shareContext, setShareContext] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const token = useRef<string | null>(null);
  const pending = useRef(false);
  const selectionTouched = useRef(false);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
  }, [step]);
  useEffect(() => {
    supportApi
      .get<string[]>("/ngo/localities")
      .then(({ data }) => {
        const list = data.filter((l) => l !== "All Localities");
        if (list.length > 0) setAvailableLocalities(list);
      })
      .catch(() => {});
  }, []);
  useEffect(() => {
    if (!contextToken) return;
    let current = true;
    // Remove the capability from history after taking it into transient component state.
    navigate(location.pathname, { replace: true, state: null });
    supportApi
      .post<DetectionContext>("/support/context", {
        context_token: contextToken,
      })
      .then(({ data }) => {
        if (current) {
          setContext(data);
          if (!selectionTouched.current) setSelection(data.suggested_context);
        }
      })
      .catch(() => {
        if (current)
          setContextNotice(
            "The earlier suggestion isn't available. You can still make a report with any choice below.",
          );
      });
    return () => {
      current = false;
    };
  }, [contextToken, navigate, location.pathname]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError("");
    const targetLocality =
      locality === "Other"
        ? (customLocality.trim() || "National Hub")
        : locality;
    try {
      token.current ||= randomToken();
      const { data } = await supportApi.post<Receipt>("/support/reports", {
        anonymous_token: token.current,
        selected_context: selection,
        report_text: notes,
        urgency_level: urgency,
        locality: targetLocality,
        share_detection_context: shareContext,
        ...(shareContext && context
          ? {
              context_token: contextToken,
              linked_alert_id: context.linked_alert_id,
            }
          : {}),
      });
      const saved = { id: data.id, token: token.current };
      try {
        sessionStorage.setItem(receiptKey, JSON.stringify(saved));
      } catch {
        /* In-memory receipt is still available. */
      }
      setNotes("");
      navigate(`/help/confirmation/${data.id}`, {
        replace: true,
        state: { receipt: saved },
      });
    } catch (err) {
      setError(supportError(err));
    } finally {
      setBusy(false);
      pending.current = false;
    }
  }
  return (
    <div className="youth-form-layout">
      <section className="youth-card youth-form-card">
        <div className="youth-step-label">
          <span>YOUR CHOICE, EVERY STEP</span>
          <span>Step {step} of 2</span>
        </div>
        <div className="youth-progress" aria-hidden="true">
          <span />
          <span className={step === 2 ? "complete" : ""} />
        </div>
        <div key={step} className="youth-enter">
          <h1 ref={heading} tabIndex={-1}>
            {step === 1
              ? "What feels closest to your situation?"
              : "Only what you're ready to share."}
          </h1>
          <p className="youth-intro">
            {step === 1
              ? "There isn't a wrong answer. You can change your choice, or just choose to talk."
              : "Your choice is enough to ask for support. The message box is optional."}
          </p>
          {step === 1 ? (
            <>
              {context && (
                <p className="youth-context-note">
                  An earlier safety signal suggested a starting choice. It may
                  be wrong — choose what fits. Nothing from that alert is
                  attached unless you choose to share it in the next step.
                </p>
              )}
              {contextNotice && (
                <p role="status" className="youth-context-note">
                  {contextNotice}
                </p>
              )}
              <fieldset className="youth-options">
                <legend className="sr-only">Choose what feels closest</legend>
                {choices.map((choice, index) => (
                  <label
                    key={choice.id}
                    className={`youth-option youth-enter ${selection === choice.id ? "selected" : ""}`}
                    style={{ animationDelay: `${index * 80}ms` }}
                  >
                    <input
                      type="radio"
                      name="situation"
                      value={choice.id}
                      checked={selection === choice.id}
                      onChange={() => {
                        selectionTouched.current = true;
                        setSelection(choice.id);
                      }}
                    />
                    <span>
                      <strong>{choice.title}</strong>
                      <small>{choice.hint}</small>
                    </span>
                  </label>
                ))}
              </fieldset>
              <button className="youth-action" onClick={() => setStep(2)}>
                Continue at my pace <ArrowRight size={18} />
              </button>
            </>
          ) : (
            <form onSubmit={submit}>
              <div className="youth-selected">
                <MessageCircle size={19} />
                <span>
                  {choices.find((item) => item.id === selection)?.title}
                </span>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => setStep(1)}
                >
                  Change
                </button>
              </div>
              <label className="youth-field">
                Anything you'd like to add?{" "}
                <span>
                  Optional. Leave out names, phone numbers, addresses, and other
                  identifying details.
                </span>
                <textarea
                  maxLength={1500}
                  value={notes}
                  disabled={busy}
                  onChange={(event) => setNotes(event.target.value)}
                  placeholder="You can leave this empty."
                />
              </label>
              <p className="youth-count">{notes.length} / 1500</p>
              <div className="my-4 p-3.5 rounded-xl bg-blue-50/70 border border-blue-200/80">
                <label className="font-semibold text-xs text-blue-950 flex items-center gap-1.5 mb-1">
                  <MapPin size={14} className="text-blue-600" />
                  Where are you located? (Your District or City)
                </label>
                <select
                  value={locality}
                  disabled={busy}
                  onChange={(e) => setLocality(e.target.value)}
                  className="mt-1 !py-2.5 !px-3 !text-xs !bg-white border border-slate-200 rounded-lg w-full font-medium"
                >
                  {availableLocalities.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
                {locality === "Other" && (
                  <input
                    type="text"
                    placeholder="Type your district or city name..."
                    value={customLocality}
                    disabled={busy}
                    onChange={(e) => setCustomLocality(e.target.value)}
                    className="mt-2 !py-2 !px-3 !text-xs !bg-white border border-slate-200 rounded-lg w-full"
                  />
                )}
                <small className="text-[11px] text-blue-800 mt-1.5 block leading-relaxed">
                  📍 Your anonymous request will be sent directly to the accredited Child Welfare Committee (CWC) & NGO stationed in <strong>{locality === "Other" ? (customLocality || "your area") : locality}</strong>.
                </small>
              </div>
              <fieldset className="youth-urgency">
                <legend>How soon would you like support?</legend>
                {[
                  ["Low", "I can take my time"],
                  ["Medium", "Soon, please"],
                  ["High", "As soon as possible"],
                ].map(([value, label]) => (
                  <label key={value}>
                    <input
                      type="radio"
                      name="urgency"
                      value={value}
                      checked={urgency === value}
                      disabled={busy}
                      onChange={() => setUrgency(value)}
                    />
                    <span>{label}</span>
                  </label>
                ))}
              </fieldset>
              {urgency === "High" && (
                <p className="youth-context-note" role="status">
                  This demo cannot send urgent help. Use “Talk to someone now”
                  above to see real help numbers immediately.
                </p>
              )}
              {context && (
                <label className="youth-consent">
                  <input
                    type="checkbox"
                    checked={shareContext}
                    disabled={busy}
                    onChange={(event) => setShareContext(event.target.checked)}
                  />
                  <span>
                    Attach the earlier safety signal
                    <small>
                      Shares only its pattern category and risk level with the
                      simulated aid channel. No chat text or guardian details.
                      This is optional.
                    </small>
                  </span>
                </label>
              )}
              <div className="youth-demo-note">
                <strong>What happens when I submit?</strong>
                <p>
                  Your choices and optional message are saved for 7 days in this
                  demo and routed to a simulated aid channel. No human or real
                  service is contacted. This app does not show your report in
                  the guardian dashboard.
                </p>
              </div>
              {error && (
                <p className="youth-error" role="alert">
                  {error}
                </p>
              )}
              <div className="youth-form-actions">
                <button
                  type="button"
                  className="youth-text-link"
                  disabled={busy}
                  onClick={() => setStep(1)}
                >
                  <ArrowLeft size={16} /> Back
                </button>
                <button type="submit" className="youth-action" disabled={busy}>
                  {busy
                    ? "Saving your report…"
                    : "Submit anonymous demo report"}
                  <ArrowRight size={17} />
                </button>
              </div>
            </form>
          )}
        </div>
      </section>
      <aside className="youth-reassurance">
        <HeartHandshake size={30} />
        <h2>You deserve to be heard.</h2>
        <p>
          You don't need to prove something happened before asking for support.
        </p>
        <p>
          You're in control of what you share. You can stop here and use the
          help numbers at any time.
        </p>
        <div>
          <LockKeyhole size={18} />
          <p>
            No account or contact details needed. This browser may keep a record
            of your visit. Only a private receipt code lets you check your
            report status.
          </p>
        </div>
      </aside>
    </div>
  );
}

function Confirmation() {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [saved, setSaved] = useState<PrivateReceipt | null>(() => {
    const candidate = location.state?.receipt || readReceipt();
    return candidate && (!id || candidate.id === id) ? candidate : null;
  });
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [code, setCode] = useState("");
  const [showCode, setShowCode] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (location.state?.receipt)
      navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);
  useEffect(() => {
    if (!saved) return;
    let current = true;
    setBusy(true);
    setReceipt(null);
    setError("");
    supportApi
      .get<Receipt>(`/support/reports/${saved.id}`, {
        headers: { Authorization: `Bearer ${saved.token}` },
      })
      .then(({ data }) => {
        if (current) setReceipt(data);
      })
      .catch((err) => {
        if (current) setError(supportError(err));
      })
      .finally(() => {
        if (current) setBusy(false);
      });
    return () => {
      current = false;
    };
  }, [saved]);
  function restore(event: FormEvent) {
    event.preventDefault();
    const [reportId, secret] = code.trim().split(".");
    if (
      !/^[a-f0-9-]{36}$/.test(reportId || "") ||
      !/^[a-f0-9]{64}$/.test(secret || "")
    ) {
      setError("Please enter the complete private receipt code.");
      return;
    }
    const next = { id: reportId, token: secret };
    setSaved(next);
    setCode("");
    try {
      sessionStorage.setItem(receiptKey, JSON.stringify(next));
    } catch {
      /* Receipt remains in memory. */
    }
  }
  async function retry() {
    if (!saved) return;
    setBusy(true);
    setError("");
    try {
      const { data } = await supportApi.post<Receipt>(
        `/support/reports/${saved.id}/retry`,
        {},
        { headers: { Authorization: `Bearer ${saved.token}` } },
      );
      setReceipt(data);
    } catch (err) {
      setError(supportError(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="youth-card youth-receipt youth-enter">
      <span className="youth-emblem">
        <HeartHandshake size={32} />
      </span>
      <span className="youth-kicker">YOUR PRIVATE RECEIPT</span>
      <h1>{receipt ? "Thank you for sharing." : "Check in on your report."}</h1>
      <p className="youth-intro">
        {receipt
          ? "Asking for support is enough. You don't need to share anything more."
          : "Use your private receipt to check its status. No login needed."}
      </p>
      {busy && (
        <p role="status" className="youth-context-note">
          Checking your receipt…
        </p>
      )}
      {error && (
        <p role="alert" className="youth-error">
          {error}
        </p>
      )}
      {receipt && (
        <>
          <div className="youth-route-status" role="status">
            <Check size={22} />
            <div>
              <strong>
                {receipt.status === "routed"
                  ? "Routed · simulation only"
                  : "Saved · routing pending"}
              </strong>
              <p>
                {receipt.aid_route?.aid_channel_name ||
                  "Your report is saved. You can retry the simulated route."}
              </p>
            </div>
          </div>
          <div className="youth-demo-note">
            <strong>No human or helpline has been contacted.</strong>
            <p>
              This receipt demonstrates how a future verified aid connection
              could work. It is not a real request for emergency help. Real help
              numbers are available through “Talk to someone now”.
            </p>
          </div>
          <dl className="youth-receipt-details">
            <div>
              <dt>Report reference</dt>
              <dd>{receipt.id}</dd>
            </div>
            <div>
              <dt>Earlier safety signal</dt>
              <dd>
                {receipt.context_shared
                  ? "Shared with your permission"
                  : "Not attached"}
              </dd>
            </div>
            <div>
              <dt>Available until</dt>
              <dd>{new Date(receipt.expires_at).toLocaleString("en-IN")}</dd>
            </div>
          </dl>
          {receipt.status === "submitted" && (
            <button disabled={busy} className="youth-action" onClick={retry}>
              Retry simulated routing
            </button>
          )}
        </>
      )}
      {saved && (
        <div className="youth-recovery">
          <button
            className="youth-text-link"
            onClick={() => setShowCode(!showCode)}
          >
            {showCode
              ? "Hide private receipt code"
              : "Show my private receipt code"}
          </button>
          {showCode && (
            <label>
              Keep this somewhere private
              <input
                readOnly
                value={`${saved.id}.${saved.token}`}
                onFocus={(event) => event.target.select()}
              />
            </label>
          )}
          <p>
            Anyone with this code can see the status. This tab remembers only
            your latest receipt; closing it may remove access. No report text is
            saved in browser storage.
          </p>
          <button
            className="youth-text-link"
            disabled={busy}
            onClick={() => setSaved({ ...saved })}
          >
            Refresh status
          </button>
        </div>
      )}
      {(!receipt || !saved) && (
        <form className="youth-restore" onSubmit={restore}>
          <label>
            Private receipt code
            <input
              type="password"
              autoComplete="off"
              value={code}
              onChange={(event) => setCode(event.target.value)}
              required
              placeholder="Paste your saved code"
            />
          </label>
          <button type="submit" className="youth-action" disabled={busy}>
            Check status <ArrowRight size={16} />
          </button>
        </form>
      )}
      <div className="youth-form-actions">
        <Link to="/help/report" className="youth-text-link">
          Start another report
        </Link>
        <button
          className="youth-text-link"
          onClick={() => {
            try {
              sessionStorage.removeItem(receiptKey);
            } catch {
              /* No storage to clear. */
            }
            setSaved(null);
            setReceipt(null);
            navigate("/help", { replace: true, state: null });
          }}
        >
          Finish and forget this receipt
        </button>
      </div>
    </section>
  );
}
