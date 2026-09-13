import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
  useParams,
} from "react-router-dom";
import {
  Activity,
  AlertCircle,
  ArrowDownLeft,
  ArrowRight,
  ArrowUpRight,
  Bell,
  BookOpen,
  Building2,
  Check,
  CheckCheck,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Clock3,
  ExternalLink,
  FileCheck,
  Filter,
  FlaskConical,
  HeartHandshake,
  LayoutDashboard,
  LockKeyhole,
  LogOut,
  MapPin,
  Menu,
  MessageSquare,
  MessageSquareQuote,
  Plus,
  Radio,
  RefreshCw,
  Send,
  Settings2,
  Shield,
  ShieldAlert,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  TrendingUp,
  UserCheck,
  Users,
  X,
  type LucideIcon,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  api,
  errorText,
  patternNames,
  type Alert,
  type Analysis,
  type Health,
  type NgoReport,
  type Risk,
  type Summary,
} from "./api";
import Support from "./Support";
import GuardianLogin from "./GuardianLogin";

const cx = (...parts: (string | false | undefined)[]) =>
  parts.filter(Boolean).join(" ");
const relativeTime = (date: string) => {
  const minutes = Math.max(
    0,
    Math.floor((Date.now() - new Date(date).getTime()) / 60000),
  );
  return minutes < 1
    ? "Just now"
    : minutes < 60
      ? `${minutes} min ago`
      : minutes < 1440
        ? `${Math.floor(minutes / 60)} hr ago`
        : new Date(date).toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
          });
};
function Magnetic({
  children,
  onClick,
  type = "button",
  disabled = false,
}: {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
}) {
  const ref = useRef<HTMLButtonElement>(null);
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled}
      onClick={onClick}
      className="primary magnetic"
      onPointerMove={(e) => {
        if (
          e.pointerType !== "mouse" ||
          window.matchMedia("(prefers-reduced-motion: reduce)").matches
        )
          return;
        const r = e.currentTarget.getBoundingClientRect();
        ref.current?.style.setProperty(
          "--mx",
          `${(e.clientX - r.left - r.width / 2) * 0.07}px`,
        );
        ref.current?.style.setProperty(
          "--my",
          `${(e.clientY - r.top - r.height / 2) * 0.12}px`,
        );
      }}
      onPointerLeave={() => {
        ref.current?.style.setProperty("--mx", "0px");
        ref.current?.style.setProperty("--my", "0px");
      }}
    >
      {children}
    </button>
  );
}
function MagneticLink({
  to,
  children,
  className = "",
}: {
  to: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Link
      to={to}
      className={cx("primary-link magnetic", className)}
      onPointerMove={(e) => {
        if (
          e.pointerType !== "mouse" ||
          window.matchMedia("(prefers-reduced-motion: reduce)").matches
        )
          return;
        const r = e.currentTarget.getBoundingClientRect();
        e.currentTarget.style.setProperty(
          "--mx",
          `${(e.clientX - r.left - r.width / 2) * 0.07}px`,
        );
        e.currentTarget.style.setProperty(
          "--my",
          `${(e.clientY - r.top - r.height / 2) * 0.12}px`,
        );
      }}
      onPointerLeave={(e) => {
        e.currentTarget.style.setProperty("--mx", "0px");
        e.currentTarget.style.setProperty("--my", "0px");
      }}
    >
      {children}
    </Link>
  );
}
function Badge({ level }: { level: Risk }) {
  return (
    <span className={cx("risk-badge", level.toLowerCase())}>
      <Shield size={12} />
      {level} risk
    </span>
  );
}
function Notice({ children }: { children: ReactNode }) {
  return (
    <div role="alert" className="error-box">
      {children}
    </div>
  );
}
function Empty({ filtered = false }: { filtered?: boolean }) {
  return (
    <div className="empty-state">
      <ShieldCheck size={36} />
      <h3>
        {filtered
          ? "No alerts match these filters"
          : "A little peace of mind starts here"}
      </h3>
      <p>
        {filtered
          ? "Try another risk level or review status."
          : "Analyze a synthetic conversation in the demo panel to see how a risk signal reaches a guardian."}
      </p>
      {!filtered && (
        <Link className="text-link" to="/demo">
          Open demo panel <ArrowRight size={15} />
        </Link>
      )}
    </div>
  );
}
function Chart({ data }: { data: Summary["trends"] }) {
  return (
    <div
      className="chart"
      role="img"
      aria-label={`Alerts over the last seven days. ${data.map((d) => `${d.date}: ${d.High} high, ${d.Medium} medium, ${d.Low} low`).join("; ")}`}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 12, right: 6, left: -30, bottom: 0 }}
        >
          <defs>
            <linearGradient id="mediumFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#c6a257" stopOpacity={0.14} />
              <stop offset="100%" stopColor="#c6a257" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            vertical={false}
            stroke="#edf0f3"
            strokeDasharray="4 4"
          />
          <XAxis
            dataKey="date"
            tickFormatter={(v) =>
              new Date(v + "T00:00:00").toLocaleDateString("en", {
                weekday: "short",
              })
            }
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#778397" }}
            dy={8}
          />
          <YAxis
            allowDecimals={false}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: "#778397" }}
          />
          <Tooltip
            contentStyle={{
              border: "1px solid #e6eaf0",
              borderRadius: 12,
              fontSize: 13,
            }}
            labelFormatter={(v) =>
              new Date(v + "T00:00:00").toLocaleDateString("en-IN")
            }
          />
          <Area
            type="monotone"
            dataKey="Medium"
            stroke="#bf9b50"
            fill="url(#mediumFill)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="High"
            stroke="#be7778"
            fill="transparent"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="Low"
            stroke="#599b86"
            fill="transparent"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
