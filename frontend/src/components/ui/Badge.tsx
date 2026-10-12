import { cn } from '../../utils/cn'

type Variant =
  | 'vulnerable'
  | 'hardened'
  | 'ready'
  | 'validating'
  | 'running'
  | 'analyzing'
  | 'completed'
  | 'failed'
  | 'timeout'
  | 'cancelled'
  | 'sample'
  | 'default'
  | 'beginner'
  | 'intermediate'
  | 'advanced'

interface BadgeProps {
  variant?: Variant
  children: React.ReactNode
  className?: string
  pulse?: boolean
}

const variantStyles: Record<Variant, string> = {
  vulnerable: 'bg-red/20 text-red-light border-red/30',
  hardened: 'bg-sage/20 text-sage border-sage/30',
  ready: 'bg-graphite text-ivory-dim border-border',
  validating: 'bg-amber/20 text-amber border-amber/30',
  running: 'bg-copper/20 text-copper-light border-copper/30',
  analyzing: 'bg-amber/20 text-amber border-amber/30',
  completed: 'bg-sage/20 text-sage border-sage/30',
  failed: 'bg-red/20 text-red-light border-red/30',
  timeout: 'bg-red/20 text-red-light border-red/30',
  cancelled: 'bg-graphite text-ivory-dim border-border',
  sample: 'bg-copper/10 text-copper border-copper/20',
  default: 'bg-graphite text-ivory-dim border-border',
  beginner: 'bg-sage/20 text-sage border-sage/30',
  intermediate: 'bg-amber/20 text-amber border-amber/30',
  advanced: 'bg-red/20 text-red-light border-red/30',
}

export function Badge({ variant = 'default', children, className, pulse }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium uppercase tracking-wider border',
        variantStyles[variant],
        pulse && 'status-pulse',
        className
      )}
    >
      {children}
    </span>
  )
}
