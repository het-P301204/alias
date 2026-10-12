import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Play, CheckCircle, XCircle, Clock, FlaskConical } from 'lucide-react'
import { useHealth, useScenarios, useExperiments } from '../../hooks/useApi'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { MetricCard } from '../../components/ui/MetricCard'
import { CardSkeleton } from '../../components/ui/LoadingSkeleton'
import type { ExperimentStatus } from '../../services/api'

const scenarioRoutes: Record<string, string> = {
  introspection: '/schema',
  'alias-authorization': '/alias',
  batching: '/batching',
  'query-complexity': '/complexity',
  'blind-recovery': '/blind-recovery',
  'field-authorization': '/field-auth',
}

const difficultyOrder: Record<string, number> = { beginner: 0, intermediate: 1, advanced: 2 }

function StatusIcon({ status }: { status: ExperimentStatus }) {
  if (status === 'completed') return <CheckCircle size={14} className="text-sage" />
  if (status === 'failed' || status === 'timeout') return <XCircle size={14} className="text-red-light" />
  return <Clock size={14} className="text-ivory-dim" />
}

export default function OverviewPage() {
  const navigate = useNavigate()
  const { data: health, isError: healthError } = useHealth()
  const { data: scenarios, isLoading: scenariosLoading } = useScenarios()
  const { data: experiments, isLoading: experimentsLoading } = useExperiments({ limit: 20 })

  const recent = experiments?.slice(0, 5) ?? []
  const completed = experiments?.filter((e) => e.status === 'completed').length ?? 0
  const hardenedVerified = experiments?.filter((e) => e.mode === 'hardened' && e.defensive_control_result?.verified).length ?? 0
  const avgDuration =
    experiments?.filter((e) => e.duration_ms != null).length
      ? Math.round(
          (experiments!.filter((e) => e.duration_ms != null).reduce((s, e) => s + (e.duration_ms ?? 0), 0)) /
            experiments!.filter((e) => e.duration_ms != null).length
        )
      : 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-6 max-w-7xl"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-3xl text-ivory">ALIAS</h1>
          <p className="text-ivory-dim text-sm mt-1">GraphQL Security Research Platform — 6 attack scenarios</p>
        </div>
        {/* Health */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded border text-xs font-mono
            ${health ? 'bg-sage/10 border-sage/30 text-sage' : healthError ? 'bg-red/10 border-red/30 text-red-light' : 'bg-graphite border-border text-ivory-dim'}`}
        >
          <span
            className={`w-2 h-2 rounded-full ${health ? 'bg-sage' : healthError ? 'bg-red-light' : 'bg-ivory-dim animate-pulse'}`}
          />
          {health ? `Backend v${health.version ?? '1.0'} — Online` : healthError ? 'Backend Offline' : 'Connecting…'}
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Total Experiments" value={experiments?.length ?? 0} />
        <MetricCard label="Completed" value={completed} highlight />
        <MetricCard label="Hardened Verified" value={hardenedVerified} />
        <MetricCard
          label="Avg Duration"
          value={avgDuration ? `${avgDuration}ms` : '—'}
        />
      </div>

      {/* Scenario Cards */}
      <div>
        <h2 className="text-sm font-mono text-ivory-dim uppercase tracking-wider mb-3">Scenarios</h2>
        {scenariosLoading ? (
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
          </div>
        ) : scenarios?.length ? (
          <div className="grid grid-cols-3 gap-4">
            {[...scenarios]
              .sort((a, b) => (difficultyOrder[a.difficulty] ?? 0) - (difficultyOrder[b.difficulty] ?? 0))
              .map((scenario) => {
                const lastRun = experiments?.find((e) => e.scenario_id === scenario.id)
                return (
                  <Card
                    key={scenario.id}
                    hover
                    onClick={() => navigate(scenarioRoutes[scenario.id] ?? '/lab')}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="font-mono text-xs text-copper uppercase tracking-wider">{scenario.category}</span>
                      <Badge variant={scenario.difficulty as 'beginner' | 'intermediate' | 'advanced'}>
                        {scenario.difficulty}
                      </Badge>
                    </div>
                    <h3 className="font-display text-lg text-ivory mb-1">{scenario.title}</h3>
                    <p className="text-xs text-ivory-dim line-clamp-2 mb-4">{scenario.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        {lastRun && <StatusIcon status={lastRun.status} />}
                        <span className="text-xs text-ivory-dim font-mono">
                          {lastRun ? lastRun.status : 'No runs yet'}
                        </span>
                      </div>
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(scenarioRoutes[scenario.id] ?? '/lab')
                        }}
                      >
                        <Play size={12} />
                        Run
                      </Button>
                    </div>
                  </Card>
                )
              })}
          </div>
        ) : (
          <Card>
            <div className="text-center py-8 text-ivory-dim">
              <FlaskConical size={32} className="mx-auto mb-3 opacity-40" />
              <p className="text-sm">No scenarios found — is the backend running?</p>
              <Button variant="secondary" size="sm" className="mt-3" onClick={() => window.location.reload()}>
                Retry
              </Button>
            </div>
          </Card>
        )}
      </div>

      {/* Recent Experiments */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-mono text-ivory-dim uppercase tracking-wider">Recent Experiments</h2>
          <Button variant="ghost" size="sm" onClick={() => navigate('/experiments')}>
            View all
          </Button>
        </div>
        {experimentsLoading ? (
          <CardSkeleton />
        ) : (
          <Card padding="none">
            {recent.length === 0 ? (
              <div className="text-center py-8 text-ivory-dim">
                <p className="text-sm">No experiments yet — run a scenario to get started.</p>
              </div>
            ) : (
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="border-b border-border">
                    {['ID', 'Scenario', 'Mode', 'Status', 'Duration'].map((h) => (
                      <th key={h} className="px-4 py-2.5 text-left text-ivory-dim uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recent.map((exp, i) => (
                    <tr
                      key={exp.id}
                      className={`border-b border-border/50 hover:bg-graphite-light/50 cursor-pointer ${i === recent.length - 1 ? 'border-b-0' : ''}`}
                      onClick={() => navigate('/experiments')}
                    >
                      <td className="px-4 py-2.5 text-ivory-dim">
                        {exp.id.slice(0, 8)}…
                        {exp.is_sample && <Badge variant="sample" className="ml-2">sample</Badge>}
                      </td>
                      <td className="px-4 py-2.5 text-copper-light">{exp.scenario_id}</td>
                      <td className="px-4 py-2.5">
                        <Badge variant={exp.mode}>{exp.mode}</Badge>
                      </td>
                      <td className="px-4 py-2.5">
                        <Badge
                          variant={exp.status}
                          pulse={['running', 'validating', 'analyzing'].includes(exp.status)}
                        >
                          {exp.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-2.5 text-ivory-dim">
                        {exp.duration_ms != null ? `${exp.duration_ms}ms` : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Card>
        )}
      </div>
    </motion.div>
  )
}
