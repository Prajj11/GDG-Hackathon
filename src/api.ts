import axios from "axios";
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 60000,
});
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("guardrails-token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && error.config?.url !== "/auth/login") {
      const health = await axios
        .get(`${api.defaults.baseURL}/health`)
        .catch(() => null);
      if (health?.data.guardian_login_enabled) {
        sessionStorage.removeItem("guardrails-token");
        window.location.replace(`${import.meta.env.BASE_URL}login`);
      }
    }
    return Promise.reject(error);
  },
);
export const errorText = (error: unknown) =>
  axios.isAxiosError(error)
    ? typeof error.response?.data?.detail === "string"
      ? error.response.data.detail
      : error.response?.status === 422
        ? "Please check the message and conversation details."
        : "Could not reach the safety service. Check the backend and try again."
    : "Something went wrong. Please try again.";
export type Risk = "High" | "Medium" | "Low";
export interface Alert {
  id: string;
  conversation_id: string;
  risk_score: number;
  risk_level: Risk;
  pattern_type: string;
  flagged_snippet: string;
  explanation: string;
  model: string;
  confidence: number;
  reviewed: boolean;
  created_at: string;
  child_label: string;
  source_platform: string;
  language: string;
}
export interface Summary {
  total_alerts: number;
  unreviewed: number;
  high_risk: number;
  reviewed: number;
  messages_analyzed: number;
  conversations: number;
  trends: { date: string; High: number; Medium: number; Low: number }[];
}
export interface Health {
  status: string;
  model: string;
  model_kind: string;
  fallback_reason: string | null;
  access_protected: boolean;
  guardian_login_enabled: boolean;
}
export interface Analysis {
  risk_score: number;
  risk_level: Risk;
  pattern_type: string;
  explanation: string;
  model: string;
  alert_id: string | null;
  support_context_token: string | null;
  message_count: number;
  escalated: boolean;
  confidence: number;
}
export const patternNames: Record<string, string> = {
  "grooming-trust-building": "Unusual trust-building",
  "grooming-isolation-request": "Secrecy & isolation",
  "grooming-coercive-language": "Pressure & coercion",
  "bullying-harassment": "Bullying & harassment",
  neutral: "No clear risk pattern",
};

export interface NgoReport {
  id: string;
  locality: string;
  selected_context: string;
  report_text: string;
  urgency_level: "High" | "Medium" | "Low";
  status: string;
  assigned_worker?: string | null;
  caseworker_notes?: string | null;
  detection_context?: { pattern_type?: string; risk_level?: string } | null;
  created_at: string;
}
