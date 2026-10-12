import { useState } from 'react'
import { useStartExperiment, useExperiment, useCancelExperiment } from './useApi'
import type { LabMode } from '../services/api'

export function useExperimentRunner() {
  const [activeId, setActiveId] = useState<string | null>(null)
  const startMutation = useStartExperiment()
  const cancelMutation = useCancelExperiment()
  const experimentQuery = useExperiment(activeId)

  const start = async (scenarioId: string, mode: LabMode, parameters?: Record<string, unknown>) => {
    const result = await startMutation.mutateAsync({ scenario_id: scenarioId, mode, parameters })
    setActiveId(result.id)
    return result
  }

  const cancel = async () => {
    if (activeId) {
      await cancelMutation.mutateAsync(activeId)
    }
  }

  const reset = () => {
    setActiveId(null)
  }

  return {
    activeId,
    experiment: experimentQuery.data,
    isLoading: startMutation.isPending,
    isPolling: experimentQuery.isFetching,
    error: startMutation.error || experimentQuery.error,
    start,
    cancel,
    reset,
  }
}
