import axios from 'axios'

export const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30_000,
  headers: { 'Content-Type': 'application/json' },
})

// Unwrap backend envelope: { data: ..., error: null, meta: {} } → data
axiosInstance.interceptors.response.use((r) => {
  if (r.data && typeof r.data === 'object' && 'data' in r.data && 'error' in r.data) {
    const inner = r.data.data
    // Experiments list returns { items, total, page, limit } — flatten to items array
    r.data = Array.isArray(inner) ? inner : (inner?.items ?? inner)
  }
  return r
})

export type ExperimentStatus =
  | 'ready'
  | 'validating'
  | 'running'
  | 'analyzing'
  | 'completed'
  | 'failed'
  | 'timeout'
  | 'cancelled'

export type LabMode = 'vulnerable' | 'hardened'

export interface Evidence {
  type: string
  label: string
  data: unknown
  timestamp: string
}

export interface DefenseResult {
  control_id: string
  verified: boolean
  description: string
  details: Record<string, unknown>
}

export interface Experiment {
  id: string
  scenario_id: string
  mode: LabMode
  config: Record<string, unknown>
  status: ExperimentStatus
  started_at: string
  completed_at: string | null
  duration_ms: number | null
  input_summary: string
  expected_outcome: string
  actual_outcome: string | null
  evidence: Evidence[]
  defensive_control_result: DefenseResult | null
  error: string | null
  is_sample: boolean
}

export interface ScenarioMetadata {
  id: string
  title: string
  description: string
  category: string
  difficulty: string
  learning_objectives: string[]
  default_config: Record<string, unknown>
}

export interface DefenseControl {
  control_id: string
  title: string
  description: string
  scenario_id: string
  vulnerable_behavior: string
  hardened_behavior: string
  config: Record<string, unknown>
  last_verified: string | null
  last_result: boolean | null
}

export interface ExperimentListParams {
  scenario_id?: string
  mode?: LabMode
  status?: ExperimentStatus
  limit?: number
  offset?: number
}

export const api = {
  health: () => axiosInstance.get<{ status: string; version: string }>('/api/health'),

  scenarios: {
    list: () => axiosInstance.get<ScenarioMetadata[]>('/api/scenarios'),
    get: (id: string) => axiosInstance.get<ScenarioMetadata>(`/api/scenarios/${id}`),
  },

  experiments: {
    list: (params?: ExperimentListParams) =>
      axiosInstance.get<Experiment[]>('/api/experiments', { params }),
    get: (id: string) => axiosInstance.get<Experiment>(`/api/experiments/${id}`),
    start: (config: { scenario_id: string; mode: LabMode; parameters?: Record<string, unknown> }) =>
      axiosInstance.post<Experiment>('/api/experiments', config),
    cancel: (id: string) => axiosInstance.post(`/api/experiments/${id}/cancel`),
  },

  defenses: {
    list: () => axiosInstance.get<DefenseControl[]>('/api/defenses'),
    get: (id: string) => axiosInstance.get<DefenseControl>(`/api/defenses/${id}`),
    verify: (id: string) => axiosInstance.post<DefenseResult>(`/api/defenses/${id}/verify`),
  },

  reports: {
    get: (id: string, format: 'json' | 'csv' | 'html' = 'json') =>
      axiosInstance.get(`/api/reports/${id}`, { params: { format }, responseType: 'blob' }),
  },
}
