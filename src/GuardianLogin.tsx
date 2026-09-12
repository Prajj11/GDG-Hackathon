import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, ArrowRight, HeartHandshake, Building2, User, MapPin, UserPlus, LogIn, CheckCircle2 } from "lucide-react";
import { api, errorText } from "./api";

export default function GuardianLogin() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [role, setRole] = useState<"guardian" | "ngo">("guardian");

  // Sign in fields
  const [username, setUsername] = useState("guardian");
  const [password, setPassword] = useState("demo123");
  const [locality, setLocality] = useState("South Delhi");

  // Sign up fields
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [orgName, setOrgName] = useState("");
  const [stationedLocation, setStationedLocation] = useState("South Delhi");
  const [customLocation, setCustomLocation] = useState("");
  const [childDeviceName, setChildDeviceName] = useState("");

  const [error, setError] = useState("");
  const [successNotice, setSuccessNotice] = useState("");
  const [busy, setBusy] = useState(false);

  const effectiveLocation =
    stationedLocation === "Other" ? (customLocation.trim() || "Local District") : stationedLocation;

  function switchRole(newRole: "guardian" | "ngo") {
    setRole(newRole);
    setError("");
    setSuccessNotice("");
    if (mode === "signin") {
      if (newRole === "guardian") {
        setUsername("guardian");
        setPassword("demo123");
      } else {
        setUsername("cwc_southdelhi");
        setPassword("demo123");
        setLocality("South Delhi");
      }
    } else {
      setUsername("");
      setPassword("");
    }
  }

  function switchMode(newMode: "signin" | "signup") {
    setMode(newMode);
    setError("");
    setSuccessNotice("");
    if (newMode === "signin") {
      if (role === "guardian") {
        setUsername("guardian");
        setPassword("demo123");
      } else {
        setUsername("cwc_southdelhi");
        setPassword("demo123");
      }
    } else {
      setUsername("");
      setPassword("");
      setFullName("");
      setEmail("");
      setOrgName(role === "ngo" ? "District Child Welfare Committee" : "");
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setSuccessNotice("");

    try {
      if (mode === "signup") {
        // Register API call
        const payload = {
          role,
          username: username.trim().toLowerCase(),
          password,
          email: email.trim() || undefined,
          full_name: fullName.trim() || (role === "guardian" ? "Parent" : "Casework Officer"),
          organization_name: role === "ngo" ? (orgName.trim() || "Child Welfare Unit") : undefined,
          stationed_location: role === "ngo" ? effectiveLocation : undefined,
          child_name: role === "guardian" ? (childDeviceName.trim() || "Protected Device") : undefined,
        };

        const { data } = await api.post("/auth/register", payload);

        sessionStorage.setItem("guardrails-token", data.access_token);
        sessionStorage.setItem("guardrails-role", data.role || role);
        sessionStorage.setItem("guardrails-locality", data.locality || effectiveLocation);
        sessionStorage.setItem("guardrails-user", data.full_name || data.username);
        sessionStorage.setItem("guardrails-username", data.username);

        setSuccessNotice("Account successfully created! Redirecting to your workspace...");
        setTimeout(() => {
          if (role === "ngo") {
            navigate("/physical-link", { replace: true });
          } else {
            navigate("/", { replace: true });
          }
        }, 600);
      } else {
        // Login API call
        const { data } = await api.post("/auth/login", {
          username: username.trim().toLowerCase(),
          password,
          role,
          locality: role === "ngo" ? locality : undefined,
        });

        sessionStorage.setItem("guardrails-token", data.access_token);
        sessionStorage.setItem("guardrails-role", data.role || role);
        sessionStorage.setItem("guardrails-locality", data.locality || locality);
        sessionStorage.setItem("guardrails-user", data.full_name || data.username);
        sessionStorage.setItem("guardrails-username", data.username);

        setPassword("");
        if (data.role === "ngo" || role === "ngo") {
          navigate("/physical-link", { replace: true });
        } else {
          navigate("/", { replace: true });
        }
      }
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 sm:p-6 bg-slate-50">
      <main className="panel w-full max-w-lg !p-7 sm:!p-9 shadow-md rounded-2xl bg-white border border-slate-200/80">
        {/* Header Branding */}
        <div className="flex items-center gap-3 mb-5">
          <span className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-700 flex items-center justify-center shrink-0">
            {role === "guardian" ? <ShieldCheck size={28} /> : <Building2 size={28} />}
          </span>
          <div>
            <span className="text-[11px] font-bold tracking-wider uppercase text-blue-700 block">
              Digital Guardrails
            </span>
            <span className="text-xs text-slate-500 font-medium">
              Unified Access & Safeguarding Gateway
            </span>
          </div>
        </div>

        {/* Mission Statement Pill */}
        <div className="p-3 mb-5 rounded-xl bg-blue-50/70 border border-blue-100 text-xs text-blue-900 leading-relaxed">
          <strong className="block text-blue-800 mb-0.5">Physical-Digital Link:</strong>
          Bridge the gap between digital alerts and ground-level intervention for child welfare organizations and local authorities.
        </div>

        {/* Mode Switch: Sign In vs Sign Up */}
        <div className="flex border-b border-slate-200 mb-5">
          <button
            type="button"
            onClick={() => switchMode("signin")}
            className={`flex items-center justify-center gap-1.5 pb-2.5 px-4 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              mode === "signin"
                ? "border-blue-600 text-blue-700"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <LogIn size={14} /> Sign In
          </button>
          <button
            type="button"
            onClick={() => switchMode("signup")}
            className={`flex items-center justify-center gap-1.5 pb-2.5 px-4 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              mode === "signup"
                ? "border-blue-600 text-blue-700"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            <UserPlus size={14} /> Create Account (Sign Up)
          </button>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-slate-100 mb-5">
          <button
            type="button"
            onClick={() => switchRole("guardian")}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              role === "guardian"
                ? "bg-white text-ink shadow-xs"
                : "text-slate-500 hover:text-ink"
            }`}
          >
            <User size={14} /> Parent / Guardian
          </button>
          <button
            type="button"
            onClick={() => switchRole("ngo")}
            className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              role === "ngo"
                ? "bg-white text-ink shadow-xs"
                : "text-slate-500 hover:text-ink"
            }`}
          >
            <Building2 size={14} /> Child Welfare / NGO
          </button>
        </div>

        {/* Dynamic Title and Context */}
        <h1 className="!text-xl font-bold mb-1 text-ink">
          {mode === "signin"
            ? role === "guardian"
              ? "Parent & Guardian Sign In"
              : "Child Welfare & NGO Sign In"
            : role === "guardian"
              ? "Create Parent Account"
              : "Register Child Welfare / NGO Unit"}
        </h1>
        <p className="subtle mb-4 text-xs leading-relaxed text-slate-500">
          {role === "guardian"
            ? "Access your private family safety space, monitor device signals, and test detectors in the Demo Panel."
            : mode === "signin"
              ? "Access your locality casework inbox to triage anonymous youth reports and dispatch field officers."
              : "Register your accredited NGO or CWC station to receive ground-level incident reports from youth in your area."}
        </p>

        {/* Form */}
        <form onSubmit={submit} className="space-y-3.5">
          {mode === "signup" && (
            <>
              <label className="text-xs font-medium text-slate-700">
                {role === "guardian" ? "Full Name" : "Officer / Caseworker Full Name"}
                <input
                  type="text"
                  placeholder={role === "guardian" ? "e.g. Priya Sharma" : "e.g. Ms. S. Sharma (CPO)"}
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  maxLength={100}
                  className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
                />
              </label>

              {role === "ngo" && (
                <>
                  <label className="text-xs font-medium text-slate-700">
                    Organization / Committee Name
                    <input
                      type="text"
                      placeholder="e.g. South Delhi Child Welfare Committee (CWC)"
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      required
                      maxLength={120}
                      className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
                    />
                  </label>

                  <div className="bg-blue-50/50 p-3 rounded-xl border border-blue-100/80">
                    <label className="text-xs font-semibold text-blue-900 flex items-center gap-1.5 mb-1">
                      <MapPin size={13} className="text-blue-700" />
                      Where is this NGO / CWC unit stationed? (Locality)
                    </label>
                    <select
                      value={stationedLocation}
                      onChange={(e) => setStationedLocation(e.target.value)}
                      className="!py-2 !px-3 !text-xs !bg-white border border-slate-200 rounded-lg w-full font-medium"
                    >
                      <option value="South Delhi">South Delhi (Saket, Hauz Khas, Greater Kailash)</option>
                      <option value="North Delhi">North Delhi (Civil Lines, Rohini, Model Town)</option>
                      <option value="Mumbai Suburban">Mumbai Suburban (Bandra, Andheri, Borivali)</option>
                      <option value="Bengaluru Urban">Bengaluru Urban (Koramangala, Indiranagar, Whitefield)</option>
                      <option value="Kolkata Central">Kolkata Central (Park Street, Salt Lake)</option>
                      <option value="East Delhi">East Delhi (Preet Vihar, Mayur Vihar)</option>
                      <option value="Other">Other / Custom District</option>
                    </select>

                    {stationedLocation === "Other" && (
                      <input
                        type="text"
                        placeholder="Enter your specific district or city"
                        value={customLocation}
                        onChange={(e) => setCustomLocation(e.target.value)}
                        required
                        className="mt-2 !py-2 !px-3 !text-xs !bg-white border border-slate-200 rounded-lg w-full"
                      />
                    )}

                    <span className="text-[11px] text-blue-700 mt-1 block">
                      ⚡ When a young person in this locality submits an anonymous report, it will be delivered directly to your casework box.
                    </span>
                  </div>
                </>
              )}

              {role === "guardian" && (
                <label className="text-xs font-medium text-slate-700">
                  Child's Device / Profile Label
                  <input
                    type="text"
                    placeholder="e.g. Aarav's Phone or Family Tablet"
                    value={childDeviceName}
                    onChange={(e) => setChildDeviceName(e.target.value)}
                    maxLength={80}
                    className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
                  />
                </label>
              )}

              <label className="text-xs font-medium text-slate-700">
                Email Address (Optional)
                <input
                  type="email"
                  placeholder="contact@example.org"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  maxLength={120}
                  className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
                />
              </label>
            </>
          )}

          {mode === "signin" && role === "ngo" && (
            <label className="text-xs font-medium text-slate-700">
              Stationed Jurisdiction / Locality
              <select
                value={locality}
                onChange={(e) => {
                  setLocality(e.target.value);
                  if (e.target.value === "South Delhi") {
                    setUsername("cwc_southdelhi");
                  } else if (e.target.value === "Mumbai Suburban") {
                    setUsername("mumbai_cwc");
                  } else if (e.target.value === "Bengaluru Urban") {
                    setUsername("bengaluru_cwc");
                  }
                }}
                className="mt-1 !py-2 !px-3 !text-xs !bg-white border border-slate-200 rounded-lg w-full font-medium"
              >
                <option value="South Delhi">South Delhi (CWC-I & DCPU)</option>
                <option value="Mumbai Suburban">Mumbai Suburban (CWC & DCPU)</option>
                <option value="Bengaluru Urban">Bengaluru Urban (CWC & DCPU)</option>
                <option value="North Delhi">North Delhi (CWC-II & DCPU)</option>
                <option value="Kolkata Central">Kolkata Central (CWC & DCPU)</option>
                <option value="All Localities">All Localities (Central Statutory Desk)</option>
              </select>
            </label>
          )}

          <label className="text-xs font-medium text-slate-700">
            Username
            <input
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              maxLength={80}
              placeholder={role === "guardian" ? "guardian or your username" : "e.g. cwc_southdelhi"}
              className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
            />
          </label>

          <label className="text-xs font-medium text-slate-700">
            Password
            <input
              autoComplete={mode === "signin" ? "current-password" : "new-password"}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={4}
              maxLength={256}
              placeholder="••••••••"
              className="mt-1 !py-2 !px-3 !text-xs border border-slate-200 rounded-lg w-full"
            />
          </label>

          {/* Demo quick fill helper */}
          {mode === "signin" && (
            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-0.5">
              <span>Demo credentials ready:</span>
              <button
                type="button"
                onClick={() => {
                  if (role === "guardian") {
                    setUsername("guardian");
                    setPassword("demo123");
                  } else {
                    setUsername("cwc_southdelhi");
                    setPassword("demo123");
                    setLocality("South Delhi");
                  }
                }}
                className="text-blue-600 hover:underline font-semibold cursor-pointer"
              >
                Autofill demo {role === "guardian" ? "parent" : "NGO"}
              </button>
            </div>
          )}

          {error && (
            <p role="alert" className="error-box text-xs">
              {error}
            </p>
          )}

          {successNotice && (
            <p role="status" className="p-3 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs font-semibold flex items-center gap-1.5">
              <CheckCircle2 size={15} className="text-emerald-600" />
              {successNotice}
            </p>
          )}

          <button
            type="submit"
            className="primary magnetic w-full justify-center !py-2.5 text-xs font-semibold mt-2 cursor-pointer"
            disabled={busy}
          >
            {busy ? (
              "Processing..."
            ) : mode === "signup" ? (
              role === "guardian" ? (
                <>Create Parent Account & Open Dashboard <ArrowRight size={15} /></>
              ) : (
                <>Register NGO Unit & Open Casework Box <ArrowRight size={15} /></>
              )
            ) : role === "guardian" ? (
              <>Sign In to Parent Workspace & Demo Panel <ArrowRight size={15} /></>
            ) : (
              <>Sign In to NGO Casework Box <ArrowRight size={15} /></>
            )}
          </button>
        </form>

        {/* Youth Support Portal Box */}
        <div className="login-youth-box mt-6 p-4 rounded-xl border border-slate-200 bg-slate-50/90 text-left">
          <div className="flex items-center gap-2 font-semibold text-ink text-sm">
            <HeartHandshake size={18} className="text-teal-600 shrink-0" />
            <span>Youth Support Portal</span>
          </div>
          <p className="text-xs text-slate-500 mt-1 mb-3 leading-relaxed">
            Are you a student or young person looking for confidential support? No guardian or caseworker login required.
          </p>
          <Link
            to="/help"
            className="flex items-center justify-center gap-2 w-full py-2.5 px-3 rounded-lg text-xs font-semibold bg-white border border-slate-200 hover:bg-slate-100 hover:border-slate-300 text-ink transition-colors shadow-xs"
          >
            Open Confidential Youth Support Portal <ArrowRight size={14} />
          </Link>
        </div>
      </main>
    </div>
  );
}
