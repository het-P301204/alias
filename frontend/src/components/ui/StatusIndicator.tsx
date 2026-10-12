import { Check, Loader2, AlertCircle, Clock, XCircle } from 'lucide-react'
import type { ExperimentStatus } from '../../services/api'
import { cn } from '../../utils/cn'

const steps: ExperimentStatus[] = ['ready', 'validating', 'running', 'analyzing', 'completed']

interface StatusIndicatorProps {
  status: ExperimentStatus
  error?: string | null
}

function StepIcon({ step, status }: { step: ExperimentStatus; status: ExperimentStatus }) {
  const stepIndex = steps.indexOf(step)
  const currentIndex = steps.indexOf(status)
  const isTerminal = ['completed', 'failed', 'timeout', 'cancelled'].includes(status)

  if (status === 'failed' || status === 'timeout') {
    if (stepIndex === currentIndex || (!isTerminal && stepIndex < currentIndex)) {
      return <AlertCircle size={14} className="text-red-light" />
    }
  }

  if (stepIndex < currentIndex || (isTerminal && step === 'completed' && status === 'completed')) {
    return <Check size={14} className="text-sage" />
  }
  if (stepIndex === currentIndex && !isTerminal) {
    return <Loader2 size={14} className="text-copper animate-spin" />
  }
  return <Clock size={14} className="text-ivory-dim opacity-40" />
}

const stepLabels: Record<string, string> = {
  ready: 'Ready',
  validating: 'Validating',
  running: 'Running',
  analyzing: 'Analyzing',
  completed: 'Completed',
}

export function StatusIndicator({ status, error }: StatusIndicatorProps) {
  const isFailed = status === 'failed' || status === 'timeout' || status === 'cancelled'

  return (
    <div className="space-y-1">
      {steps.map((step, i) => {
        const stepIndex = steps.indexOf(step)
        const currentIndex = steps.indexOf(status)
        const isPast = stepIndex < currentIndex
        const isCurrent = stepIndex === currentIndex && !['failed', 'timeout', 'cancelled'].includes(status)
        const isCompleted = status === 'completed'

        return (
          <div key={step} className="flex items-center gap-3">
            <div
              className={cn(
                'w-6 h-6 rounded-full flex items-center justify-center border',
                isPast || (step === 'completed' && isCompleted)
                  ? 'bg-sage/20 border-sage/30'
                  : isCurrent
                    ? 'bg-copper/20 border-copper/50'
                    : 'bg-surface border-border'
              )}
            >
              <StepIcon step={step} status={status} />
            </div>
            <span
              className={cn(
                'text-xs font-mono',
                isCurrent ? 'text-copper-light' : isPast || (step === 'completed' && isCompleted) ? 'text-sage' : 'text-ivory-dim opacity-50'
              )}
            >
              {stepLabels[step]}
            </span>
          </div>
        )
      })}

      {isFailed && (
        <div className="flex items-center gap-3 mt-1">
          <div className="w-6 h-6 rounded-full flex items-center justify-center border bg-red/20 border-red/30">
            <XCircle size={14} className="text-red-light" />
          </div>
          <span className="text-xs font-mono text-red-light capitalize">{status}</span>
        </div>
      )}

      {error && (
        <div className="mt-2 p-2 bg-red/10 border border-red/20 rounded text-xs text-red-light font-mono">
          {error}
        </div>
      )}
    </div>
  )
}
