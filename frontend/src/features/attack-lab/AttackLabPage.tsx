import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, XCircle, ChevronDown, ChevronUp } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { useScenarios } from '../../hooks/useApi'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Button } from '../../components/ui/Button'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import { JsonViewer } from '../../components/ui/JsonViewer'
import type { LabMode } from '../../services/api'

const scenarioQueries: Record<string, string> = {
  introspection: `# Introspection Query
{
  __schema {
    types {
      name
      kind
      fields {
        name
        type { name kind }
      }
    }
  }
}`,
  'alias-authorization': `# Alias Authorization Attack
{
  order1: order(id: "ORD-001") { id total owner }
  order2: order(id: "ORD-002") { id total owner }
  order3: order(id: "ORD-003") { id total owner }
}`,
  batching: `# Batched Operations
query Op1 { viewer { id name } }
query Op2 { viewer { email role } }
query Op3 { orders { id status } }`,
  'query-complexity': `# Deep Nested Query
{
  users {
    orders {
      items {
        product {
          reviews {
            author { orders { items { product { id } } } }
          }
        }
      }
    }
  }
}`,
  'blind-recovery': `# Blind Schema Recovery
# Uses field suggestion errors to discover schema
{
  __type(name: "User") {
    fields { name type { name } }
  }
}`,
  'field-authorization': `# Field Authorization Test
{
  viewer {
    id
    name
    email
    ssn
    creditCard
    internalNotes
  }
}`,
}

export default function AttackLabPage() {
  const [selectedScenario, setSelectedScenario] = useState('introspection')
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [openEvidence, setOpenEvidence] = useState<number | null>(null)

  const { data: scenarios } = useScenarios()
  const { experiment, isLoading, error, start, cancel } = useExperimentRunner()

  const currentScenario = scenarios?.find((s) => s.id === selectedScenario)
  const query = scenarioQueries[selectedScenario] ?? '# Select a scenario'

  const handleRun = () => {
    start(selectedScenario, mode, currentScenario?.default_config ?? {})
  }

  const isActive = experiment && ['ready', 'validating', 'running', 'analyzing'].includes(experiment.status)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="h-full p-6"
    >
      <div className="flex items-center gap-4 mb-5">
        <h1 className="font-display text-2xl text-ivory">Attack Lab</h1>
        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      <div className="grid gap-4 h-[calc(100%-60px)]" style={{ gridTemplateColumns: '320px 1fr 320px' }}>
        {/* LEFT: Config Panel */}
        <div className="flex flex-col gap-4 overflow-auto">
          <Card>
            <label className="block text-xs font-mono text-ivory-dim uppercase tracking-wider mb-2">
              Scenario
            </label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full bg-surface border border-border rounded px-3 py-2 text-sm text-ivory font-mono focus:border-copper outline-none"
              aria-label="Scenario selector"
            >
              {scenarios?.map((s) => (
                <option key={s.id} value={s.id}>{s.title}</option>
              )) ?? (
                <option value="introspection">Schema Introspection</option>
              )}
            </select>
          </Card>

          {currentScenario && (
            <Card>
              <p className="text-xs font-mono text-copper uppercase tracking-wider mb-1">{currentScenario.category}</p>
              <h3 className="font-display text-base text-ivory mb-2">{currentScenario.title}</h3>
              <p className="text-xs text-ivory-dim leading-relaxed mb-3">{currentScenario.description}</p>
              {currentScenario.learning_objectives.length > 0 && (
                <div>
                  <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-1">Objectives</p>
                  <ul className="space-y-1">
                    {currentScenario.learning_objectives.map((obj, i) => (
                      <li key={i} className="text-xs text-ivory-dim flex gap-2">
                        <span className="text-copper mt-0.5">›</span>
                        {obj}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Card>
          )}

          <div className="flex gap-2">
            <Button
              className="flex-1"
              onClick={handleRun}
              loading={isLoading || !!isActive}
              disabled={!selectedScenario}
              aria-label="Run experiment"
            >
              <Play size={14} />
              Run Experiment
            </Button>
            {isActive && (
              <Button variant="danger" size="md" onClick={cancel} aria-label="Cancel experiment">
                <XCircle size={14} />
              </Button>
            )}
          </div>
        </div>

        {/* CENTER: Query Preview */}
        <div className="flex flex-col gap-4 min-w-0">
          <Card padding="none" className="flex-1">
            <div className="px-4 py-2.5 border-b border-border">
              <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Query Preview</span>
            </div>
            <div style={{ height: 300 }}>
              <Editor
                value={query}
                language="graphql"
                theme="vs-dark"
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  lineNumbers: 'off',
                  scrollBeyondLastLine: false,
                  fontSize: 12,
                  fontFamily: 'JetBrains Mono, monospace',
                  padding: { top: 12 },
                }}
              />
            </div>
          </Card>

          {error && (
            <Card className="border-red/30">
              <p className="text-xs text-red-light font-mono">
                {error instanceof Error ? error.message : 'An error occurred'}
              </p>
            </Card>
          )}
        </div>

        {/* RIGHT: Results Panel */}
        <div className="flex flex-col gap-4 overflow-auto">
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Status</p>
            <StatusIndicator
              status={experiment?.status ?? 'ready'}
              error={experiment?.error}
            />
          </Card>

          {experiment?.actual_outcome && (
            <Card>
              <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-2">Outcome</p>
              <p className="text-xs text-ivory-dim">{experiment.actual_outcome}</p>
            </Card>
          )}

          {experiment?.evidence && experiment.evidence.length > 0 && (
            <Card padding="none">
              <div className="px-4 py-2.5 border-b border-border">
                <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Evidence</span>
              </div>
              <div className="divide-y divide-border">
                {experiment.evidence.map((ev, i) => (
                  <div key={i}>
                    <button
                      className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-graphite-light text-left"
                      onClick={() => setOpenEvidence(openEvidence === i ? null : i)}
                      aria-expanded={openEvidence === i}
                    >
                      <span className="text-xs font-mono text-ivory-dim">{ev.label}</span>
                      {openEvidence === i ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                    {openEvidence === i && (
                      <div className="px-4 pb-3">
                        <JsonViewer data={ev.data} maxHeight={200} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {experiment?.defensive_control_result && (
            <Card className={experiment.defensive_control_result.verified ? 'border-sage/40' : 'border-red/30'}>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={experiment.defensive_control_result.verified ? 'hardened' : 'vulnerable'}>
                  {experiment.defensive_control_result.verified ? 'Defense Active' : 'Defense Bypassed'}
                </Badge>
              </div>
              <p className="text-xs text-ivory-dim">{experiment.defensive_control_result.description}</p>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  )
}
