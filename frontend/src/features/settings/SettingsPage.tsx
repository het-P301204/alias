import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, ChevronUp, Terminal, Book, Wrench, AlertTriangle } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'

const SCENARIOS = [
  {
    id: 'introspection',
    title: 'Schema Introspection',
    description: 'GraphQL introspection allows querying the API\'s own schema. In production, this can expose the full API structure to attackers, revealing all types, fields, mutations, and their relationships — enabling highly targeted attacks.',
    cve: null,
    fix: 'Disable introspection in production: set introspection=False in your server config.',
  },
  {
    id: 'alias-authorization',
    title: 'Alias Authorization',
    description: 'GraphQL aliases allow renaming query fields. An attacker can use multiple aliases to access multiple resources in a single request, bypassing per-query rate limits and sometimes per-resource authorization checks.',
    cve: null,
    fix: 'Validate authorization for each aliased field independently. Limit total aliases per request.',
  },
  {
    id: 'batching',
    title: 'Query Batching',
    description: 'GraphQL supports batching multiple operations in one HTTP request. Without limits, attackers can use batching to brute-force, enumerate, or overwhelm backends with a single request.',
    cve: null,
    fix: 'Enforce a max batch size (e.g., 3 operations per request). Log and alert on high-batch requests.',
  },
  {
    id: 'query-complexity',
    title: 'Query Complexity & Depth',
    description: 'Deeply nested GraphQL queries can trigger N+1 database calls, causing CPU and memory exhaustion (DoS). Without complexity analysis, a single request can overwhelm a production service.',
    cve: null,
    fix: 'Use a complexity analysis library. Set max_depth and max_complexity thresholds. Reject queries over budget.',
  },
  {
    id: 'blind-recovery',
    title: 'Blind Schema Recovery',
    description: 'GraphQL field suggestion errors ("Did you mean ...?") leak field names even when introspection is disabled. By fuzzing field names, attackers reconstruct the schema one field at a time.',
    cve: null,
    fix: 'Suppress field suggestions in errors. Return generic "Field not found" messages in production.',
  },
  {
    id: 'field-authorization',
    title: 'Field Authorization',
    description: 'GraphQL resolves each field independently. Without field-level authorization, a resolver may return sensitive data (e.g., SSN, salary) to callers who should not have access, even if the parent type is correctly authorized.',
    cve: null,
    fix: 'Implement field-level RBAC using a directive or resolver middleware. Test every sensitive field.',
  },
]

const TROUBLESHOOTING = [
  {
    problem: 'Backend returns 502 or CORS error',
    solution: 'Start the backend: cd backend && uvicorn alias_core.main:app --reload --port 8000. Ensure CORS allows http://localhost:5173.',
  },
  {
    problem: 'Scenarios show empty or no data',
    solution: 'Check that the database is seeded: python -m alias_core.database.init_db. Sample data is pre-loaded automatically.',
  },
  {
    problem: 'Monaco editor not loading',
    solution: 'Check for ad-blockers or CSP headers blocking cdn.jsdelivr.net. Try hard-refreshing (Ctrl+Shift+R).',
  },
  {
    problem: 'Experiment stuck in "running" state',
    solution: 'Cancel the experiment using the cancel button, or restart the backend. Check backend logs for timeout errors.',
  },
]

function Accordion({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between px-4 py-3 bg-graphite hover:bg-graphite-light transition-colors"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className="text-sm font-medium text-ivory">{title}</span>
        {open ? <ChevronUp size={15} className="text-ivory-dim" /> : <ChevronDown size={15} className="text-ivory-dim" />}
      </button>
      {open && (
        <div className="px-4 py-3 bg-surface border-t border-border">
          {children}
        </div>
      )}
    </div>
  )
}