function PageHeading({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children}
    </div>
  );
}
function AlertCard({ alert, index }: { alert: Alert; index: number }) {
  return (
    <Link
      to={`/alerts/${alert.id}`}
      className="alert-card fade-lift"
      style={{ animationDelay: `${Math.min(index, 7) * 70}ms` }}
    >
      <div className={cx("alert-symbol", alert.risk_level.toLowerCase())}>
        {alert.pattern_type === "bullying-harassment" ? (
          <MessageSquare size={20} />
        ) : (
          <Shield size={20} />
        )}
      </div>
      <div className="alert-main">
        <div className="alert-title">
          <h3>{patternNames[alert.pattern_type]}</h3>
          <Badge level={alert.risk_level} />
        </div>
        <p className="alert-preview">
          {alert.flagged_snippet
            ? `“${alert.flagged_snippet}”`
            : `“${alert.explanation}”`}
        </p>
        <div className="metadata">
          <span>{alert.child_label}</span>
          <span>{alert.source_platform}</span>
          <span>{alert.language}</span>
          <span
            className={cx("review-status", alert.reviewed && "is-reviewed")}
          >
            {alert.reviewed ? (
              <>
                <CheckCheck size={12} /> Reviewed
              </>
            ) : (
              <>
                <span className="small-dot" /> Needs review
              </>
            )}
          </span>
        </div>
      </div>
      <div className="alert-trailing">
        <time>{relativeTime(alert.created_at)}</time>
        <ChevronRight size={18} />
      </div>
    </Link>
  );
}
function Dashboard({
  alerts,
  summary,
  loading,
  error,
  refresh,
}: {
  alerts: Alert[];
  summary: Summary | null;
  loading: boolean;
  error: string;
  refresh: () => void;
}) {
  const [filter, setFilter] = useState("All alerts");
  const [risk, setRisk] = useState("All risks");
  const [child, setChild] = useState("All children");
  const [showFilters, setShowFilters] = useState(false);
  const list = alerts.filter(
    (a) =>
      (filter === "All alerts" ||
        (filter === "Needs review" ? !a.reviewed : a.reviewed)) &&
      (risk === "All risks" || a.risk_level === risk) &&
      (child === "All children" || a.child_label === child),
  );
  return (
    <>
      <PageHeading
        eyebrow="YOUR FAMILY'S SAFETY, AT A GLANCE"
        title="A safer space to grow."
        description="Stay close to what matters, while giving them room to be themselves."
      >
        <MagneticLink to="/demo">
          <FlaskConical size={16} /> Try the demo <ArrowUpRight size={16} />
        </MagneticLink>
      </PageHeading>
      <div className="privacy-banner">
        <span className="privacy-icon">
          <ShieldCheck size={24} />
        </span>
        <div>
          <strong>Protection with privacy at its heart</strong>
          <p>
            You see the signals that need attention. Their private conversations
            stay private.
          </p>
        </div>
        <span className="privacy-tag">
          <LockKeyhole size={13} /> Minimal context only
        </span>
      </div>
      <div className="stats-grid">
        {(
          [
            {
              label: "Messages analyzed",
              value: summary?.messages_analyzed,
              icon: MessageSquare,
              foot: "In the retained demo history",
              tone: "blue",
            },
            {
              label: "Needs your attention",
              value: summary?.unreviewed,
              icon: Bell,
              foot: `${summary?.high_risk ?? 0} high-risk alerts to review`,
              tone: "amber",
            },
            {
              label: "Reviewed with care",
              value: summary?.reviewed,
              icon: CheckCheck,
              foot: "A moment of care goes a long way",
              tone: "green",
            },
          ] as {
            label: string;
            value: number | undefined;
            icon: LucideIcon;
            foot: string;
            tone: string;
          }[]
        ).map((s) => (
          <div className="stat-card" key={s.label}>
            <div className="stat-top">
              <span>{s.label}</span>
              <s.icon className={s.tone} size={19} />
            </div>
            <div className="stat-value">{s.value ?? "—"}</div>
            <p>{s.foot}</p>
          </div>
        ))}
      </div>
      <div className="dashboard-grid">
        <section className="feed-section">
          <div className="section-heading">
            <div>
              <h2>
                Your alert feed{" "}
                <span className="count-bubble">{alerts.length}</span>
              </h2>
              <p>A little context. A clear next step.</p>
            </div>
            <button
              className="icon-button"
              aria-label="Refresh alerts"
              onClick={refresh}
            >
              <RefreshCw size={17} className={loading ? "spin" : ""} />
            </button>
          </div>
          <div className="feed-toolbar">
            <div className="tabs">
              {["All alerts", "Needs review", "Reviewed"].map((t) => (
                <button
                  key={t}
                  aria-pressed={filter === t}
                  onClick={() => setFilter(t)}
                  className={filter === t ? "active" : ""}
                >
                  {t}
                </button>
              ))}
            </div>
            <button
              className={cx("filter-button", showFilters && "selected")}
              onClick={() => setShowFilters(!showFilters)}
              aria-expanded={showFilters}
              aria-label="Filters"
            >
              <SlidersHorizontal size={14} />
              <span>Filters</span>
            </button>
          </div>
          {showFilters && (
            <div className="filter-row">
              <label>
                Risk level
                <select value={risk} onChange={(e) => setRisk(e.target.value)}>
                  {["All risks", "High", "Medium", "Low"].map((v) => (
                    <option key={v}>{v}</option>
                  ))}
                </select>
              </label>
              <label>
                Child profile
                <select
                  value={child}
                  onChange={(e) => setChild(e.target.value)}
                >
                  {["All children", "Child 1", "Child 2"].map((v) => (
                    <option key={v}>{v}</option>
                  ))}
                </select>
              </label>
            </div>
          )}
          {error ? (
            <Notice>
              {error} <button onClick={refresh}>Try again</button>
            </Notice>
          ) : loading && !summary ? (
            <div className="loading-state">Loading your safety overview…</div>
          ) : list.length ? (
            <div className="alert-list">
              {list.map((a, i) => (
                <AlertCard key={a.id} alert={a} index={i} />
              ))}
            </div>
          ) : (
            <Empty filtered={alerts.length > 0} />
          )}
          <div className="feed-footer">
            <LockKeyhole size={13} />
            <span>
              Only short flagged excerpts are shown. Full chats are never saved.
            </span>
          </div>
        </section>
        <aside className="insights-column">
          <section className="panel">
            <div className="section-heading compact">
              <h2>A week in perspective</h2>
              <TrendingUp size={17} />
            </div>
            <p className="subtle">Alerts over the last 7 days</p>
            <Chart data={summary?.trends ?? []} />
            <div className="chart-legend">
              {["High", "Medium", "Low"].map((v) => (
                <span key={v}>
                  <i className={v.toLowerCase()} />
                  {v}
                </span>
              ))}
            </div>
            <Link className="panel-bottom-link" to="/trends">
              Explore your trends <ArrowRight size={15} />
            </Link>
          </section>
          <section className="care-card">
            <div className="care-icon">
              <HeartHandshake size={27} />
            </div>
            <span className="eyebrow">A GENTLE REMINDER</span>
            <h2>
              Start with a conversation,
              <br />
              not a conclusion.
            </h2>
            <p>
              An alert is a reason to check in. Listen first, let them know
              they’re not in trouble, and take the next step together.
            </p>
            <Link to="/resources" className="text-link">
              Find a way to start <ArrowUpRight size={15} />
            </Link>
          </section>
          <div className="language-note">
            <span className="language-glyph">
              अ<span>അ</span>
            </span>
            <div>
              <strong>Care speaks their language.</strong>
              <p>
                English, Hindi, Malayalam
                <br />
                and the ways they mix.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}
const supportedLanguages = [
  "Hinglish",
  "English",
  "Hindi",
  "Malayalam",
  "Manglish",
];
const guardianDisplayName =
  import.meta.env.VITE_GUARDIAN_DISPLAY_NAME?.trim() || "Guardian workspace";
function Demo({
  health,
  onChange,
}: {
  health: Health | null;
  onChange: () => void;
}) {
  const [language, setLanguage] = useState("Hinglish");
  const [text, setText] = useState("");
  const [child, setChild] = useState("Child 1");
  const [source, setSource] = useState("Gaming chat");
  const [conversation, setConversation] = useState(
    () => `demo-${crypto.randomUUID().slice(0, 8)}`,
  );
  const [result, setResult] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  function reset() {
    setConversation(`demo-${crypto.randomUUID().slice(0, 8)}`);
    setResult(null);
    setText("");
    setError("");
  }
  async function analyze() {
    if (!text.trim() || busy) return;
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const { data } = await api.post<Analysis>("/messages/ingest", {
        text,
        conversation_id: conversation,
        child_label: child,
        source_platform: source,
        language,
      });
      setResult(data);
      setText("");
      onChange();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="SEE THE SAFETY NET IN ACTION"
        title="Small signals. Meaningful context."
        description="Try synthetic messages and follow a pattern as it develops."
      />
      <div className="demo-layout">
        <section className="panel form-panel">
          <div className="section-heading">
            <h2>
              <FlaskConical size={19} /> Demo ingestion
            </h2>
            <span className="pill">Synthetic data only</span>
          </div>
          <p className="subtle mb-6">
            Write a fictional message to explore the detector. Please don’t
            paste a child’s real conversation.
          </p>
          <div className="form-grid">
            <label>
              Child profile
              <select
                disabled={busy}
                value={child}
                onChange={(e) => {
                  setChild(e.target.value);
                  reset();
                }}
              >
                <option>Child 1</option>
                <option>Child 2</option>
              </select>
            </label>
            <label>
              Conversation source
              <select
                disabled={busy}
                value={source}
                onChange={(e) => {
                  setSource(e.target.value);
                  reset();
                }}
              >
                {["Gaming chat", "Social chat", "Study group", "Demo"].map(
                  (v) => (
                    <option key={v}>{v}</option>
                  ),
                )}
              </select>
            </label>
          </div>
          <label className="mt-5">
            Language{" "}
            <select
              disabled={busy}
              value={language}
              onChange={(e) => {
                setLanguage(e.target.value);
                setText("");
                setResult(null);
              }}
            >
              {supportedLanguages.map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <label htmlFor="message" className="mt-5">
            Message to analyze
          </label>
          <textarea
            id="message"
            value={text}
            onChange={(e) => setText(e.target.value)}
            maxLength={2000}
            rows={6}
            placeholder="Type a fictional message here…"
            disabled={busy}
          />
          <div className="input-footer">
            <span>
              <LockKeyhole size={12} /> Cleared after analysis
            </span>
            <span>{text.length} / 2,000</span>
          </div>
          <div className="submit-row">
            <button className="text-link" disabled={busy} onClick={reset}>
              <Plus size={14} /> New conversation
            </button>
            <Magnetic disabled={busy || !text.trim()} onClick={analyze}>
              {busy ? (
                <>
                  <RefreshCw size={16} className="spin" /> Analyzing…
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Analyze message{" "}
                  <ArrowRight size={16} />
                </>
              )}
            </Magnetic>
          </div>
          <p className="conversation-note">
            {conversation} · Continue here to test a sequence. Starting a new
            conversation resets its context.
          </p>
          {error && <Notice>{error}</Notice>}
        </section>
        <aside className="demo-aside">
          <section className="panel result-panel" aria-live="polite">
            {result ? (
              <>
                <div className="section-heading">
                  <h2>Analysis complete</h2>
                  <Check className="green" size={20} />
                </div>
                <div className="result-score">
                  <strong>
                    {result.risk_score}
                    <span>/100</span>
                  </strong>
                  <Badge level={result.risk_level} />
                </div>
                <div className="score-track">
                  <div
                    className={result.risk_level.toLowerCase()}
                    style={{ width: `${result.risk_score}%` }}
                  />
                </div>
                <h3>{patternNames[result.pattern_type]}</h3>
                <p>{result.explanation}</p>
                {result.escalated && (
                  <div className="sequence-note">
                    <TrendingUp size={16} /> Concern increased across the
                    conversation.
                  </div>
                )}
                <div className="model-caption">
                  {result.model}
                  <br />
                  Illustrative concern score, not a probability of harm.
                </div>
                {result.alert_id ? (
                  <Link
                    className="primary-link w-full justify-center"
                    to={`/alerts/${result.alert_id}`}
                  >
                    View the guardian alert <ArrowRight size={16} />
                  </Link>
                ) : (
                  <div className="safe-note">
                    <ShieldCheck size={18} /> No alert saved. No message text
                    retained.
                  </div>
                )}
                <Link
                  className="secondary w-full justify-center mt-4"
                  to="/help/report"
                  state={{ supportContext: result.support_context_token }}
                >
                  <HeartHandshake size={17} /> Open youth support
                </Link>
                <p className="subtle mt-3">
                  The young person can ask for help independently and choose
                  whether to attach this safety signal.
                </p>
              </>
            ) : (
              <div className="result-placeholder">
                <span className="large-shield">
                  <ShieldCheck size={35} />
                </span>
                <h2>A signal, then a next step.</h2>
                <p>
                  Your analysis will appear here with a risk level and a
                  plain-language explanation.
                </p>
                <div className="flow-steps">
                  <span>01 &nbsp; Submit</span>
                  <ChevronRight size={13} />
                  <span>02 &nbsp; Understand</span>
                  <ChevronRight size={13} />
                  <span>03 &nbsp; Support</span>
                </div>
              </div>
            )}
          </section>
          <section className="demo-tip">
            <BookOpen size={21} />
            <div>
              <h3>Try a developing pattern</h3>
              <p>
                Submit successive fictional messages in the same conversation to
                explore how detected patterns affect concern. Results depend on
                the submitted text and the active model.
              </p>
            </div>
          </section>
          <div className="engine-note">
            <Activity size={16} />
            <div>
              <strong>{health?.model ?? "Connecting to detector…"}</strong>
              <p>
                {health?.model_kind === "indicbert"
                  ? "AI4Bharat encoder with a head trained on synthetic examples."
                  : "The offline baseline is active. Model status is always disclosed."}
              </p>
            </div>
          </div>
        </aside>
      </div>
    </>
  );
}
function Detail({ onChange }: { onChange: () => void }) {
  const { id } = useParams();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    setAlert(null);
    setError("");
    api
      .get(`/alerts/${id}`)
      .then((r) => setAlert(r.data))
      .catch((e) => setError(errorText(e)));
  }, [id]);
  async function review() {
    if (!alert) return;
    setBusy(true);
    try {
      const { data } = await api.patch(`/alerts/${id}`, {
        reviewed: !alert.reviewed,
      });
      setAlert(data);
      onChange();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Link to="/" className="text-link back-link">
        <ArrowDownLeft size={16} /> Back to your dashboard
      </Link>
      {error && <Notice>{error}</Notice>}
      {alert ? (
        <div className="detail-reveal">
          <PageHeading
            eyebrow={`${alert.child_label.toUpperCase()} · ${alert.source_platform.toUpperCase()}`}
            title={patternNames[alert.pattern_type]}
            description={`Flagged ${new Date(alert.created_at).toLocaleString("en-IN")} · ${alert.language}`}
          >
            <Badge level={alert.risk_level} />
          </PageHeading>
          <div className="detail-grid">
            <section className="panel detail-main">
              <div className="detail-score">
                <div>
                  <span className="eyebrow">CONCERN SCORE</span>
                  <strong>
                    {alert.risk_score}
                    <small>/100</small>
                  </strong>
                </div>
                <div>
                  <Badge level={alert.risk_level} />
                  <p>
                    For prioritizing review.
                    <br />
                    Not a probability of harm.
                  </p>
                </div>
              </div>
              <hr />
              <h2>What we noticed</h2>
              <p>{alert.explanation}</p>
              <div className="snippet-box">
                <span>
                  <LockKeyhole size={13} /> FLAGGED MESSAGE EXCERPT
                </span>
                <blockquote>
                  {alert.flagged_snippet
                    ? `“${alert.flagged_snippet}”`
                    : `“${alert.explanation}”`}
                </blockquote>
              </div>
              <p className="model-caption">
                Detected by {alert.model}. This prototype can miss risks or flag
                harmless messages. Review the context with your child.
              </p>
              <button
                className={cx(
                  "secondary w-full justify-center",
                  alert.reviewed && "reviewed-button",
                )}
                disabled={busy}
                onClick={review}
              >
                <CheckCheck size={17} />
                {busy
                  ? "Saving…"
                  : alert.reviewed
                    ? "Reviewed · Mark as unreviewed"
                    : "Mark as reviewed"}
              </button>
            </section>
            <aside>
              <section className="care-card detail-care">
                <HeartHandshake size={28} />
                <h2>Take the next step together.</h2>
                <ol>
                  <li>
                    <strong>Make space to listen.</strong>
                    <p>
                      Ask how they feel about the interaction, without blame or
                      pressure.
                    </p>
                  </li>
                  <li>
                    <strong>Agree on a safer next step.</strong>
                    <p>
                      Discuss pausing contact and using the platform’s block or
                      report tools.
                    </p>
                  </li>
                  <li>
                    <strong>Find support when needed.</strong>
                    <p>
                      A trusted adult or a child-support service can help you
                      decide what to do next.
                    </p>
                  </li>
                </ol>
                <MagneticLink className="w-full justify-center" to="/resources">
                  View support resources <ArrowUpRight size={16} />
                </MagneticLink>
              </section>
              <p className="quiet-note">
                <LockKeyhole size={14} /> Full private conversations are never
                available in this dashboard.
              </p>
            </aside>
          </div>
        </div>
      ) : (
        !error && (
          <div className="loading-state">Opening the necessary context…</div>
        )
      )}
    </>
  );
}
function Trends({
  summary,
  alerts,
  error,
}: {
  summary: Summary | null;
  alerts: Alert[];
  error: string;
}) {
  return (
    <>
      <PageHeading
        eyebrow="THE BIGGER PICTURE"
        title="Patterns over time."
        description="A measured view of the signals in your retained demo history."
      >
        <MagneticLink to="/">
          Review your alerts <ArrowRight size={16} />
        </MagneticLink>
      </PageHeading>
      {error && <Notice>{error}</Notice>}
      <div className="trends-grid">
        <section className="panel large-chart">
          <div className="section-heading">
            <h2>Alert activity</h2>
            <span className="pill">Last 7 days · UTC</span>
          </div>
          <Chart data={summary?.trends ?? []} />
          <div className="chart-legend">
            {["High", "Medium", "Low"].map((v) => (
              <span key={v}>
                <i className={v.toLowerCase()} />
                {v} risk
              </span>
            ))}
          </div>
        </section>
        <section className="panel">
          <h2>Patterns to understand</h2>
          <p className="subtle">All retained alerts, including reviewed</p>
          <div className="pattern-bars">
            {Object.entries(patternNames)
              .filter(([key]) => key !== "neutral")
              .map(([key, name]) => {
                const count = alerts.filter(
                  (a) => a.pattern_type === key,
                ).length;
                return (
                  <div key={key}>
                    <div>
                      <span>{name}</span>
                      <strong>{count}</strong>
                    </div>
                    <div className="bar-track">
                      <span
                        style={{
                          width: `${(count / Math.max(alerts.length, 1)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
          </div>
          <div className="safe-note">
            <ShieldCheck size={20} /> {summary?.reviewed ?? 0} of{" "}
            {summary?.total_alerts ?? 0} alerts reviewed
          </div>
        </section>
      </div>
      <div className="privacy-banner mt-6">
        <LockKeyhole size={22} />
        <div>
          <strong>Less data, more intention.</strong>
          <p>
            These charts use counts and risk categories. They never need the
            full conversation.
          </p>
        </div>
      </div>
    </>
  );
}
function Settings({
  onChange,
  health,
}: {
  onChange: () => void;
  health: Health | null;
}) {
  const [retention, setRetention] = useState(7);
  const [snippets, setSnippets] = useState(true);
  const [token, setToken] = useState(
    () => sessionStorage.getItem("guardrails-token") ?? "",
  );
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    api
      .get("/settings")
      .then(({ data }) => {
        setRetention(data.retention_days);
        setSnippets(data.snippets_enabled);
      })
      .catch((e) => setError(errorText(e)));
  }, []);
  async function save() {
    setBusy(true);
    setError("");
    setSaved(false);
    try {
      await api.patch("/settings", {
        retention_days: retention,
        snippets_enabled: snippets,
      });
      setSaved(true);
      onChange();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        eyebrow="YOUR FAMILY, YOUR BOUNDARIES"
        title="Privacy by choice."
        description="Keep just what helps, for only as long as it’s needed."
      />
      <div className="settings-layout">
        <section className="panel settings-panel">
          <h2>
            <LockKeyhole size={20} /> Privacy & retention
          </h2>
          <div className="setting-row">
            <div>
              <h3>Keep short flagged excerpts</h3>
              <p>
                Up to 140 characters from a flagged message, with email
                addresses, phone numbers, and links removed. Turning this off
                also clears saved excerpts.
              </p>
            </div>
            <button
              role="switch"
              aria-checked={snippets}
              aria-label="Keep short flagged excerpts"
              className={cx("toggle", snippets && "on")}
              onClick={() => {
                setSnippets(!snippets);
                setSaved(false);
              }}
            >
              <span />
            </button>
          </div>
          <div className="setting-row">
            <div>
              <h3>Alert retention</h3>
              <p>
                Older alerts and inactive conversation metadata are deleted when
                the service handles a request or starts.
              </p>
            </div>
            <select
              aria-label="Alert retention"
              value={retention}
              onChange={(e) => {
                setRetention(Number(e.target.value));
                setSaved(false);
              }}
            >
              {[1, 7, 30].map((n) => (
                <option key={n} value={n}>
                  {n} {n === 1 ? "day" : "days"}
                </option>
              ))}
            </select>
          </div>
          <div className="submit-row">
            <span role="status" className="green">
              {saved && (
                <>
                  <Check size={16} /> Preferences saved
                </>
              )}
            </span>
            <Magnetic disabled={busy} onClick={save}>
              {busy ? "Saving…" : "Save preferences"}
              <Check size={16} />
            </Magnetic>
          </div>
          {error && <Notice>{error}</Notice>}
        </section>
        <aside className="panel">
          <ShieldCheck className="blue" size={28} />
          <h2 className="mt-4">What stays private</h2>
          <ul className="privacy-list">
            <li>
              <Check size={15} /> No full conversation logs
            </li>
            <li>
              <Check size={15} /> No real names required
            </li>
            <li>
              <Check size={15} /> No message text in analytics
            </li>
            <li>
              <Check size={15} /> No messages sent to an AI API
            </li>
          </ul>
          <p className="subtle">
            Youth reports stay separate from this dashboard. Guardian login is
            available when configured. This prototype still needs independent
            safety evaluation.
          </p>
        </aside>
        <section className="panel">
          <h2>Guardian access</h2>
          <p className="subtle mb-5">
            {health?.guardian_login_enabled
              ? "Guardian sign-in is enabled. Use the sign-in page to start a one-hour session."
              : health?.access_protected
                ? "This service requires a shared demo access token."
                : "The local demo is open on this machine. A hosted demo requires an access token."}
          </p>
          {health?.guardian_login_enabled && (
            <Link to="/login" className="text-link mb-5">
              Open guardian sign in
            </Link>
          )}
          {!health?.guardian_login_enabled && (
            <>
              <label>
                Access token
                <input
                  type="password"
                  autoComplete="off"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Enter a token if your host requires one"
                />
              </label>
              <button
                className="secondary mt-4"
                onClick={() => {
                  sessionStorage.setItem("guardrails-token", token);
                  setError("");
                  onChange();
                  api
                    .get("/settings")
                    .then(({ data }) => {
                      setRetention(data.retention_days);
                      setSnippets(data.snippets_enabled);
                    })
                    .catch((e) => setError(errorText(e)));
                }}
              >
                Use token for this session
              </button>
            </>
          )}
        </section>
      </div>
    </>
  );
}
function Resources() {
  return (
    <>
      <PageHeading
        eyebrow="CARE BEYOND THE ALERT"
        title="You don’t have to navigate this alone."
        description="A calm first conversation can make it easier for a child to ask for help."
      >
        <MagneticLink to="https://www.cybercrime.gov.in/">
          Official reporting portal <ArrowUpRight size={16} />
        </MagneticLink>
      </PageHeading>
      <div className="resources-grid">
        <section className="care-card">
          <HeartHandshake size={30} />
          <h2>“I’m here to listen.”</h2>
          <p>
            “Has anything online made you uncomfortable lately? You’re not in
            trouble. We can figure out what to do together.”
          </p>
          <p>
            Give them time to respond. Ask what support they want, and avoid
            making promises you cannot keep.
          </p>
        </section>
        <section className="panel">
          <BookOpen size={27} className="blue" />
          <h2 className="mt-4">Find official support</h2>
          <p className="subtle">
            Visit these official services for their current reporting and
            support options.
          </p>
          <a
            className="resource-link"
            href="https://www.cybercrime.gov.in/"
            target="_blank"
            rel="noreferrer"
          >
            National Cyber Crime Reporting Portal <ArrowUpRight size={17} />
          </a>
          <a
            className="resource-link"
            href="https://www.ncpcr.gov.in/"
            target="_blank"
            rel="noreferrer"
          >
            National Commission for Protection of Child Rights{" "}
            <ArrowUpRight size={17} />
          </a>
          <a
            className="resource-link"
            href="https://www.childlineindia.org/"
            target="_blank"
            rel="noreferrer"
          >
            CHILDLINE India <ArrowUpRight size={17} />
          </a>
        </section>
      </div>
    </>
  );
}
function PhysicalLink({
  summary,
  alerts,
}: {
  summary: Summary | null;
  alerts: Alert[];
}) {
  const userRole = sessionStorage.getItem("guardrails-role") || "guardian";
  const userLocality =
    sessionStorage.getItem("guardrails-locality") || "South Delhi";
  const [activeTab, setActiveTab] = useState<
    "inbox" | "simulator" | "partners"
  >("inbox");
  const [localityFilter, setLocalityFilter] = useState<string>(
    userRole === "ngo" ? userLocality : "All Localities",
  );
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [reports, setReports] = useState<NgoReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [workerInputs, setWorkerInputs] = useState<Record<string, string>>({});
  const [notesInputs, setNotesInputs] = useState<Record<string, string>>({});
  const [actionNotice, setActionNotice] = useState<string>("");

  // Simulator state
  const [activeStep, setActiveStep] = useState(2);
  const [selectedAlertId, setSelectedAlertId] = useState<string>(
    alerts.find((a) => a.risk_level === "High")?.id ||
      (alerts[0]?.id ?? "demo-case-1"),
  );
  const [dispatchStatus, setDispatchStatus] = useState<
    "idle" | "dispatching" | "dispatched"
  >("idle");
  const [dispatchLog, setDispatchLog] = useState<{
    id: string;
    agency: string;
    time: string;
  } | null>(null);

  const highRiskCount = alerts.filter((a) => a.risk_level === "High").length;

  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get<NgoReport[]>("/ngo/reports", {
        params: {
          locality:
            localityFilter !== "All Localities" ? localityFilter : undefined,
          status: statusFilter !== "all" ? statusFilter : undefined,
        },
      });
      setReports(data);
    } catch {
      setReports([]);
    } finally {
      setLoading(false);
    }
  }, [localityFilter, statusFilter]);

  useEffect(() => {
    fetchReports();
    const interval = setInterval(fetchReports, 6000);
    return () => clearInterval(interval);
  }, [fetchReports]);

  const updateStatus = async (reportId: string, newStatus: string) => {
    try {
      await api.patch(`/ngo/reports/${reportId}`, { status: newStatus });
      setActionNotice(
        `Case #${reportId.slice(0, 8)} status updated to "${newStatus.replace(/_/g, " ")}".`,
      );
      setTimeout(() => setActionNotice(""), 4000);
      fetchReports();
    } catch (err) {
      alert(errorText(err));
    }
  };

  const assignWorker = async (reportId: string) => {
    const workerName = workerInputs[reportId] || "Ms. S. Sharma (CPO)";
    try {
      await api.patch(`/ngo/reports/${reportId}`, {
        assigned_worker: workerName,
      });
      setActionNotice(
        `Caseworker ${workerName} assigned to Case #${reportId.slice(0, 8)}.`,
      );
      setTimeout(() => setActionNotice(""), 4000);
      fetchReports();
    } catch (err) {
      alert(errorText(err));
    }
  };

  const saveNotes = async (reportId: string) => {
    const notes = notesInputs[reportId] || "";
    try {
      await api.patch(`/ngo/reports/${reportId}`, { caseworker_notes: notes });
      setActionNotice(
        `Intervention notes saved for Case #${reportId.slice(0, 8)}.`,
      );
      setTimeout(() => setActionNotice(""), 4000);
      fetchReports();
    } catch (err) {
      alert(errorText(err));
    }
  };

  const handleSimulateDispatch = () => {
    setDispatchStatus("dispatching");
    setTimeout(() => {
      setDispatchStatus("dispatched");
      setActiveStep(4);
      setDispatchLog({
        id: `PDL-DL-${Math.floor(1000 + Math.random() * 9000)}`,
        agency: "District Child Protection Unit (DCPU) - South Zone",
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      });
    }, 900);
  };

  const steps = [
    {
      num: 1,
      title: "Digital Safety Signal Detected",
      desc: "Multilingual AI pattern analysis flags a high-confidence threat without retaining private conversations.",
      icon: Radio,
    },
    {
      num: 2,
      title: "Guardian / Safeguarding Review",
      desc: "Human-in-the-loop validation: Guardian reviews minimal-context alert summary and authorizes escalation.",
      icon: ShieldCheck,
    },
    {
      num: 3,
      title: "Jurisdictional Routing & Dossier Generation",
      desc: "A simulated referral contains a report reference and the selected concern level.",
      icon: FileCheck,
    },
    {
      num: 4,
      title: "On-Ground Welfare Intervention",
      desc: "Accredited child protection caseworker or juvenile officer assigned for direct welfare check & support.",
      icon: Users,
    },
  ];

  const partners = [
    {
      name: "National Commission for Protection of Child Rights (NCPCR)",
      badge: "Apex Statutory Body",
      role: "Central oversight & regulatory coordination",
      link: "https://www.ncpcr.gov.in/",
      details:
        "Official e-BaalNidan digital complaint gateway for escalating severe rights violations and systemic abuse.",
    },
    {
      name: "CHILDLINE 1098 / Emergency Response",
      badge: "24/7 Rapid Handoff",
      role: "Emergency welfare dispatch",
      link: "https://www.childlineindia.org/",
      details:
        "Immediate on-ground response and transit care for children experiencing imminent online or offline peril.",
    },
    {
      name: "District Child Protection Unit (DCPU) & CWC",
      badge: "Ground Caseworkers",
      role: "Local judicial & protection committee",
      link: "https://www.cybercrime.gov.in/",
      details:
        "Empowered under the Juvenile Justice Act to conduct welfare inquiries, assign social workers, and order protective counseling.",
    },
    {
      name: "Special Juvenile Police Unit (SJPU) & Cyber Cell",
      badge: "Law Enforcement Liaison",
      role: "Child-sensitized cyber unit",
      link: "https://www.cybercrime.gov.in/",
      details:
        "Specialized juvenile police personnel handling serious cyberbullying, extortion, coercion, and syndicate grooming.",
    },
  ];

  const localities = [
    "All Localities",
    "South Delhi",
    "North Delhi",
    "Mumbai Suburban",
    "Bengaluru Urban",
    "Kolkata Central",
    "Other",
  ];

  return (
    <>
      <PageHeading
        eyebrow="CHILD WELFARE & LOCAL AUTHORITIES INTERVENTION"
        title="Casework workspace"
        description="Review support requests by area and record follow-up notes. External referrals are simulated."
      >
        <div className="flex items-center gap-2">
          <span className="text-xs px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-100 font-semibold flex items-center gap-1.5">
            <Building2 size={14} />
            Caseworker Desk · {userLocality}
          </span>
        </div>
      </PageHeading>

      {actionNotice && (
        <div className="mb-5 p-3.5 rounded-xl border border-blue-200 bg-blue-50 text-blue-800 text-xs font-medium flex items-center justify-between">
          <span>{actionNotice}</span>
          <button
            onClick={() => setActionNotice("")}
            className="underline text-blue-700"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Top Sub-Navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-3 mb-6">
        <button
          onClick={() => setActiveTab("inbox")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "inbox"
              ? "bg-blue-600 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
          }`}
        >
          <MessageSquareQuote size={15} />
          Incoming Locality Casework Inbox
          <span
            className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] ${
              activeTab === "inbox"
                ? "bg-blue-700 text-white"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            {reports.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab("simulator")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "simulator"
              ? "bg-blue-600 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
          }`}
        >
          <Radio size={15} />
          Escalation Dispatch Simulator
        </button>

        <button
          onClick={() => setActiveTab("partners")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "partners"
              ? "bg-blue-600 text-white shadow-xs"
              : "bg-white text-slate-600 hover:bg-slate-50 border border-slate-200"
          }`}
        >
          <Building2 size={15} />
          Public support resources
        </button>
      </div>

      {activeTab === "inbox" && (
        <section className="ngo-inbox-section">
          {/* Locality & Status Filter Bar */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="!text-lg">Locality Incident Reports Box</h2>
                <span className="physical-link-badge">Real-time Handoff</span>
              </div>
              <p className="subtle mt-1 text-xs">
                Messages submitted anonymously by youth in this district
                arriving for Child Welfare Committee & NGO review.
              </p>
            </div>

            <div className="ngo-filter-toolbar flex flex-wrap items-center gap-2">
              <div className="ngo-filter-control locality flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs">
                <MapPin size={13} className="text-blue-600" />
                <span className="ngo-filter-label text-slate-500 font-medium">
                  Locality:
                </span>
                <select
                  value={localityFilter}
                  onChange={(e) => setLocalityFilter(e.target.value)}
                  className="ngo-filter-select bg-transparent font-semibold text-slate-700 outline-none !p-0 !border-0 text-xs cursor-pointer"
                >
                  {localities.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
              </div>

              <div className="ngo-filter-control status flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs">
                <Filter size={13} className="text-slate-500" />
                <span className="ngo-filter-label text-slate-500 font-medium">
                  Status:
                </span>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="ngo-filter-select bg-transparent font-semibold text-slate-700 outline-none !p-0 !border-0 text-xs cursor-pointer"
                >
                  <option value="all">All Statuses</option>
                  <option value="submitted">New / Submitted</option>
                  <option value="under_review">Under Review</option>
                  <option value="dispatched">Referral recorded</option>
                  <option value="resolved">Welfare Verified</option>
                </select>
              </div>

              <button
                type="button"
                onClick={fetchReports}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600"
                title="Refresh inbox"
              >
                <RefreshCw
                  size={14}
                  className={loading ? "animate-spin" : ""}
                />
              </button>
            </div>
          </div>

          {/* Reports List */}
          {reports.length === 0 ? (
            <div className="p-12 text-center border border-dashed border-slate-200 rounded-2xl">
              <MessageSquareQuote
                size={36}
                className="mx-auto text-slate-300 mb-3"
              />
              <h3 className="text-base font-semibold text-slate-700 mb-1">
                No incoming reports for {localityFilter}
              </h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                When a student submits an anonymous report choosing this
                locality in the Youth Support Portal (/help), it will arrive
                immediately in this inbox.
              </p>
              <Link to="/help" className="secondary mt-4 inline-flex text-xs">
                Open Youth Support Portal to test submission
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {reports.map((r) => (
                <article key={r.id} className="ngo-case-card">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3 mb-3">
                    <div className="flex items-center gap-2.5">
                      <span className="flex items-center gap-1 text-xs font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
                        <MapPin size={12} /> {r.locality}
                      </span>
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                          r.urgency_level === "High"
                            ? "bg-rose-100 text-rose-700"
                            : r.urgency_level === "Medium"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        Urgency: {r.urgency_level}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      <span
                        className={`font-semibold px-2.5 py-0.5 rounded-full ${
                          r.status === "dispatched"
                            ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                            : r.status === "under_review"
                              ? "bg-amber-100 text-amber-800 border border-amber-200"
                              : r.status === "resolved"
                                ? "bg-slate-100 text-slate-700 border border-slate-200"
                                : "bg-indigo-50 text-indigo-700 border border-indigo-200"
                        }`}
                      >
                        {r.status === "dispatched"
                          ? "● Field Officer Dispatched"
                          : r.status === "under_review"
                            ? "● Under Review"
                            : r.status === "resolved"
                              ? "✓ Welfare Check Resolved"
                              : "★ New Incoming Report"}
                      </span>
                    </div>
                  </div>

                  <div className="mb-2">
                    <span className="text-xs font-medium text-slate-500">
                      Reported Concern:{" "}
                      <strong className="text-slate-800 capitalize">
                        {r.selected_context.replace(/-/g, " ")}
                      </strong>
                    </span>
                  </div>

                  {/* The actual message from youth */}
                  <div className="ngo-message-box">
                    <span className="text-[11px] uppercase tracking-wider font-bold text-slate-500 block mb-1.5 flex items-center gap-1.5">
                      <MessageSquareQuote size={14} className="text-blue-600" />
                      Anonymous Message from Youth:
                    </span>
                    <p className="text-sm font-medium text-slate-800 leading-relaxed whitespace-pre-wrap">
                      {r.report_text && r.report_text.trim()
                        ? r.report_text
                        : "(No custom text message entered. Youth submitted safety signals and urgency level only)."}
                    </p>
                  </div>

                  {/* AI Detection Context */}
                  {r.detection_context && (
                    <div className="p-3 rounded-lg bg-emerald-50/70 border border-emerald-100 mb-3 text-xs flex items-center justify-between">
                      <span className="text-emerald-900 font-medium">
                        Attached Safety Signal:{" "}
                        <strong>
                          {patternNames[
                            r.detection_context.pattern_type || ""
                          ] || r.detection_context.pattern_type}
                        </strong>
                      </span>
                      <span className="text-emerald-700 font-semibold">
                        Risk Level: {r.detection_context.risk_level}
                      </span>
                    </div>
                  )}

                  {/* Casework & Ground Action Bar */}
                  <div className="ngo-case-actions mt-4 pt-3 border-t border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                    <div className="ngo-case-actions-main flex flex-wrap items-center gap-3">
                      <div className="ngo-case-action-group flex items-center gap-1.5">
                        <UserCheck size={14} className="text-slate-400" />
                        <span className="text-slate-500">Officer:</span>
                        {r.assigned_worker ? (
                          <strong className="text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                            {r.assigned_worker}
                          </strong>
                        ) : (
                          <div className="ngo-inline-action flex items-center gap-1">
                            <input
                              type="text"
                              placeholder="e.g. Ms. S. Sharma"
                              value={workerInputs[r.id] ?? ""}
                              onChange={(e) =>
                                setWorkerInputs((prev) => ({
                                  ...prev,
                                  [r.id]: e.target.value,
                                }))
                              }
                              className="!py-1 !px-2 !text-xs !w-36 rounded border border-slate-200"
                            />
                            <button
                              type="button"
                              onClick={() => assignWorker(r.id)}
                              className="secondary !py-1 !px-2 !text-[11px]"
                            >
                              Assign
                            </button>
                          </div>
                        )}
                      </div>

                      {r.caseworker_notes ? (
                        <div className="text-slate-600 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                          <span className="font-semibold text-slate-700">
                            Notes:
                          </span>{" "}
                          {r.caseworker_notes}
                        </div>
                      ) : (
                        <div className="ngo-inline-action flex items-center gap-1">
                          <input
                            type="text"
                            placeholder="Add action note..."
                            value={notesInputs[r.id] ?? ""}
                            onChange={(e) =>
                              setNotesInputs((prev) => ({
                                ...prev,
                                [r.id]: e.target.value,
                              }))
                            }
                            className="!py-1 !px-2 !text-xs !w-40 rounded border border-slate-200"
                          />
                          <button
                            type="button"
                            onClick={() => saveNotes(r.id)}
                            className="secondary !py-1 !px-2 !text-[11px]"
                          >
                            Save Note
                          </button>
                        </div>
                      )}
                    </div>

                    <div className="ngo-case-actions-buttons flex items-center gap-1.5">
                      {r.status !== "under_review" && (
                        <button
                          type="button"
                          onClick={() => updateStatus(r.id, "under_review")}
                          className="px-2.5 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 font-semibold cursor-pointer"
                        >
                          Review Case
                        </button>
                      )}
                      {r.status !== "dispatched" && (
                        <button
                          type="button"
                          onClick={() => updateStatus(r.id, "dispatched")}
                          className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white font-semibold flex items-center gap-1 cursor-pointer"
                        >
                          <Send size={11} /> Dispatch Field Officer
                        </button>
                      )}
                      {r.status !== "resolved" && (
                        <button
                          type="button"
                          onClick={() => updateStatus(r.id, "resolved")}
                          className="px-2.5 py-1 rounded bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 font-semibold cursor-pointer"
                        >
                          Mark Resolved
                        </button>
                      )}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "simulator" && (
        <section className="ground-simulator">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="!text-lg">
                  Ground Intervention Dispatch Simulator
                </h2>
                <span className="physical-link-badge">Interactive Flow</span>
              </div>
              <p className="subtle mt-1">
                Preview a referral workflow. This simulation does not contact a
                caseworker or arrange a visit.
              </p>
            </div>
            <div className="flex items-center gap-3 shrink-0">
              {alerts.length > 0 && (
                <select
                  className="!py-2 !text-xs !w-auto"
                  value={selectedAlertId}
                  onChange={(e) => {
                    setSelectedAlertId(e.target.value);
                    setDispatchStatus("idle");
                    setActiveStep(2);
                  }}
                >
                  {alerts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.child_label} ·{" "}
                      {patternNames[a.pattern_type] || a.pattern_type} (
                      {a.risk_level})
                    </option>
                  ))}
                </select>
              )}
              <button
                className="primary !py-2.5 !px-4 text-xs font-semibold flex items-center gap-2"
                disabled={dispatchStatus === "dispatching"}
                onClick={handleSimulateDispatch}
              >
                {dispatchStatus === "dispatching" ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />{" "}
                    Dispatching…
                  </>
                ) : dispatchStatus === "dispatched" ? (
                  <>
                    <CheckCircle2 size={14} /> Escalation Active
                  </>
                ) : (
                  <>
                    <Send size={14} /> Simulate Ground Handoff
                  </>
                )}
              </button>
            </div>
          </div>

          {dispatchStatus === "dispatched" && dispatchLog && (
            <div className="my-5 p-4 rounded-xl border border-emerald-200 bg-emerald-50/80 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                  <CheckCircle2 size={18} />
                </span>
                <div>
                  <strong className="text-emerald-900 text-sm">
                    Simulated referral created · Reference ID #{dispatchLog.id}
                  </strong>
                  <p className="text-xs text-emerald-700 mt-0.5">
                    Routed to {dispatchLog.agency} at {dispatchLog.time}. No
                    external organization has been contacted.
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setDispatchStatus("idle");
                  setActiveStep(2);
                }}
                className="text-xs text-emerald-800 underline hover:no-underline font-medium shrink-0"
              >
                Reset simulation
              </button>
            </div>
          )}

          <div className="ground-step-list">
            {steps.map((s) => {
              const isCompleted =
                activeStep > s.num || dispatchStatus === "dispatched";
              const isActive =
                activeStep === s.num && dispatchStatus !== "dispatched";
              return (
                <div
                  key={s.num}
                  className={cx(
                    "ground-step-item",
                    isActive && "active",
                    isCompleted && "completed",
                  )}
                >
                  <div
                    className={cx(
                      "ground-step-badge",
                      isCompleted
                        ? "bg-emerald-100 text-emerald-700"
                        : isActive
                          ? "bg-blue-100 text-blue-700"
                          : "bg-slate-100 text-slate-500",
                    )}
                  >
                    {isCompleted ? <Check size={14} /> : s.num}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <strong className="text-sm text-[#1e3a5f]">
                        {s.title}
                      </strong>
                      {isCompleted && (
                        <span className="text-[11px] font-medium text-emerald-600">
                          Verified
                        </span>
                      )}
                      {isActive && (
                        <span className="text-[11px] font-medium text-blue-600">
                          Ready for handoff
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-[#5f738c] mt-1">{s.desc}</p>
                  </div>
                  <s.icon
                    size={18}
                    className={
                      isCompleted
                        ? "text-emerald-500"
                        : isActive
                          ? "text-blue-500"
                          : "text-slate-400"
                    }
                  />
                </div>
              );
            })}
          </div>
        </section>
      )}

      {activeTab === "partners" && (
        <>
          <div className="section-heading mb-4">
            <div>
              <h2>Accredited Partner Organizations & Direct Escalation</h2>
              <p className="subtle mt-0.5">
                Statutory authorities empowered to execute ground welfare checks
                and emergency child care orders.
              </p>
            </div>
          </div>

          <div className="ground-partner-grid">
            {partners.map((p) => (
              <div key={p.name} className="ground-partner-card">
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <span className="physical-link-badge">{p.badge}</span>
                    <a
                      href={p.link}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-blue-600 flex items-center gap-1 hover:underline"
                    >
                      Official Portal <ExternalLink size={12} />
                    </a>
                  </div>
                  <h3 className="text-base font-semibold text-[#1e3a5f] mb-1">
                    {p.name}
                  </h3>
                  <span className="text-xs font-medium text-[#4a6585] block mb-2">
                    {p.role}
                  </span>
                  <p className="text-xs text-[#627792] leading-relaxed">
                    {p.details}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-[#768a9f]">
                  <span className="flex items-center gap-1">
                    <ShieldCheck size={14} className="text-teal-600" />{" "}
                    Statutory Mandate
                  </span>
                  <span className="font-mono text-[11px]">
                    API Status: Active Bridge
                  </span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <div className="panel p-6 border-l-4 !border-l-blue-600 mb-8">
        <h3 className="text-sm font-semibold text-[#1e3a5f] flex items-center gap-2 mb-2">
          <LockKeyhole size={16} className="text-blue-600" /> Prototype limits
          and privacy
        </h3>
        <p className="text-xs text-[#526b88] leading-relaxed">
          This workspace demonstrates report review and referral recording. It
          does not establish legal compliance, verify organizations, or arrange
          emergency intervention. Report notes are retained for case review;
          full private chats are not required.
        </p>
      </div>
    </>
  );
}
function WorkspaceGate() {
  const location = useLocation();
  const hasSession = Boolean(sessionStorage.getItem("guardrails-token"));

  if (!hasSession) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <GuardianApp />;
}

function GuardianApp() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [mobile, setMobile] = useState(false);
  const location = useLocation();

  const userRole = sessionStorage.getItem("guardrails-role") || "guardian";
  const userLocality =
    sessionStorage.getItem("guardrails-locality") || "South Delhi";
  const storedUser = sessionStorage.getItem("guardrails-user");
  const displayName =
    storedUser ||
    (userRole === "ngo" ? "CWC Casework Officer" : guardianDisplayName);

  const handleSignOut = () => {
    sessionStorage.removeItem("guardrails-token");
    sessionStorage.removeItem("guardrails-role");
    sessionStorage.removeItem("guardrails-locality");
    sessionStorage.removeItem("guardrails-user");
    setAlerts([]);
    setSummary(null);
  };

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      if (userRole === "ngo") {
        const { data } = await api.get("/health");
        setHealth(data);
        setAlerts([]);
        setSummary(null);
        setError("");
        return;
      }
      const [a, s, h] = await Promise.all([
        api.get("/alerts"),
        api.get("/dashboard/summary"),
        api.get("/health"),
      ]);
      setAlerts(a.data);
      setSummary(s.data);
      setHealth(h.data);
      setError("");
    } catch (e) {
      setAlerts([]);
      setSummary(null);
      setError(errorText(e));
      api
        .get("/health")
        .then((r) => setHealth(r.data))
        .catch(() => setHealth(null));
    } finally {
      setLoading(false);
    }
  }, [userRole]);
  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 15000);
    return () => clearInterval(timer);
  }, [refresh]);
  useEffect(() => {
    setMobile(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);

  const nav =
    userRole === "ngo"
      ? [
          {
            to: "/physical-link",
            label: "Casework & Dispatch Box",
            icon: Radio,
          },
        ]
      : [
          { to: "/", label: "Overview", icon: LayoutDashboard },
          { to: "/trends", label: "Trends & insights", icon: TrendingUp },
          { to: "/demo", label: "Demo panel", icon: FlaskConical },
        ];

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      {mobile && (
        <button
          className="nav-backdrop"
          aria-label="Close menu"
          onClick={() => setMobile(false)}
        />
      )}
      <aside id="navigation" className={cx("sidebar", mobile && "mobile-open")}>
        <Link
          to={userRole === "ngo" ? "/physical-link" : "/"}
          className="brand"
        >
          <span className="brand-mark">
            <ShieldCheck size={27} />
          </span>
          <span>
            digital
            <span className="brand-second">
              guardrails<span className="brand-period">.</span>
            </span>
          </span>
        </Link>
        <div className="workspace-label">
          {userRole === "ngo"
            ? `CHILD WELFARE & NGO SPACE · ${userLocality.toUpperCase()}`
            : "FAMILY SAFETY SPACE"}
        </div>
        <nav>
          {nav.map((n) => (
            <NavLink end={n.to === "/"} key={n.to} to={n.to}>
              <n.icon size={19} />
              <span>{n.label}</span>
              {n.to === "/" && !!summary?.unreviewed && (
                <span className="nav-count">{summary.unreviewed}</span>
              )}
            </NavLink>
          ))}
          <div className="nav-divider" />
          {userRole === "ngo" ? (
            <>
              <NavLink to="/settings">
                <Settings2 size={19} /> Settings
              </NavLink>
            </>
          ) : (
            <>
              <NavLink to="/resources">
                <BookOpen size={19} /> Support resources
              </NavLink>
              <NavLink to="/settings">
                <Settings2 size={19} /> Settings
              </NavLink>
            </>
          )}
        </nav>
        <div className="sidebar-bottom">
          <div className="privacy-mini">
            <span>
              <LockKeyhole size={15} />{" "}
              {userRole === "ngo" ? "Casework privacy" : "Private by design"}
            </span>
            <p>
              {userRole === "ngo"
                ? `Casework area: ${userLocality}. Access is limited to your assigned area.`
                : "A safety net that respects their growing independence."}
            </p>
          </div>
          <div className="guardian">
            <span className="avatar">{userRole === "ngo" ? "CW" : "DG"}</span>
            <div>
              <strong>{displayName}</strong>
              <span>
                {userRole === "ngo"
                  ? `${userLocality} · Field Welfare Unit`
                  : "Prototype · Guardian View"}
              </span>
            </div>
            <ShieldCheck size={17} />
          </div>
          <Link
            to="/login"
            onClick={handleSignOut}
            className="flex items-center justify-center gap-2 py-2 px-3 mt-3 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 rounded-lg transition-colors text-center"
          >
            <LogOut size={13} /> Sign Out
          </Link>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-menu"
              onClick={() => setMobile(!mobile)}
              aria-label="Open navigation"
              aria-expanded={mobile}
              aria-controls="navigation"
            >
              <Menu size={21} />
            </button>
            <span>Your workspace</span>
            <ChevronRight size={13} />
            <strong>
              {location.pathname === "/demo"
                ? "Demo panel"
                : location.pathname === "/settings"
                  ? "Settings"
                  : location.pathname === "/trends"
                    ? "Trends & insights"
                    : location.pathname === "/resources"
                      ? "Support resources"
                      : location.pathname === "/physical-link"
                        ? "Casework workspace"
                        : location.pathname.startsWith("/alerts/")
                          ? "Alert details"
                          : "Overview"}
            </strong>
          </div>
          <div className="topbar-right">
            {userRole === "ngo" ? (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40">
                <Building2 size={13} /> Child Welfare Unit · {userLocality}
              </span>
            ) : (
              <span className="demo-badge">
                <FlaskConical size={13} /> Parent Mode · Demo Enabled
              </span>
            )}
            <Link
              to="/resources"
              className="icon-button"
              aria-label="Help and support"
            >
              <CircleHelp size={19} />
            </Link>
            <span className="topbar-divider" />
            <span className="small-avatar">
              {userRole === "ngo" ? "CW" : "DG"}
            </span>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          <div className="privacy-banner">
            <ShieldCheck size={19} />
            <span>
              {userRole === "ngo"
                ? `Child Welfare & NGO portal active (${userLocality} Unit). Report routing is a prototype feature.`
                : "Parent & Guardian workspace active. Demo panel and local telemetry monitoring enabled."}
            </span>
            <Link className="text-link" to="/login" onClick={handleSignOut}>
              Sign Out
            </Link>
          </div>
          <Routes>
            <Route
              path="/"
              element={
                userRole === "ngo" ? (
                  <Navigate to="/physical-link" replace />
                ) : (
                  <Dashboard
                    alerts={alerts}
                    summary={summary}
                    loading={loading}
                    error={error}
                    refresh={refresh}
                  />
                )
              }
            />
            <Route
              path="/demo"
              element={
                userRole === "ngo" ? (
                  <Navigate to="/physical-link" replace />
                ) : (
                  <Demo health={health} onChange={refresh} />
                )
              }
            />
            <Route
              path="/alerts/:id"
              element={
                userRole === "ngo" ? (
                  <Navigate to="/physical-link" replace />
                ) : (
                  <Detail onChange={refresh} />
                )
              }
            />
            <Route
              path="/trends"
              element={
                userRole === "ngo" ? (
                  <Navigate to="/physical-link" replace />
                ) : (
                  <Trends summary={summary} alerts={alerts} error={error} />
                )
              }
            />
            <Route
              path="/settings"
              element={<Settings health={health} onChange={refresh} />}
            />
            <Route
              path="/resources"
              element={
                userRole === "ngo" ? (
                  <Navigate to="/physical-link" replace />
                ) : (
                  <Resources />
                )
              }
            />
            <Route
              path="/physical-link"
              element={
                userRole === "ngo" ? (
                  <PhysicalLink summary={summary} alerts={alerts} />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route
              path="*"
              element={
                <div className="empty-state">
                  <h1>This page isn’t here.</h1>
                  <Link to="/">Return to your dashboard</Link>
                </div>
              }
            />
          </Routes>
          <footer className="page-footer">
            <span>
              <ShieldCheck size={14} /> Built for care. Designed for privacy.
            </span>
            <span>
              {health ? health.model : "Safety service unavailable"}{" "}
              <span className="footer-dot">·</span> Bal Suraksha
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/help/*" element={<Support />} />
      <Route path="/support/*" element={<Navigate to="/help" replace />} />
      <Route path="/login" element={<GuardianLogin />} />
      <Route path="/*" element={<WorkspaceGate />} />
    </Routes>
  );
}
