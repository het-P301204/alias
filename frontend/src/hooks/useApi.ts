import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, ScenarioMetadata, Experiment, DefenseControl, ExperimentListParams } from '../services/api'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.health().then((r) => r.data),
    refetchInterval: 30_000,
  })
}

export function useScenarios() {
  return useQuery({
    queryKey: ['scenarios'],
    queryFn: () => api.scenarios.list().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useScenario(id: string) {
  return useQuery({
    queryKey: ['scenarios', id],
    queryFn: () => api.scenarios.get(id).then((r) => r.data),
    enabled: !!id,
  })
}

export function useExperiments(params?: ExperimentListParams) {
  return useQuery({
    queryKey: ['experiments', params],
    queryFn: () => api.experiments.list(params).then((r) => r.data),
  })
}

export function useExperiment(id: string | null) {
  return useQuery({
    queryKey: ['experiments', id],
    queryFn: () => api.experiments.get(id!).then((r) => r.data),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data as Experiment | undefined
      if (!data) return false
      const active = ['ready', 'validating', 'running', 'analyzing'].includes(data.status)
      return active ? 2000 : false
    },
  })
}

export function useStartExperiment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (config: {
      scenario_id: string
      mode: 'vulnerable' | 'hardened'
      parameters?: Record<string, unknown>
    }) => api.experiments.start(config).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['experiments'] })
    },
  })
}

export function useCancelExperiment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.experiments.cancel(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['experiments'] })
    },
  })
}

export function useDefenses() {
  return useQuery({
    queryKey: ['defenses'],
    queryFn: () => api.defenses.list().then((r) => r.data),
  })
}

export function useVerifyDefense() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.defenses.verify(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['defenses'] })
    },
  })
}