export default function SettingsPage() {
  const [backendUrl, setBackendUrl] = useState('http://127.0.0.1:8000')

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="p-6 space-y-8 max-w-4xl"
    >
      <div>
        <h1 className="font-display text-2xl text-ivory">Settings & Documentation</h1>
        <p className="text-sm text-ivory-dim mt-1">Configure ALIAS and learn about each attack scenario</p>
      </div>

      {/* Backend URL */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3 flex items-center gap-2">
          <Wrench size={14} />
          Configuration
        </h2>
        <Card>
          <label className="block text-xs font-mono text-ivory-dim uppercase tracking-wider mb-2">
            Backend URL
          </label>
          <div className="flex gap-2">
            <input
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              className="flex-1 bg-surface border border-border rounded px-3 py-2 text-sm text-ivory font-mono focus:border-copper outline-none"
              aria-label="Backend URL"
            />
            <Button variant="secondary" onClick={() => window.location.reload()}>
              Apply
            </Button>
          </div>
          <p className="text-xs text-ivory-dim mt-2">Default: http://127.0.0.1:8000</p>
        </Card>
      </section>

      {/* First-run guide */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3 flex items-center gap-2">
          <Book size={14} />
          First-Run Guide
        </h2>
        <Card>
          <ol className="space-y-3">
            {[
              'Clone the ALIAS repository: git clone https://github.com/het-P301204/alias',
              'Install Python dependencies: cd backend && pip install -r requirements.txt',
              'Seed the database: python -m alias_core.database.init_db',
              'Start the backend: uvicorn alias_core.main:app --reload --port 8000',
              'Install frontend dependencies: cd frontend && npm install',
              'Start the frontend: npm run dev',
              'Open http://localhost:5173 in your browser',
              'Navigate to Attack Lab → select a scenario → click Run Experiment',
            ].map((step, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="w-6 h-6 rounded-full bg-copper/20 text-copper flex items-center justify-center text-xs font-mono flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span className="text-ivory-dim">{step}</span>
              </li>
            ))}
          </ol>
        </Card>
      </section>

      {/* CLI docs */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3 flex items-center gap-2">
          <Terminal size={14} />
          CLI Reference
        </h2>
        <Card>
          <p className="text-xs text-ivory-dim mb-3">Run experiments directly from the terminal using the ALIAS CLI:</p>
          <div className="space-y-3">
            {[
              { cmd: 'python -m alias_cli run --scenario introspection --mode vulnerable', desc: 'Run a scenario in vulnerable mode' },
              { cmd: 'python -m alias_cli run --scenario all --mode hardened', desc: 'Run all scenarios in hardened mode' },
              { cmd: 'python -m alias_cli list --status completed', desc: 'List completed experiments' },
              { cmd: 'python -m alias_cli report --id <experiment-id> --format html', desc: 'Export a report as HTML' },
            ].map(({ cmd, desc }) => (
              <div key={cmd}>
                <p className="text-xs text-ivory-dim mb-1">{desc}</p>
                <pre className="bg-obsidian border border-border rounded px-3 py-2 text-xs font-mono text-ivory-dim overflow-x-auto">
                  <code>{cmd}</code>
                </pre>
              </div>
            ))}
          </div>
        </Card>
      </section>

      {/* Architecture */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3">Architecture</h2>
        <Card>
          <pre className="text-xs font-mono text-ivory-dim leading-loose overflow-x-auto">
{`┌─────────────────────────────────────────────────────────────────┐
│                         ALIAS Platform                          │
├──────────────────────┬──────────────────────────────────────────┤
│   React Frontend     │           FastAPI Backend                │
│   (port 5173)        │           (port 8000)                    │
│                      │                                          │
│  ┌──────────────┐    │  ┌───────────────────────────────┐      │
│  │  11 Pages    │◄───┼──│  /api/experiments             │      │
│  │  Attack Lab  │    │  │  /api/scenarios                │      │
│  │  Defense Ctr │    │  │  /api/defenses                 │      │
│  │  Schema Exp  │    │  │  /api/reports                  │      │
│  └──────────────┘    │  └──────────────────┬────────────┘      │
│                      │                     │                    │
│  ┌──────────────┐    │  ┌──────────────────▼────────────┐      │
│  │ TanStack     │    │  │  Scenario Engine               │      │
│  │ Query Cache  │    │  │  (6 attack modules)            │      │
│  └──────────────┘    │  └──────────────────┬────────────┘      │
│                      │                     │                    │
│                      │  ┌──────────────────▼────────────┐      │
│                      │  │  SQLite / Demo Database        │      │
│                      │  │  (sample users, orders)        │      │
│                      │  └───────────────────────────────┘      │
└──────────────────────┴──────────────────────────────────────────┘`}
          </pre>
        </Card>
      </section>

      {/* Scenario guides */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3">Scenario Guides</h2>
        <div className="space-y-2">
          {SCENARIOS.map((s) => (
            <Accordion key={s.id} title={s.title}>
              <p className="text-xs text-ivory-dim leading-relaxed mb-3">{s.description}</p>
              <div className="bg-obsidian rounded p-3 border border-border">
                <p className="text-xs font-mono text-sage uppercase tracking-wider mb-1">Mitigation</p>
                <p className="text-xs text-ivory-dim">{s.fix}</p>
              </div>
            </Accordion>
          ))}
        </div>
      </section>

      {/* Troubleshooting */}
      <section>
        <h2 className="font-mono text-sm text-ivory-dim uppercase tracking-wider mb-3 flex items-center gap-2">
          <AlertTriangle size={14} />
          Troubleshooting
        </h2>
        <div className="space-y-2">
          {TROUBLESHOOTING.map((item) => (
            <Accordion key={item.problem} title={item.problem}>
              <p className="text-xs text-ivory-dim">{item.solution}</p>
            </Accordion>
          ))}
        </div>
      </section>
    </motion.div>
  )
}
