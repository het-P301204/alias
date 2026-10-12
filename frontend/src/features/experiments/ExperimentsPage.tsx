import { useState } from 'react'
import { motion } from 'framer-motion'
import { Search, Download, Play, ChevronLeft, ChevronRight } from 'lucide-react'
import { useExperiments, useStartExperiment } from '../../hooks/useApi'
import { api } from '../../services/api'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { Drawer } from '../../components/ui/Drawer'
import { JsonViewer } from '../../components/ui/JsonViewer'
import { CardSkeleton } from '../../components/ui/LoadingSkeleton'
import type { Experiment, ExperimentStatus, LabMode } from '../../services/api'

const PAGE_SIZE = 10

const statusOptions: Array<ExperimentStatus | 'all'> = [
  'all', 'ready', 'validating', 'running', 'analyzing', 'completed', 'failed', 'timeout', 'cancelled',
]

const scenarioOptions = [
  'all',
  'introspection',
  'alias-authorization',
  'batching',
  'query-complexity',
  'blind-recovery',
  'field-authorization',
]

export default function ExperimentsPage() {
  const [search, setSearch] = useState('')
  const [scenarioFilter, setScenarioFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState<ExperimentStatus | 'all'>('all')
  const [page, setPage] = useState(0)
  const [selectedExp, setSelectedExp] = useState<Experiment | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const { data: experiments, isLoading } = useExperiments({ limit: 100 })
  const startMutation = useStartExperiment()

  const filtered = (experiments ?? []).filter((e) => {
    const matchSearch = !search || e.id.includes(search) || e.scenario_id.includes(search)
    const matchScenario = scenarioFilter === 'all' || e.scenario_id === scenarioFilter
    const matchStatus = statusFilter === 'all' || e.status === statusFilter
    return matchSearch && matchScenario && matchStatus
  })

  const paged = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)
  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)

  const handleRerun = async (exp: Experiment) => {
    await startMutation.mutateAsync({
      scenario_id: exp.scenario_id,
      mode: exp.mode,
      parameters: exp.config as Record<string, unknown>,
    })
  }

  const handleExport = async (exp: Experiment, format: 'json' | 'csv' | 'html') => {
    try {
      const res = await api.reports.get(exp.id, format)
      const blob = new Blob([res.data as BlobPart])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `alias-report-${exp.id.slice(0, 8)}.${format}`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      const json = JSON.stringify(exp, null, 2)
      const blob = new Blob([json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `alias-report-${exp.id.slice(0, 8)}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div>
        <h1 className="font-display text-2xl text-ivory">Experiments & Reports</h1>
        <p className="text-sm text-ivory-dim mt-1">{filtered.length} experiments{search || scenarioFilter !== 'all' || statusFilter !== 'all' ? ' (filtered)' : ''}</p>
      </div>

      {/* Filters */}
      <Card className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-ivory-dim" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID or scenario…"
            className="w-full bg-surface border border-border rounded pl-8 pr-3 py-1.5 text-xs text-ivory font-mono placeholder:text-ivory-dim/50 focus:border-copper outline-none"
            aria-label="Search experiments"
          />
        </div>

        <select
          value={scenarioFilter}
          onChange={(e) => setScenarioFilter(e.target.value)}
          className="bg-surface border border-border rounded px-3 py-1.5 text-xs text-ivory font-mono focus:border-copper outline-none"
          aria-label="Scenario filter"
        >
          {scenarioOptions.map((s) => (
            <option key={s} value={s}>{s === 'all' ? 'All Scenarios' : s}</option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ExperimentStatus | 'all')}
          className="bg-surface border border-border rounded px-3 py-1.5 text-xs text-ivory font-mono focus:border-copper outline-none"
          aria-label="Status filter"
        >
          {statusOptions.map((s) => (
            <option key={s} value={s}>{s === 'all' ? 'All Statuses' : s}</option>
          ))}
        </select>
      </Card>

      {/* Table */}
      {isLoading ? (
        <CardSkeleton />
      ) : (
        <Card padding="none">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b border-border">
                {['ID', 'Scenario', 'Mode', 'Status', 'Duration', 'Started', 'Actions'].map((h) => (
                  <th key={h} className="px-4 py-2.5 text-left text-ivory-dim uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paged.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-ivory-dim">
                    No experiments found
                  </td>
                </tr>
              ) : (
                paged.map((exp, i) => (
                  <tr
                    key={exp.id}
                    className={`border-b border-border/50 hover:bg-graphite-light/50 cursor-pointer ${i === paged.length - 1 ? 'border-b-0' : ''}`}
                    onClick={() => { setSelectedExp(exp); setDrawerOpen(true) }}
                  >
                    <td className="px-4 py-2.5">
                      <span className="text-ivory-dim">{exp.id.slice(0, 8)}…</span>
                      {exp.is_sample && <Badge variant="sample" className="ml-1.5">sample</Badge>}
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
                    <td className="px-4 py-2.5 text-ivory-dim">
                      {new Date(exp.started_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5" onClick={(e) => e.stopPropagation()}>
                      <div className="flex gap-1.5">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRerun(exp)}
                          loading={startMutation.isPending}
                          aria-label="Re-run experiment"
                        >
                          <Play size={11} />
                        </Button>
                        <div className="relative group">
                          <Button
                            variant="ghost"
                            size="sm"
                            aria-label="Export experiment"
                          >
                            <Download size={11} />
                          </Button>
                          <div className="hidden group-hover:flex absolute right-0 top-full mt-1 bg-graphite border border-border rounded shadow-lg z-10 flex-col">
                            {(['json', 'csv', 'html'] as const).map((fmt) => (
                              <button
                                key={fmt}
                                onClick={() => handleExport(exp, fmt)}
                                className="px-3 py-1.5 text-xs font-mono text-ivory-dim hover:text-ivory hover:bg-graphite-light text-left"
                              >
                                .{fmt}
                              </button>
                            ))}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-border">
              <span className="text-xs text-ivory-dim font-mono">
                Page {page + 1} of {totalPages}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  aria-label="Previous page"
                >
                  <ChevronLeft size={14} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                  aria-label="Next page"
                >
                  <ChevronRight size={14} />
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Detail Drawer */}
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={selectedExp ? `Experiment ${selectedExp.id.slice(0, 8)}` : ''}
        width={520}
      >
        {selectedExp && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              <Badge variant={selectedExp.mode}>{selectedExp.mode}</Badge>
              <Badge
                variant={selectedExp.status}
                pulse={['running', 'validating', 'analyzing'].includes(selectedExp.status)}
              >
                {selectedExp.status}
              </Badge>
              {selectedExp.is_sample && <Badge variant="sample">sample</Badge>}
            </div>

            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-ivory-dim">Scenario</span>
                <span className="text-copper-light">{selectedExp.scenario_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ivory-dim">Started</span>
                <span className="text-ivory">{new Date(selectedExp.started_at).toLocaleString()}</span>
              </div>
              {selectedExp.duration_ms != null && (
                <div className="flex justify-between">
                  <span className="text-ivory-dim">Duration</span>
                  <span className="text-ivory">{selectedExp.duration_ms}ms</span>
                </div>
              )}
            </div>

            {selectedExp.input_summary && (
              <div>
                <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-1">Input</p>
                <p className="text-xs text-ivory-dim bg-surface rounded p-2">{selectedExp.input_summary}</p>
              </div>
            )}

            {selectedExp.actual_outcome && (
              <div>
                <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-1">Outcome</p>
                <p className="text-xs text-ivory bg-surface rounded p-2">{selectedExp.actual_outcome}</p>
              </div>
            )}

            <JsonViewer data={selectedExp} label="Full Result" maxHeight={300} />
          </div>
        )}
      </Drawer>
    </motion.div>
  )
}
