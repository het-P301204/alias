interface Operation {
  id: number
  status: 'accepted' | 'rejected'
  label?: string
}

interface BatchTimelineProps {
  operations: Operation[]
  title?: string
}

export function BatchTimeline({ operations, title }: BatchTimelineProps) {
  return (
    <div>
      {title && (
        <p className="text-xs font-mono text-ivory-dim uppercase tracking-wider mb-3">{title}</p>
      )}
      <div className="space-y-2">
        {operations.map((op) => (
          <div key={op.id} className="flex items-center gap-3">
            <span className="text-xs font-mono text-ivory-dim w-6">{op.id}</span>
            <div className="flex-1 h-6 rounded overflow-hidden bg-surface">
              <div
                className="h-full rounded transition-all duration-500"
                style={{
                  width: '100%',
                  background: op.status === 'accepted' ? '#8EAA91' : '#B84D43',
                  opacity: 0.8,
                }}
              />
            </div>
            <span
              className="text-xs font-mono w-16"
              style={{ color: op.status === 'accepted' ? '#8EAA91' : '#D4625A' }}
            >
              {op.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
