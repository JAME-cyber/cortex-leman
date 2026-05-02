/**
 * Cortex Leman v5 — API Client
 */
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('cl_access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    localStorage.removeItem('cl_access_token');
    // Don't hard-redirect — let React state handle routing
    throw new Error('Session expirée');
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur ${res.status}`);
  }
  return res.json();
}

// Auth
export const auth = {
  login: (email: string, password: string) =>
    apiFetch<any>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: () => apiFetch<any>('/api/v1/auth/me'),
};

// Intentions
export const intentions = {
  create: (data: any) =>
    apiFetch('/api/v1/intentions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  list: (clientId: string) =>
    apiFetch(`/api/v1/intentions?client_id=${clientId}`),
  get: (id: string) => apiFetch(`/api/v1/intentions/${id}`),
};

// Chat
export const chat = {
  send: (message: string, vertical: string, agent: string) =>
    apiFetch('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify({ message, vertical, agent_name: agent }),
    }),
};

// Journal
export const journal = {
  query: (params: string) => apiFetch(`/api/v1/journal?${params}`),
  verify: () => apiFetch('/api/v1/journal/verify'),
};

// RAG
export const rag = {
  search: (query: string, vertical?: string) =>
    apiFetch(`/api/v1/rag/search?query=${encodeURIComponent(query)}${vertical ? `&vertical=${vertical}` : ''}`),
  stats: () => apiFetch('/api/v1/rag/stats'),
};

// Admin
export const admin = {
  users: () => apiFetch('/api/v1/admin/users'),
  audit: (params?: string) => apiFetch(`/api/v1/admin/audit${params ? `?${params}` : ''}`),
  apiKeys: () => apiFetch('/api/v1/auth/api-keys'),
  createApiKey: (data: any) =>
    apiFetch('/api/v1/auth/api-keys', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  revokeApiKey: (id: string) =>
    apiFetch(`/api/v1/auth/api-keys/${id}`, { method: 'DELETE' }),
};
