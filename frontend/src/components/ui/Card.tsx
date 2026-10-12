import { cn } from '../../utils/cn'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'sm' | 'md' | 'lg' | 'none'
  hover?: boolean
  onClick?: () => void
}

const paddingStyles = {
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-6',
  none: '',
}

export function Card({ children, className, padding = 'md', hover, onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-graphite border border-border rounded-lg',
        paddingStyles[padding],
        hover && 'transition-all duration-150 hover:border-copper/50 hover:scale-[1.01] cursor-pointer',
        className
      )}
    >
      {children}
    </div>
  )
}
