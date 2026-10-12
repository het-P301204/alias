import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Play, ChevronDown, ChevronUp } from 'lucide-react'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import type { LabMode, ExperimentStatus } from '../../services/api'

type CandidateStatus = 'pending' | 'confirmed' | 'rejected' | 'unknown'

const CANDIDATES = [
  'id', 'name', 'email', 'password', 'ssn', 'role', 'orders', 'createdAt',
  'updatedAt', 'phone', 'address', 'creditCard', 'token', 'refreshToken',
  'internalNotes', 'adminFlag', 'permissions', 'lastLogin', 'ipAddress', 'userAgent',
  'profilePicture', 'bio', 'website', 'twoFactorSecret', 'backupCodes',
  'paymentMethod', 'billingAddress', 'subscriptionPlan', 'trialEndsAt', 'cancelledAt',
  'apiKey', 'webhookUrl', 'slackToken', 'githubToken', 'stripeCustomerId',
  'taxId', 'vatNumber', 'companyName', 'department', 'employeeId',
  'salary', 'bonus', 'performanceScore', 'terminationDate', 'hrNotes',
  'accessLog', 'auditTrail', 'flaggedForReview', 'riskScore', 'fraudScore',
]

function getCandidateStatus(index: number, totalProcessed: number, isHardened: boolean): CandidateStatus {
  if (isHardened) return 'unknown'
  if (index >= totalProcessed) return 'pending'
  if (index % 7 === 0) return 'rejected'
  if (index % 3 === 0) return 'confirmed'
  return 'unknown'
}

const statusColors: Record<CandidateStatus, string> = {
  pending: 'text-ivory-dim',
  confirmed: 'text-sage',
  rejected: 'text-red-light',
  unknown: 'text-amber',
}

const statusBadge: Record<CandidateStatus, 'completed' | 'failed' | 'ready' | 'analyzing'> = {
  pending: 'ready',
  confirmed: 'completed',
  rejected: 'failed',
  unknown: 'analyzing',
}

export default function BlindRecoveryPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [openEvidence, setOpenEvidence] = useState<number | null>(null)
  const { experiment, isLoading, start } = useExperimentRunner()

  const handleRun = () => start('blind-recovery', mode)

  const isRunning = experiment && ['validating', 'running', 'analyzing'].includes(experiment.status)
  const isCompleted = experiment?.status === 'completed'

  const processed = isCompleted ? CANDIDATES.length : isRunning ? Math.floor(CANDIDATES.length * 0.6) : 0

  const confirmed = useMemo(() => {
    if (mode === 'hardened') return 0
    return CANDIDATES.filter((_, i) => getCandidateStatus(i, processed, false) === 'confirmed').length
  }, [processed, mode])

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div className="flex items-center gap-4">
        <h1 className="font-display text-2xl text-ivory">Blind Schema Recovery</h1>
        <ModeToggle mode={mode} onChange={setMode} />
        <Button onClick={handleRun} loading={isLoading} size="sm" aria-label="Start blind recovery">
          <Play size={13} />
          Start Recovery
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <p className="text-xs text-ivory-dim font-mono mb-1">Candidates</p>
          <p className="font-display text-2xl text-ivory">{CANDIDATES.length}</p>
        </Card>
        <Card>
          <p className="text-xs text-ivory-dim font-mono mb-1">Processed</p>
          <p className="font-display text-2xl text-copper">{processed}</p>
        </Card>
        <Card>
          <p className="text-xs text-ivory-dim font-mono mb-1">Confirmed</p>
          <p className="font-display text-2xl text-sage">{confirmed}</p>
        </Card>
        <Card>
          <p className="text-xs text-ivory-dim font-mono mb-1">Mode</p>
          <Badge variant={mode}>{mode}</Badge>
        </Card>
      </div>

      {/* Progress bar */}
      {(isRunning || isCompleted) && (
        <Card>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Discovery Progress</span>
            <span className="text-xs font-mono text-ivory">{processed}/{CANDIDATES.length}</span>
          </div>
          <div className="h-2 bg-surface rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-copper"
              initial={{ width: 0 }}
              animate={{ width: `${(processed / CANDIDATES.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </Card>
      )}

      <div className="grid gap-4" style={{ gridTemplateColumns: '1fr 280px' }}>
        {/* Candidate list */}
        <Card padding="none">
          <div className="px-4 py-2.5 border-b border-border">
            <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">
              Candidate Fields ({CANDIDATES.length})
            </span>
          </div>
          <div className="grid grid-cols-5 gap-0 divide-x divide-border p-4 gap-y-2">
            {CANDIDATES.map((candidate, i) => {
              const status = getCandidateStatus(i, processed, mode === 'hardened')
              return (
                <div key={candidate} className="flex items-center gap-1.5 px-2 py-1">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      status === 'confirmed' ? 'bg-sage' :
                      status === 'rejected' ? 'bg-red-light' :
                      status === 'unknown' ? 'bg-amber' :
                      'bg-border'
                    }`}
                  />
                  <span className={`text-xs font-mono ${statusColors[status]}`}>{candidate}</span>
                </div>
              )
            })}
          </div>

          {/* Legend */}
          <div className="px-4 pb-3 flex gap-4">
            {([['confirmed', '#8EAA91'], ['rejected', '#B84D43'], ['unknown', '#D5A45B'], ['pending', '#3A3530']] as const).map(([label, color]) => (
              <div key={label} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: color }} />
                <span className="text-xs text-ivory-dim capitalize">{label}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Side panel */}
        <div className="space-y-4">
          {experiment && (
            <Card>
              <StatusIndicator status={experiment.status} error={experiment.error} />
            </Card>
          )}

          {mode === 'hardened' && (
            <Card className="border-sage/30">
              <Badge variant="hardened" className="mb-2">Protected</Badge>
              <p className="text-xs text-ivory-dim">
                Field suggestion errors are suppressed. Blind recovery returns no actionable information.
              </p>
            </Card>
          )}

          {experiment?.evidence && experiment.evidence.length > 0 && (
            <Card padding="none">
              <div className="px-4 py-2.5 border-b border-border">
                <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Evidence</span>
              </div>
              {experiment.evidence.map((ev, i) => (
                <div key={i} className={i < experiment.evidence.length - 1 ? 'border-b border-border' : ''}>
                  <button
                    className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-graphite-light text-left"
                    onClick={() => setOpenEvidence(openEvidence === i ? null : i)}
                    aria-expanded={openEvidence === i}
                  >
                    <span className="text-xs font-mono text-ivory-dim">{ev.label}</span>
                    {openEvidence === i ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                  </button>
                  {openEvidence === i && (
                    <div className="px-4 pb-3 text-xs font-mono text-ivory bg-surface mx-4 mb-3 rounded p-2">
                      {JSON.stringify(ev.data, null, 2)}
                    </div>
                  )}
                </div>
              ))}
            </Card>
          )}

          {isCompleted && confirmed > 0 && (
            <Card className="border-red/30">
              <Badge variant="vulnerable" className="mb-2">Schema Leaked</Badge>
              <p className="text-xs text-ivory-dim">
                {confirmed} fields discovered via suggestion errors. Schema partially reconstructed.
              </p>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  )
}
