import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '../../utils/cn'

interface MetricCardProps {
  label: string
  value: string | number
  trend?: 'up' | 'down' | 'flat'
  trendText?: string
  highlight?: boolean
  className?: string
  icon?: React.ReactNode
}

export function MetricCard({ label, value, trend, trendText, highlight, className, icon }: MetricCardProps) {
  return (
    <div
      className={cn(
        'bg-graphite border border-border rounded-lg p-4',
        highlight && 'border-copper/40',
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs text-ivory-dim font-sans uppercase tracking-wider mb-1">{label}</p>
        {icon && <span className="text-ivory-dim">{icon}</span>}
      </div>
      <p className="text-2xl font-display text-ivory">{value}</p>
      {(trend || trendText) && (
        <div className="flex items-center gap-1 mt-1">
          {trend === 'up' && <TrendingUp size={12} className="text-sage" />}
          {trend === 'down' && <TrendingDown size={12} className="text-red-light" />}
          {trend === 'flat' && <Minus size={12} className="text-ivory-dim" />}
          {trendText && (
            <span className="text-xs text-ivory-dim font-mono">{trendText}</span>
          )}
        </div>
      )}
    </div>
  )
}
