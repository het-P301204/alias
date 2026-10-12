import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, RefreshCw, Clock } from 'lucide-react'
import { useDefenses, useVerifyDefense } from '../../hooks/useApi'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { CardSkeleton } from '../../components/ui/LoadingSkeleton'

const DEFAULT_CONTROLS = [
  {
    control_id: 'introspection-disable',
    title: 'Introspection Disabled',
    description: 'Prevents schema enumeration by disabling the __schema and __type queries.',
    scenario_id: 'introspection',
    vulnerable_behavior: 'Returns full schema including all types, fields, and relationships',
    hardened_behavior: 'Returns error: "Introspection is not allowed in this environment"',
    config: { disabled: true },
    last_verified: null,
    last_result: null,
  },
  {
    control_id: 'alias-depth-limit',
    title: 'Alias Count Limit',
    description: 'Limits the number of aliases per query to prevent IDOR via alias batching.',
    scenario_id: 'alias-authorization',
    vulnerable_behavior: 'Allows unlimited aliases; authorization checked only on first alias',
    hardened_behavior: 'Rejects queries with more than 5 aliases per operation',
    config: { max_aliases: 5 },
    last_verified: null,
    last_result: null,
  },
  {
    control_id: 'batch-rate-limit',
    title: 'Operation Batch Limit',
    description: 'Enforces a maximum of 3 batched operations per HTTP request.',
    scenario_id: 'batching',
    vulnerable_behavior: 'Executes all batched operations without limit',
    hardened_behavior: 'Rejects batched requests with more than 3 operations',
    config: { max_batch_size: 3 },
    last_verified: null,
    last_result: null,
  },
  {
    control_id: 'complexity-budget',
    title: 'Query Complexity Budget',
    description: 'Rejects queries that exceed a complexity score of 100.',
    scenario_id: 'query-complexity',
    vulnerable_behavior: 'Executes queries of any depth and complexity',
    hardened_behavior: 'Rejects queries with complexity score > 100',
    config: { max_complexity: 100, max_depth: 6 },
    last_verified: null,
    last_result: null,
  },
  {
    control_id: 'suggestion-suppression',
    title: 'Error Suggestion Suppression',
    description: 'Strips "Did you mean...?" suggestions from GraphQL error responses.',
    scenario_id: 'blind-recovery',
    vulnerable_behavior: 'Includes field name suggestions in error messages',
    hardened_behavior: 'Returns generic "Field not found" without suggestions',
    config: { suppress_suggestions: true },
    last_verified: null,
    last_result: null,
  },
  {
    control_id: 'field-auth-enforcement',
    title: 'Field-Level Authorization',
    description: 'Enforces per-field RBAC — sensitive fields require appropriate role.',
    scenario_id: 'field-authorization',
    vulnerable_behavior: 'Returns all fields regardless of caller role',
    hardened_behavior: 'Null-masks or errors unauthorized field accesses per role',
    config: { enforce_field_auth: true },
    last_verified: null,
    last_result: null,
  },
]

export default function DefenseCenterPage() {
  const { data: controls, isLoading } = useDefenses()
  const verifyMutation = useVerifyDefense()
  const [verifyResults, setVerifyResults] = useState<Record<string, { verified: boolean; ts: string }>>({})
  const [verifyingId, setVerifyingId] = useState<string | null>(null)

  const displayed = controls ?? DEFAULT_CONTROLS

  const handleVerify = async (id: string) => {
    setVerifyingId(id)
    try {
      const result = await verifyMutation.mutateAsync(id)
      setVerifyResults((prev) => ({
        ...prev,
        [id]: { verified: result.verified, ts: new Date().toLocaleTimeString() },
      }))
    } catch {
      setVerifyResults((prev) => ({
        ...prev,
        [id]: { verified: false, ts: new Date().toLocaleTimeString() },
      }))
    } finally {
      setVerifyingId(null)
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
        <h1 className="font-display text-2xl text-ivory">Defense Center</h1>
        <p className="text-sm text-ivory-dim mt-1">Verify defensive controls across all 6 attack scenarios</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {displayed.map((control) => {
            const verifyResult = verifyResults[control.control_id]
            const isVerifying = verifyingId === control.control_id

            return (
              <Card key={control.control_id} className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-xs font-mono text-copper uppercase tracking-wider mb-1">
                      {control.scenario_id}
                    </p>
                    <h3 className="font-display text-lg text-ivory">{control.title}</h3>
                  </div>
                  {verifyResult && (
                    <Badge variant={verifyResult.verified ? 'hardened' : 'vulnerable'}>
                      {verifyResult.verified ? '✓ Pass' : '✗ Fail'}
                    </Badge>
                  )}
                </div>

                <p className="text-xs text-ivory-dim leading-relaxed">{control.description}</p>

                {/* Config values */}
                <div className="bg-surface rounded p-3">
                  <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-1.5">Config</p>
                  {Object.entries(control.config).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-xs font-mono">
                      <span className="text-ivory-dim">{k}</span>
                      <span className="text-amber">{String(v)}</span>
                    </div>
                  ))}
                </div>

                {/* Behavior comparison */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-red/5 border border-red/20 rounded">
                    <p className="text-xs font-mono text-red-light uppercase tracking-wider mb-1.5">Vulnerable</p>
                    <p className="text-xs text-ivory-dim leading-relaxed">{control.vulnerable_behavior}</p>
                  </div>
                  <div className="p-3 bg-sage/5 border border-sage/20 rounded">
                    <p className="text-xs font-mono text-sage uppercase tracking-wider mb-1.5">Hardened</p>
                    <p className="text-xs text-ivory-dim leading-relaxed">{control.hardened_behavior}</p>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center gap-1.5 text-xs font-mono text-ivory-dim">
                    <Clock size={12} />
                    {verifyResult ? `Last check: ${verifyResult.ts}` : 'Never verified'}
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleVerify(control.control_id)}
                    loading={isVerifying}
                    aria-label={`Verify ${control.title}`}
                  >
                    <RefreshCw size={12} />
                    Verify Now
                  </Button>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </motion.div>
  )
}
