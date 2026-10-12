import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, CheckCircle, XCircle, Minus } from 'lucide-react'
import { useExperimentRunner } from '../../hooks/useExperiment'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ModeToggle } from '../../components/ui/ModeToggle'
import { StatusIndicator } from '../../components/ui/StatusIndicator'
import type { LabMode } from '../../services/api'

type Role = 'GUEST' | 'CUSTOMER' | 'STAFF' | 'ADMIN'

const ROLES: Role[] = ['GUEST', 'CUSTOMER', 'STAFF', 'ADMIN']

const FIELDS = [
  { name: 'id', sensitive: false },
  { name: 'name', sensitive: false },
  { name: 'email', sensitive: false },
  { name: 'phone', sensitive: true },
  { name: 'address', sensitive: true },
  { name: 'ssn', sensitive: true },
  { name: 'creditCard', sensitive: true },
  { name: 'role', sensitive: false },
  { name: 'internalNotes', sensitive: true },
  { name: 'salary', sensitive: true },
  { name: 'apiKey', sensitive: true },
  { name: 'auditTrail', sensitive: false },
]

type Permission = 'allowed' | 'denied' | 'na'

const EXPECTED_MATRIX: Record<Role, Record<string, Permission>> = {
  GUEST: {
    id: 'allowed', name: 'allowed', email: 'denied', phone: 'denied', address: 'denied',
    ssn: 'denied', creditCard: 'denied', role: 'denied', internalNotes: 'denied',
    salary: 'denied', apiKey: 'denied', auditTrail: 'denied',
  },
  CUSTOMER: {
    id: 'allowed', name: 'allowed', email: 'allowed', phone: 'allowed', address: 'allowed',
    ssn: 'denied', creditCard: 'allowed', role: 'allowed', internalNotes: 'denied',
    salary: 'denied', apiKey: 'denied', auditTrail: 'denied',
  },
  STAFF: {
    id: 'allowed', name: 'allowed', email: 'allowed', phone: 'allowed', address: 'allowed',
    ssn: 'denied', creditCard: 'denied', role: 'allowed', internalNotes: 'allowed',
    salary: 'denied', apiKey: 'denied', auditTrail: 'allowed',
  },
  ADMIN: {
    id: 'allowed', name: 'allowed', email: 'allowed', phone: 'allowed', address: 'allowed',
    ssn: 'allowed', creditCard: 'allowed', role: 'allowed', internalNotes: 'allowed',
    salary: 'allowed', apiKey: 'allowed', auditTrail: 'allowed',
  },
}

const VULNERABLE_MATRIX: Record<Role, Record<string, Permission>> = {
  ...EXPECTED_MATRIX,
  CUSTOMER: {
    ...EXPECTED_MATRIX.CUSTOMER,
    ssn: 'allowed',
  },
}

function PermCell({ perm, isVuln }: { perm: Permission; isVuln?: boolean }) {
  if (perm === 'na') return <Minus size={13} className="text-ivory-dim opacity-40 mx-auto" />
  if (perm === 'allowed') return <CheckCircle size={14} className={`mx-auto ${isVuln ? 'text-red-light' : 'text-sage'}`} />
  return <XCircle size={14} className="text-ivory-dim opacity-50 mx-auto" />
}

