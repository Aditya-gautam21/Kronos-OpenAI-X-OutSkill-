const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchBotStatus() {
  const res = await fetch(`${API_BASE}/bot-status`);
  return res.json();
}

export async function fetchPositions() {
  const res = await fetch(`${API_BASE}/positions`);
  return res.json();
}

export async function fetchTradeHistory() {
  const res = await fetch(`${API_BASE}/trade-history`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  return res.json();
}

export async function fetchPipeline() {
  const res = await fetch(`${API_BASE}/pipeline`);
  return res.json();
}

export async function fetchAllocation() {
  const res = await fetch(`${API_BASE}/allocation`);
  return res.json();
}

export async function fetchLogs() {
  const res = await fetch(`${API_BASE}/logs`);
  return res.json();
}

export async function startBot() {
  const res = await fetch(`${API_BASE}/start-autonomous-bot`, {
    method: "POST",
  });
  return res.json();
}
