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
  ArrowDownLeft,
  ArrowRight,
  ArrowUpRight,
  Bell,
  BookOpen,
  Check,
  CheckCheck,
  ChevronRight,
  CircleHelp,
  Clock3,
  FlaskConical,
  HeartHandshake,
  LayoutDashboard,
  LockKeyhole,
  Menu,
  MessageSquare,
  Plus,
  RefreshCw,
  Settings2,
  Shield,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  TrendingUp,
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
            : "An excerpt is hidden by your privacy preference."}
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
const samples: Record<string, { label: string; text: string }[]> = {
  Hinglish: [
    {
      label: "Trust-building",
      text: "Tum apni age se bahut mature ho. Sirf main tumhe samajhta hoon. Gift bhejun?",
    },
    {
      label: "Secrecy request",
      text: "Mummy papa ko mat batana. Ye humara secret hai. Private chat pe aao.",
    },
    {
      label: "Harassment",
      text: "Tu loser hai, koi tujhe pasand nahi karta. Group se nikal ja.",
    },
    {
      label: "Everyday chat",
      text: "Kal homework saath mein karte hain, mummy ko bhi bata dena.",
    },
  ],
  English: [
    {
      label: "Trust-building",
      text: "You are so mature for your age. Nobody understands you like I do. I can buy you gifts.",
    },
    {
      label: "Secrecy request",
      text: "Do not tell your parents about us. Delete our chat and move to a private app.",
    },
    {
      label: "Harassment",
      text: "Nobody likes you. You are worthless. Leave our group, loser.",
    },
    {
      label: "Everyday chat",
      text: "Great game! See you tomorrow with the rest of the team.",
    },
  ],
  Hindi: [
    {
      label: "Trust-building",
      text: "तुम अपनी उम्र से बहुत समझदार हो। तुम्हें सिर्फ मैं समझता हूँ। मैं तुम्हें गिफ्ट दूंगा।",
    },
    {
      label: "Secrecy request",
      text: "मम्मी पापा को हमारे बारे में मत बताना। चैट डिलीट कर दो और अकेले मिलने आओ।",
    },
    {
      label: "Harassment",
      text: "तुम बेकार हो। कोई तुम्हें पसंद नहीं करता। हमारे ग्रुप से निकल जाओ।",
    },
    {
      label: "Everyday chat",
      text: "आज स्कूल कैसा था? चलो साथ में होमवर्क करते हैं।",
    },
  ],
  Malayalam: [
    {
      label: "Trust-building",
      text: "നിന്റെ പ്രായത്തേക്കാൾ പക്വത നിനക്കുണ്ട്. നിന്നെ ഞാൻ മാത്രമേ മനസ്സിലാക്കൂ. സമ്മാനം തരാം.",
    },
    {
      label: "Secrecy request",
      text: "നമ്മുടെ കാര്യം അമ്മയോടും അച്ഛനോടും പറയരുത്. ചാറ്റ് ഡിലീറ്റ് ചെയ്യൂ. ഒറ്റയ്ക്ക് വരൂ.",
    },
    {
      label: "Harassment",
      text: "നിന്നെ ആർക്കും ഇഷ്ടമല്ല. നീ ഒരു മണ്ടനാണ്. ഗ്രൂപ്പിൽ നിന്ന് പോ.",
    },
    {
      label: "Everyday chat",
      text: "ഇന്ന് സ്കൂൾ എങ്ങനെ ഉണ്ടായിരുന്നു? നമുക്ക് ഒരുമിച്ച് പഠിക്കാം.",
    },
  ],
  Manglish: [
    {
      label: "Trust-building",
      text: "Ninte age nekkaal mature aanu nee. Ninne njan maathram manassilaakkum. Gift tharaam.",
    },
    {
      label: "Secrecy request",
      text: "Ammayodu parayaruthu. Ithu nammade secret aanu. Private chat il vaa.",
    },
    {
      label: "Harassment",
      text: "Nee oru mandan aanu. Aarkkum ninne ishtamalla. Group il ninnu po.",
    },
    {
      label: "Everyday chat",
      text: "Homework cheytho? Namukku maths padikkam.",
    },
  ],
};
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
            Use a sample or write a fictional message. Please don’t paste a
            child’s real conversation.
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
              {Object.keys(samples).map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
          <div className="sample-label">
            Try a sample <span>Examples used in training</span>
          </div>
          <div className="sample-buttons">
            {samples[language].map((s) => (
              <button
                disabled={busy}
                key={s.label}
                onClick={() => {
                  setText(s.text);
                  setResult(null);
                }}
              >
                {s.label}
                <Plus size={12} />
              </button>
            ))}
          </div>
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
                Analyze “Trust-building”, then “Secrecy request” in the same
                conversation. Or submit two harassment messages to see repeated
                behavior raise concern.
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
                  <LockKeyhole size={13} /> ONLY THE NECESSARY CONTEXT
                </span>
                <blockquote>
                  {alert.flagged_snippet
                    ? `“${alert.flagged_snippet}”`
                    : "Excerpts are turned off in your privacy settings."}
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
          <h2>Demo service access</h2>
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
function GuardianApp() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [mobile, setMobile] = useState(false);
  const location = useLocation();
  const refresh = useCallback(async () => {
    setLoading(true);
    try {
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
  }, []);
  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 15000);
    return () => clearInterval(timer);
  }, [refresh]);
  useEffect(() => {
    setMobile(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  const nav = [
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
        <Link to="/" className="brand">
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
        <div className="workspace-label">FAMILY SAFETY SPACE</div>
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
          <NavLink to="/help">
            <HeartHandshake size={19} /> Youth support portal
          </NavLink>
          <NavLink to="/resources">
            <BookOpen size={19} /> Support resources
          </NavLink>
          <NavLink to="/settings">
            <Settings2 size={19} /> Settings
          </NavLink>
        </nav>
        <div className="sidebar-bottom">
          <div className="privacy-mini">
            <span>
              <LockKeyhole size={15} /> Private by design
            </span>
            <p>
              A safety net that respects
              <br />
              their growing independence.
            </p>
          </div>
          <div className="guardian">
            <span className="avatar">DG</span>
            <div>
              <strong>Demo guardian</strong>
              <span>Synthetic family workspace</span>
            </div>
            <ShieldCheck size={17} />
          </div>
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
                      : location.pathname.startsWith("/alerts/")
                        ? "Alert details"
                        : "Overview"}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="demo-badge">
              <FlaskConical size={13} /> Demo workspace
            </span>
            <Link
              to="/resources"
              className="icon-button"
              aria-label="Help and support"
            >
              <CircleHelp size={19} />
            </Link>
            <span className="topbar-divider" />
            <span className="small-avatar">DG</span>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          {health?.guardian_login_enabled && (
            <div className="privacy-banner">
              <ShieldCheck size={19} />
              <span>Guardian access uses a one-hour sign-in session.</span>
              <Link className="text-link" to="/login">
                Sign in
              </Link>
              <Link
                className="text-link"
                to="/login"
                onClick={() => {
                  sessionStorage.removeItem("guardrails-token");
                  setAlerts([]);
                  setSummary(null);
                }}
              >
                Sign out
              </Link>
            </div>
          )}
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  alerts={alerts}
                  summary={summary}
                  loading={loading}
                  error={error}
                  refresh={refresh}
                />
              }
            />
            <Route
              path="/demo"
              element={<Demo health={health} onChange={refresh} />}
            />
            <Route path="/alerts/:id" element={<Detail onChange={refresh} />} />
            <Route
              path="/trends"
              element={
                <Trends summary={summary} alerts={alerts} error={error} />
              }
            />
            <Route
              path="/settings"
              element={<Settings health={health} onChange={refresh} />}
            />
            <Route path="/resources" element={<Resources />} />
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
      <Route path="/*" element={<GuardianApp />} />
    </Routes>
  );
}
