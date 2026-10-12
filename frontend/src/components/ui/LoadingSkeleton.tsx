import { cn } from '../../utils/cn'

interface LoadingSkeletonProps {
  className?: string
  lines?: number
  height?: number
}

export function LoadingSkeleton({ className, lines = 1, height = 20 }: LoadingSkeletonProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn('animate-pulse bg-graphite-light rounded', className)}
          style={{ height }}
        />
      ))}
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="bg-graphite border border-border rounded-lg p-5 space-y-3">
      <div className="animate-pulse bg-graphite-light rounded h-5 w-3/4" />
      <div className="animate-pulse bg-graphite-light rounded h-4 w-1/2" />
      <div className="animate-pulse bg-graphite-light rounded h-4 w-full" />
    </div>
  )
}
