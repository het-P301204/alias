import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Plus, Minus, CheckCircle, XCircle } from 'lucide-react'
import Editor from '@monaco-editor/react'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import type { LabMode } from '../../services/api'

const USERS = [
  { id: 'alice', name: 'Alice Chen', role: 'CUSTOMER', color: '#8EAA91' },
  { id: 'bob', name: 'Bob Torres', role: 'CUSTOMER', color: '#D5A45B' },
  { id: 'carol', name: 'Carol Kim', role: 'STAFF', color: '#B97853' },
]

const ORDERS = [
  { id: 'ORD-001', owner: 'alice', total: '$149.99' },
  { id: 'ORD-002', owner: 'bob', total: '$89.50' },
  { id: 'ORD-003', owner: 'alice', total: '$234.00' },
  { id: 'ORD-004', owner: 'bob', total: '$45.00' },
  { id: 'ORD-005', owner: 'carol', total: '$320.75' },
]

function buildQuery(selectedUser: string, selectedOrders: string[], aliasCount: number): string {
  const aliases = selectedOrders.slice(0, aliasCount).map((orderId, i) =>
    `  alias${i + 1}: order(id: "${orderId}") {\n    id\n    total\n    owner {\n      id\n      name\n    }\n  }`
  )
  return `# Alias Authorization Attack (user: ${selectedUser})\n# ${aliasCount} aliases in 1 HTTP request\n{\n${aliases.join('\n')}\n}`
}

export default function AliasAuthPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [selectedUser, setSelectedUser] = useState('alice')
  const [selectedOrders, setSelectedOrders] = useState<string[]>(['ORD-001', 'ORD-002'])
  const [aliasCount, setAliasCount] = useState(3)
  const { experiment, isLoading, start } = useExperimentRunner()

  const toggleOrder = (id: string) => {
    setSelectedOrders((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    )
  }

  const query = buildQuery(selectedUser, selectedOrders, aliasCount)

  const handleRun = () => {
    start('alias-authorization', mode, {
      user_id: selectedUser,
      order_ids: selectedOrders.slice(0, aliasCount),
      alias_count: aliasCount,
    })
  }

  type AuthResult = { orderId: string; expectedOwner: string; actualOwner: string; authorized: boolean }

  const results: AuthResult[] = experiment?.evidence?.find((e) => e.type === 'table')?.data as AuthResult[] ?? (
    mode === 'vulnerable'
      ? selectedOrders.slice(0, aliasCount).map((orderId) => {
          const order = ORDERS.find((o) => o.id === orderId)
          return {
            orderId,
            expectedOwner: order?.owner ?? '?',
            actualOwner: order?.owner ?? '?',
            authorized: order?.owner === selectedUser || selectedUser === 'carol',
          }
        })
      : []
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div className="flex items-center gap-4">
        <h1 className="font-display text-2xl text-ivory">Alias Authorization Lab</h1>
        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      <div className="grid gap-4" style={{ gridTemplateColumns: '320px 1fr' }}>
        {/* Controls */}
        <div className="space-y-4">
          {/* User selector */}
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Acting User</p>
            <div className="space-y-2">
              {USERS.map((user) => (
                <button
                  key={user.id}
                  onClick={() => setSelectedUser(user.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded border transition-all text-left
                    ${selectedUser === user.id ? 'border-copper/50 bg-copper/10' : 'border-border bg-surface hover:border-border/80'}`}
                  aria-pressed={selectedUser === user.id}
                >
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold text-obsidian"
                    style={{ background: user.color }}
                  >
                    {user.name[0]}
                  </div>
                  <div>
                    <p className="text-sm text-ivory font-medium">{user.name}</p>
                    <p className="text-xs text-ivory-dim font-mono">{user.role}</p>
                  </div>
                </button>
              ))}
            </div>
          </Card>

          {/* Order selector */}
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Target Orders</p>
            <div className="space-y-1.5">
              {ORDERS.map((order) => (
                <label key={order.id} className="flex items-center gap-3 px-2 py-1.5 rounded hover:bg-graphite-light cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedOrders.includes(order.id)}
                    onChange={() => toggleOrder(order.id)}
                    className="accent-copper"
                    aria-label={`Select order ${order.id}`}
                  />
                  <span className="text-xs font-mono text-ivory">{order.id}</span>
                  <span className="text-xs text-ivory-dim ml-auto">{order.total}</span>
                  <span className="text-xs font-mono text-copper-light">{order.owner}</span>
                </label>
              ))}
            </div>
          </Card>

          {/* Alias count */}
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Alias Count</p>
            <div className="flex items-center gap-3">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setAliasCount(Math.max(1, aliasCount - 1))}
                aria-label="Decrease alias count"
              >
                <Minus size={12} />
              </Button>
              <span className="font-display text-2xl text-copper w-8 text-center">{aliasCount}</span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setAliasCount(Math.min(10, aliasCount + 1))}
                aria-label="Increase alias count"
              >
                <Plus size={12} />
              </Button>
              <span className="text-xs text-ivory-dim font-mono ml-2">aliases / request</span>
            </div>
          </Card>

          {/* Visualization */}
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Request Structure</p>
            <div className="flex items-center gap-2 text-xs font-mono">
              <div className="px-3 py-1.5 bg-copper/20 border border-copper/30 rounded text-copper-light">
                1 HTTP Request
              </div>
              <span className="text-ivory-dim">→</span>
              <div className="flex gap-1 flex-wrap">
                {Array.from({ length: aliasCount }).map((_, i) => (
                  <div key={i} className="px-2 py-1 bg-surface border border-border rounded text-ivory-dim text-[10px]">
                    alias{i + 1}
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Button className="w-full" onClick={handleRun} loading={isLoading} aria-label="Run authorization test">
            <Play size={14} />
            Run Test
          </Button>

          {experiment && (
            <StatusIndicator status={experiment.status} error={experiment.error} />
          )}
        </div>

        {/* Right panel */}
        <div className="space-y-4">
          <Card padding="none">
            <div className="px-4 py-2.5 border-b border-border">
              <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Generated Query</span>
            </div>
            <div style={{ height: 260 }}>
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

          {/* Results table */}
          {results.length > 0 && (
            <Card padding="none">
              <div className="px-4 py-2.5 border-b border-border flex items-center gap-2">
                <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Authorization Results</span>
                {mode === 'vulnerable' ? (
                  <Badge variant="vulnerable">Vulnerable</Badge>
                ) : (
                  <Badge variant="hardened">Hardened</Badge>
                )}
              </div>
              <table className="w-full text-xs font-mono">
                <thead>
                  <tr className="border-b border-border">
                    {['Order ID', 'Expected Owner', 'Actual Returned', 'Authorized'].map((h) => (
                      <th key={h} className="px-4 py-2.5 text-left text-ivory-dim uppercase tracking-wider">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {results.map((row, i) => (
                    <tr
                      key={i}
                      className={`border-b border-border/50 ${!row.authorized ? 'bg-red/5' : ''}`}
                    >
                      <td className="px-4 py-2.5 text-ivory">{row.orderId}</td>
                      <td className="px-4 py-2.5 text-ivory-dim">{row.expectedOwner}</td>
                      <td className="px-4 py-2.5 text-ivory-dim">{row.actualOwner}</td>
                      <td className="px-4 py-2.5">
                        {row.authorized ? (
                          <CheckCircle size={14} className="text-sage" />
                        ) : (
                          <XCircle size={14} className="text-red-light" />
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  )
}
