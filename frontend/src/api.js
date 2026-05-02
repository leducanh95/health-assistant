function getToken() {
  return localStorage.getItem("bha.token");
}

function clearAuth() {
  localStorage.removeItem("bha.token");
  localStorage.removeItem("bha.activeBabyId");
}

async function request(method, url, body) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const opts = { method, headers };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);

  if (res.status === 401) {
    clearAuth();
    window.dispatchEvent(new Event("bha:auth-expired"));
    throw new Error("401 Unauthorized");
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${text ? ` — ${text}` : ""}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Auth
  signup: (email, password) =>
    request("POST", "/api/auth/signup", { email, password }),
  login: (email, password) =>
    request("POST", "/api/auth/login", { email, password }),
  me: () => request("GET", "/api/auth/me"),

  // Babies
  listBabies: () => request("GET", "/api/babies"),
  createBaby: (data) => request("POST", "/api/babies", data),
  updateBaby: (id, data) => request("PATCH", `/api/babies/${id}`, data),

  // Measurements
  listMeasurements: (babyId) =>
    request("GET", `/api/babies/${babyId}/measurements`),
  addMeasurement: (babyId, data) =>
    request("POST", `/api/babies/${babyId}/measurements`, data),
  deleteMeasurement: (babyId, id) =>
    request("DELETE", `/api/babies/${babyId}/measurements/${id}`),
  growthStatus: (babyId) =>
    request("GET", `/api/babies/${babyId}/growth-status`),

  // Milestones
  listMilestoneRecords: (babyId) =>
    request("GET", `/api/babies/${babyId}/milestones`),
  upsertMilestone: (babyId, data) =>
    request("POST", `/api/babies/${babyId}/milestones`, data),
  deleteMilestone: (babyId, id) =>
    request("DELETE", `/api/babies/${babyId}/milestones/${id}`),
  milestoneStatus: (babyId) =>
    request("GET", `/api/babies/${babyId}/milestone-status`),

  // Vaccinations
  listVaccinations: (babyId) =>
    request("GET", `/api/babies/${babyId}/vaccinations`),
  addVaccination: (babyId, data) =>
    request("POST", `/api/babies/${babyId}/vaccinations`, data),
  deleteVaccination: (babyId, id) =>
    request("DELETE", `/api/babies/${babyId}/vaccinations/${id}`),
  vaccinationStatus: (babyId) =>
    request("GET", `/api/babies/${babyId}/vaccinations/status`),

  // Reference (WHO)
  refMilestones: () => request("GET", "/api/reference/milestones"),
  refVaccines: () => request("GET", "/api/reference/vaccines"),
  refFeeding: () => request("GET", "/api/reference/feeding"),
  refFeedingNutrition: () => request("GET", "/api/reference/feeding/nutrition"),
  refGrowthCurves: (sex, indicator) =>
    request(
      "GET",
      `/api/reference/growth-curves?sex=${encodeURIComponent(
        sex,
      )}&indicator=${encodeURIComponent(indicator)}`,
    ),
  refGrowthTable: (sex) =>
    request("GET", `/api/reference/growth-table?sex=${encodeURIComponent(sex)}`),

  // Chat
  chat: (message, sessionId, babyId, language) =>
    request("POST", "/chat", {
      message,
      session_id: sessionId,
      baby_id: babyId,
      language,
    }),
};
