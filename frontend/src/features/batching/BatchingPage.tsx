import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play } from 'lucide-react'
import Editor from '@monaco-editor/react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import { BatchTimeline } from '../../components/visualization/BatchTimeline'
import type { LabMode } from '../../services/api'

function buildBatchQuery(count: number): string {
  const queries = Array.from({ length: count }, (_, i) => {
    const names = ['viewer', 'orders', 'products', 'users', 'notifications', 'profile', 'settings', 'analytics', 'reports', 'audit']
    return `  op${i + 1}: ${names[i % names.length] ?? 'query'} { id }`
  })
  return `# Batched Query — ${count} operations in 1 HTTP request\n{\n${queries.join('\n')}\n}`
}

export default function BatchingPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [operationCount, setOperationCount] = useState(5)
  const { experiment, isLoading, start } = useExperimentRunner()

  const query = buildBatchQuery(operationCount)

  const handleRun = () => {
    start('batching', mode, { operation_count: operationCount })
  }

  const maxAllowed = mode === 'hardened' ? 3 : operationCount
  const acceptedCount = Math.min(operationCount, maxAllowed)
  const rejectedCount = operationCount - acceptedCount

  const chartData = [
    { name: 'Operations', Accepted: acceptedCount, Rejected: rejectedCount },
  ]

  const timelineOps = Array.from({ length: operationCount }, (_, i) => ({
    id: i + 1,
    status: (i < acceptedCount ? 'accepted' : 'rejected') as 'accepted' | 'rejected',
  }))

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div className="flex items-center gap-4">
        <h1 className="font-display text-2xl text-ivory">Batching & Rate Limits</h1>
        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: '320px 1fr' }}>
        {/* Controls */}
        <div className="space-y-4">
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-4">Operation Count</p>
            <input
              type="range"
              min={1}
              max={10}
              value={operationCount}
              onChange={(e) => setOperationCount(Number(e.target.value))}
              className="w-full accent-copper"
              aria-label="Operation count slider"
            />
            <div className="flex justify-between mt-2">
              <span className="text-xs font-mono text-ivory-dim">1</span>
              <span className="font-display text-2xl text-copper">{operationCount}</span>
              <span className="text-xs font-mono text-ivory-dim">10</span>
            </div>
          </Card>

          {/* Dual metrics */}
          <div className="grid grid-cols-2 gap-3">
            <Card className="text-center">
              <p className="text-xs text-ivory-dim font-mono mb-1">HTTP Requests</p>
              <p className="font-display text-3xl text-copper">1</p>
            </Card>
            <Card className="text-center">
              <p className="text-xs text-ivory-dim font-mono mb-1">Operations</p>
              <p className="font-display text-3xl text-ivory">{operationCount}</p>
            </Card>
          </div>

          {mode === 'hardened' && (
            <Card className="border-sage/30">
              <p className="text-xs font-mono text-sage mb-1">Rate Limit Active</p>
              <p className="text-xs text-ivory-dim">Max {maxAllowed} operations per request</p>
            </Card>
          )}

          <Button className="w-full" onClick={handleRun} loading={isLoading} aria-label="Run batch test">
            <Play size={14} />
            Run Batch Test
          </Button>

          {experiment && (
            <StatusIndicator status={experiment.status} error={experiment.error} />
          )}
        </div>

        {/* Right panel */}
        <div className="space-y-4">
          <Card padding="none">
            <div className="px-4 py-2.5 border-b border-border">
              <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Batch Preview</span>
            </div>
            <div style={{ height: 240 }}>
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

          <div className="grid grid-cols-2 gap-4">
            <Card>
              <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Breakdown</p>
              <ResponsiveContainer width="100%" height={120}>
                <BarChart data={chartData}>
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
                  />
                  <Legend wrapperStyle={{ fontSize: 10, color: '#C8C2B8' }} />
                  <Bar dataKey="Accepted" fill="#8EAA91" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="Rejected" fill="#B84D43" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card>
              <BatchTimeline
                operations={timelineOps}
                title="Execution Timeline"
              />
            </Card>
          </div>

          {rejectedCount > 0 && (
            <Card className="border-red/30">
              <div className="flex items-center gap-2">
                <Badge variant="failed">Rate Limited</Badge>
                <span className="text-xs text-ivory-dim font-mono">
                  {rejectedCount} operation{rejectedCount !== 1 ? 's' : ''} rejected — exceeded limit of {maxAllowed}
                </span>
              </div>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  )
}
