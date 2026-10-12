import type { LabMode } from '../../services/api'

interface ModeToggleProps {
  mode: LabMode
  onChange: (mode: LabMode) => void
}

export function ModeToggle({ mode, onChange }: ModeToggleProps) {
  return (
    <div
      className="inline-flex rounded border border-border overflow-hidden"
      role="group"
      aria-label="Lab mode toggle"
    >
      <button
        onClick={() => onChange('vulnerable')}
        className={`px-4 py-1.5 text-xs font-mono font-semibold uppercase tracking-wider transition-all ${
          mode === 'vulnerable'
            ? 'bg-red/20 text-red-light border-r border-red/30'
            : 'text-ivory-dim hover:text-ivory bg-graphite border-r border-border'
        }`}
        aria-pressed={mode === 'vulnerable'}
      >
        Vulnerable
      </button>
      <button
        onClick={() => onChange('hardened')}
        className={`px-4 py-1.5 text-xs font-mono font-semibold uppercase tracking-wider transition-all ${
          mode === 'hardened'
            ? 'bg-sage/20 text-sage'
            : 'text-ivory-dim hover:text-ivory bg-graphite'
        }`}
        aria-pressed={mode === 'hardened'}
      >
        Hardened
      </button>
    </div>
  )
}