export default function FieldAuthPage() {
  const [mode, setMode] = useState<LabMode>('vulnerable')
  const [selectedRole, setSelectedRole] = useState<Role>('CUSTOMER')
  const { experiment, isLoading, start } = useExperimentRunner()

  const matrix = mode === 'vulnerable' ? VULNERABLE_MATRIX : EXPECTED_MATRIX

  const handleRun = () => {
    start('field-authorization', mode, { role: selectedRole })
  }

  const roleColors: Record<Role, string> = {
    GUEST: '#C8C2B8',
    CUSTOMER: '#8EAA91',
    STAFF: '#D5A45B',
    ADMIN: '#D4625A',
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
        <h1 className="font-display text-2xl text-ivory">Field Authorization Lab</h1>
        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: '240px 1fr' }}>
        {/* Controls */}
        <div className="space-y-4">
          <Card>
            <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">Acting Role</p>
            <div className="space-y-2">
              {ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`w-full px-3 py-2.5 rounded border text-left transition-all text-sm font-mono
                    ${selectedRole === role ? 'border-copper/50 bg-copper/10 text-copper-light' : 'border-border bg-surface text-ivory-dim hover:text-ivory'}`}
                  aria-pressed={selectedRole === role}
                >
                  <span className="inline-block w-2 h-2 rounded-full mr-2" style={{ background: roleColors[role] }} />
                  {role}
                </button>
              ))}
            </div>
          </Card>

          <Button className="w-full" onClick={handleRun} loading={isLoading} aria-label="Run authorization test">
            <Play size={14} />
            Run Test
          </Button>

          {experiment && (
            <StatusIndicator status={experiment.status} error={experiment.error} />
          )}

          {mode === 'vulnerable' && (
            <Card className="border-red/30">
              <Badge variant="vulnerable" className="mb-2">Vulnerability Present</Badge>
              <p className="text-xs text-ivory-dim">
                CUSTOMER role can access the <span className="text-red-light font-mono">ssn</span> field — an authorization bypass.
              </p>
            </Card>
          )}

          {mode === 'hardened' && (
            <Card className="border-sage/30">
              <Badge variant="hardened" className="mb-2">Protected</Badge>
              <p className="text-xs text-ivory-dim">
                Field-level authorization enforced. All cells match expected permissions.
              </p>
            </Card>
          )}
        </div>

        {/* Permission matrix */}
        <Card padding="none" className="overflow-auto">
          <div className="px-4 py-2.5 border-b border-border">
            <span className="text-xs font-mono text-ivory-dim uppercase tracking-wider">Permission Matrix</span>
          </div>
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-2.5 text-left text-ivory-dim uppercase tracking-wider w-32">Field</th>
                {ROLES.map((role) => (
                  <th key={role} className="px-4 py-2.5 text-center uppercase tracking-wider">
                    <span style={{ color: roleColors[role] }}>{role}</span>
                  </th>
                ))}
                <th className="px-4 py-2.5 text-center text-ivory-dim uppercase tracking-wider">Sensitive</th>
              </tr>
            </thead>
            <tbody>
              {FIELDS.map((field) => {
                const isVulnerableRow =
                  mode === 'vulnerable' &&
                  field.name === 'ssn' &&
                  matrix.CUSTOMER?.[field.name] === 'allowed' &&
                  EXPECTED_MATRIX.CUSTOMER[field.name] === 'denied'

                return (
                  <tr
                    key={field.name}
                    className={`border-b border-border/50 ${isVulnerableRow ? 'bg-red/10' : ''}`}
                  >
                    <td className={`px-4 py-2.5 font-mono ${isVulnerableRow ? 'text-red-light font-semibold' : 'text-ivory'}`}>
                      {field.name}
                      {isVulnerableRow && <span className="ml-2 text-[10px] text-red-light">⚠</span>}
                    </td>
                    {ROLES.map((role) => {
                      const perm = matrix[role][field.name] as Permission
                      const isVuln = mode === 'vulnerable' && field.name === 'ssn' && role === 'CUSTOMER' && perm === 'allowed'
                      return (
                        <td key={role} className="px-4 py-2.5 text-center">
                          <PermCell perm={perm} isVuln={isVuln} />
                        </td>
                      )
                    })}
                    <td className="px-4 py-2.5 text-center">
                      {field.sensitive ? (
                        <span className="text-amber text-[10px]">●</span>
                      ) : (
                        <span className="text-ivory-dim opacity-30 text-[10px]">○</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          <div className="px-4 py-3 flex gap-4 text-xs text-ivory-dim">
            <span className="flex items-center gap-1.5"><CheckCircle size={12} className="text-sage" /> Allowed</span>
            <span className="flex items-center gap-1.5"><XCircle size={12} className="text-ivory-dim opacity-50" /> Denied</span>
            <span className="flex items-center gap-1.5"><CheckCircle size={12} className="text-red-light" /> Unauthorized Access</span>
          </div>
        </Card>
      </div>
    </motion.div>
  )
}
