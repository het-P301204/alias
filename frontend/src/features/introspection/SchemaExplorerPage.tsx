import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Play, EyeOff } from 'lucide-react'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { useExperiments } from '../../hooks/useApi'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { Drawer } from '../../components/ui/Drawer'
import { SchemaGraph } from '../../components/visualization/SchemaGraph'
import { MetricCard } from '../../components/ui/MetricCard'
import type { LabMode } from '../../services/api'

type Kind = 'ALL' | 'Query' | 'Mutation' | 'Object' | 'Enum' | 'Scalar'

const SAMPLE_TYPES = [
  { name: 'Query', kind: 'QUERY', fields: ['viewer', 'user', 'order', 'orders', 'product'] },
  { name: 'Mutation', kind: 'MUTATION', fields: ['createOrder', 'updateUser', 'deleteOrder'] },
  { name: 'User', kind: 'OBJECT', fields: ['id', 'name', 'email', 'ssn', 'orders', 'role'] },
  { name: 'Order', kind: 'OBJECT', fields: ['id', 'total', 'status', 'owner', 'items'] },
  { name: 'Product', kind: 'OBJECT', fields: ['id', 'name', 'price', 'reviews'] },
  { name: 'OrderItem', kind: 'OBJECT', fields: ['id', 'product', 'quantity', 'price'] },
  { name: 'Review', kind: 'OBJECT', fields: ['id', 'author', 'rating', 'comment'] },
  { name: 'Role', kind: 'ENUM', fields: ['GUEST', 'CUSTOMER', 'STAFF', 'ADMIN'] },
  { name: 'OrderStatus', kind: 'ENUM', fields: ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED'] },
  { name: 'String', kind: 'SCALAR', fields: [] },
  { name: 'Int', kind: 'SCALAR', fields: [] },
  { name: 'Boolean', kind: 'SCALAR', fields: [] },
  { name: 'ID', kind: 'SCALAR', fields: [] },
]

export default function SchemaExplorerPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [search, setSearch] = useState('')
  const [kindFilter, setKindFilter] = useState<Kind>('ALL')
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const { start, isLoading, experiment } = useExperimentRunner()
  const { data: experiments } = useExperiments({ scenario_id: 'introspection' })

  const lastRun = experiments?.[0]
  const types = useMemo(() => {
    if (mode === 'hardened') return []
    return SAMPLE_TYPES
  }, [mode])

  const filtered = useMemo(() => {
    return types.filter((t) => {
      const matchesSearch = !search || t.name.toLowerCase().includes(search.toLowerCase())
      const matchesKind = kindFilter === 'ALL' || t.kind.toLowerCase() === kindFilter.toLowerCase()
      return matchesSearch && matchesKind
    })
  }, [types, search, kindFilter])

  const selectedTypeData = SAMPLE_TYPES.find((t) => t.name === selectedType)

  const handleRun = () => start('introspection', mode)

  const kinds: Kind[] = ['ALL', 'Query', 'Mutation', 'Object', 'Enum', 'Scalar']
  const kindVariants: Record<Kind, string> = {
    ALL: 'default',
    Query: 'vulnerable',
    Mutation: 'vulnerable',
    Object: 'hardened',
    Enum: 'sample',
    Scalar: 'default',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-5"
    >
      <div className="flex items-center gap-4">
        <h1 className="font-display text-2xl text-ivory">Schema Explorer</h1>
        <ModeToggle mode={mode} onChange={setMode} />
        <Button onClick={handleRun} loading={isLoading} size="sm" aria-label="Run schema discovery">
          <Play size={13} />
          Run Discovery
        </Button>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Types" value={mode === 'hardened' ? '—' : types.length} />
        <MetricCard label="Fields" value={mode === 'hardened' ? '—' : types.reduce((s, t) => s + t.fields.length, 0)} />
        <MetricCard label="Mutations" value={mode === 'hardened' ? '—' : types.filter((t) => t.kind === 'MUTATION').flatMap((t) => t.fields).length} />
        <MetricCard label="Deprecated" value={0} />
      </div>

      {mode === 'hardened' ? (
        <Card className="border-sage/30">
          <div className="flex flex-col items-center py-12 gap-4">
            <EyeOff size={48} className="text-sage opacity-60" />
            <h3 className="font-display text-xl text-sage">Introspection Disabled</h3>
            <p className="text-ivory-dim text-sm text-center max-w-md">
              In hardened mode, GraphQL introspection is disabled. Attackers cannot enumerate the schema.
              Schema discovery returns an error: "Introspection is not allowed."
            </p>
            {lastRun && (
              <Badge variant={lastRun.status as 'completed' | 'failed'}>{lastRun.status}</Badge>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid gap-4" style={{ gridTemplateColumns: '280px 1fr' }}>
          {/* Left: Type List */}
          <div className="space-y-3">
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-ivory-dim" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search types…"
                className="w-full bg-surface border border-border rounded pl-9 pr-3 py-2 text-sm text-ivory font-mono placeholder:text-ivory-dim/50 focus:border-copper outline-none"
                aria-label="Search types"
              />
            </div>

            <div className="flex flex-wrap gap-1.5">
              {kinds.map((k) => (
                <button
                  key={k}
                  onClick={() => setKindFilter(k)}
                  className={`px-2 py-0.5 rounded text-xs font-mono border transition-all
                    ${kindFilter === k ? 'bg-copper/20 text-copper-light border-copper/30' : 'bg-graphite border-border text-ivory-dim hover:text-ivory'}`}
                  aria-pressed={kindFilter === k}
                >
                  {k}
                </button>
              ))}
            </div>

            <Card padding="none" className="max-h-96 overflow-auto">
              {filtered.map((t, i) => (
                <button
                  key={t.name}
                  onClick={() => { setSelectedType(t.name); setDrawerOpen(true) }}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-graphite-light transition-colors text-xs font-mono
                    ${i < filtered.length - 1 ? 'border-b border-border' : ''}
                    ${selectedType === t.name ? 'bg-graphite-light' : ''}`}
                  aria-label={`Open ${t.name} type`}
                >
                  <span className="text-ivory">{t.name}</span>
                  <span className="text-ivory-dim text-[10px] uppercase">{t.kind}</span>
                </button>
              ))}
            </Card>
          </div>

          {/* Right: Graph */}
          <SchemaGraph types={filtered} onTypeClick={(name) => { setSelectedType(name); setDrawerOpen(true) }} />
        </div>
      )}

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={selectedTypeData?.name ?? ''}
      >
        {selectedTypeData && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge variant="default">{selectedTypeData.kind}</Badge>
            </div>
            <div>
              <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-2">Fields</p>
              <div className="space-y-1">
                {selectedTypeData.fields.map((field) => (
                  <div key={field} className="flex items-center gap-2 py-1.5 px-3 bg-surface rounded text-xs font-mono text-ivory">
                    <span className="text-copper-light">›</span>
                    {field}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Drawer>
    </motion.div>
  )
}
