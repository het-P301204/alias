import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import { ComplexityHeatMap } from '../../components/visualization/ComplexityHeatMap'
import type { LabMode } from '../../services/api'

type Preset = 'shallow' | 'medium' | 'deep'

const PRESETS: Record<Preset, { label: string; query: string; depth: number; complexity: number }> = {
  shallow: {
    label: 'Shallow',
    depth: 2,
    complexity: 10,
    query: `# Shallow Query — depth: 2, complexity: 10
{
  viewer {
    id
    name
    email
  }
}`,
  },
  medium: {
    label: 'Medium',
    depth: 4,
    complexity: 45,
    query: `# Medium Query — depth: 4, complexity: 45
{
  users {
    orders {
      items {
        product {
          name
          price
        }
      }
    }
  }
}`,
  },
  deep: {
    label: 'Deep',
    depth: 7,
    complexity: 180,
    query: `# Deep Nested Query — depth: 7, complexity: 180
{
  users {
    orders {
      items {
        product {
          reviews {
            author {
              orders {
                items { id }
              }
            }
          }
        }
      }
    }
  }
}`,
  },
}

const FIELDS = [
  { name: 'users', cost: 10 },
  { name: 'orders', cost: 8 },
  { name: 'items', cost: 6 },
  { name: 'product', cost: 5 },
  { name: 'reviews', cost: 15 },
  { name: 'author', cost: 8 },
  { name: 'viewer', cost: 2 },
]

const BUDGET = 100

export default function QueryComplexityPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [preset, setPreset] = useState<Preset>('medium')
  const { experiment, isLoading, start } = useExperimentRunner()

  const current = PRESETS[preset]
  const isOverBudget = current.complexity > BUDGET
  const budgetRemaining = Math.max(0, BUDGET - current.complexity)

  const handleRun = () => {
    start('query-complexity', mode, { preset, depth: current.depth, complexity: current.complexity })
  }

  const executionData = [
    { name: preset, time: mode === 'vulnerable' ? current.complexity * 3 : isOverBudget ? 0 : current.complexity * 2 },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div className="flex items-center gap-4">
        <h1 className="font-display text-2xl text-ivory">Query Complexity Lab</h1>
        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: '320px 1fr' }}>
        {/* Controls */}
        <div className="space-y-4">
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Preset</p>
            <div className="flex gap-2">
              {(Object.keys(PRESETS) as Preset[]).map((p) => (
                <button
                  key={p}
                  onClick={() => setPreset(p)}
                  className={`flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider border transition-all
                    ${preset === p
                      ? p === 'shallow' ? 'bg-sage/20 text-sage border-sage/30'
                        : p === 'medium' ? 'bg-amber/20 text-amber border-amber/30'
                        : 'bg-red/20 text-red-light border-red/30'
                      : 'bg-graphite border-border text-ivory-dim hover:text-ivory'
                    }`}
                  aria-pressed={preset === p}
                >
                  {PRESETS[p].label}
                </button>
              ))}
            </div>
          </Card>

          {/* Complexity calculator */}
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Complexity Analysis</p>
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-ivory-dim">Depth</span>
                <span className="text-ivory">{current.depth}</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-ivory-dim">Complexity Score</span>
                <span className={isOverBudget ? 'text-red-light' : 'text-ivory'}>{current.complexity}</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-ivory-dim">Budget</span>
                <span className="text-amber">{BUDGET}</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-ivory-dim">Remaining</span>
                <span className={budgetRemaining === 0 ? 'text-red-light' : 'text-sage'}>{budgetRemaining}</span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-3 h-2 rounded-full bg-surface overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(100, (current.complexity / BUDGET) * 100)}%`,
                  background: isOverBudget ? '#B84D43' : current.complexity > BUDGET * 0.7 ? '#D5A45B' : '#8EAA91',
                }}
              />
            </div>
          </Card>

          {mode === 'hardened' && isOverBudget && (
            <Card className="border-sage/30">
              <Badge variant="hardened" className="mb-2">Protection Active</Badge>
              <p className="text-xs text-ivory-dim">Query exceeds complexity budget and will be rejected.</p>
            </Card>
          )}

          <Button className="w-full" onClick={handleRun} loading={isLoading} aria-label="Run complexity test">
            <Play size={14} />
            Analyze & Run
          </Button>

          {experiment && (
            <StatusIndicator status={experiment.status} error={experiment.error} />
          )}
        </div>

        {/* Right */}
        <div className="space-y-4">
          <Card padding="none">
            <div className="px-4 py-2.5 border-b border-border">
              <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Query</span>
            </div>
            <div style={{ height: 220 }}>
              <Editor
                value={current.query}
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

          <div className="grid grid-cols-2 gap-4">
            <Card>
              <ComplexityHeatMap fields={FIELDS} budget={BUDGET} />
            </Card>

            <Card>
              <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Execution Time (est.)</p>
              <ResponsiveContainer width="100%" height={140}>
                <BarChart data={executionData}>
                  <XAxis dataKey="name" tick={{ fill: '#C8C2B8', fontSize: 10 }} />
                  <YAxis tick={{ fill: '#C8C2B8', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      background: '#282624',
                      border: '1px solid #3A3530',
                      borderRadius: 4,
                      color: '#F5F0E8',
                      fontSize: 11,
                    }}
                    formatter={(v: number) => [`${v}ms`, 'Time']}
                  />
                  <Bar dataKey="time" radius={[3, 3, 0, 0]}>
                    {executionData.map((_, i) => (
                      <Cell
                        key={i}
                        fill={mode === 'hardened' && isOverBudget ? '#B84D43' : '#8EAA91'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              {mode === 'hardened' && isOverBudget && (
                <Badge variant="failed" className="mt-2">Rejected — over budget</Badge>
              )}
            </Card>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
