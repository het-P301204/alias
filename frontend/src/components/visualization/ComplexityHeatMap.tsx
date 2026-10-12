import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface FieldCost {
  name: string
  cost: number
}

interface ComplexityHeatMapProps {
  fields: FieldCost[]
  budget?: number
}

function getCostColor(cost: number, max: number): string {
  const ratio = cost / max
  if (ratio < 0.33) return '#8EAA91'  // sage
  if (ratio < 0.66) return '#D5A45B'  // amber
  return '#B84D43'                     // red
}

export function ComplexityHeatMap({ fields, budget = 100 }: ComplexityHeatMapProps) {
  const max = Math.max(...fields.map((f) => f.cost), 1)

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs text-ivory-dim font-mono uppercase tracking-wider">Field Cost Distribution</span>
        <span className="text-xs font-mono text-ivory-dim">Budget: {budget}</span>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={fields} layout="vertical" margin={{ left: 60, right: 20 }}>
          <XAxis type="number" tick={{ fill: '#C8C2B8', fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: '#C8C2B8', fontSize: 10, fontFamily: 'JetBrains Mono' }}
            width={60}
          />
          <Tooltip
            contentStyle={{
              background: '#282624',
              border: '1px solid #3A3530',
              borderRadius: 4,
              color: '#F5F0E8',
              fontSize: 11,
              fontFamily: 'JetBrains Mono',
            }}
            formatter={(val: number) => [val, 'Cost']}
          />
          <Bar dataKey="cost" radius={[0, 3, 3, 0]}>
            {fields.map((f, i) => (
              <Cell key={i} fill={getCostColor(f.cost, max)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="flex gap-4 mt-3 justify-end">
        {[
          { color: '#8EAA91', label: 'Low' },
          { color: '#D5A45B', label: 'Medium' },
          { color: '#B84D43', label: 'High' },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-3 h-2 rounded-sm" style={{ background: color }} />
            <span className="text-xs text-ivory-dim">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
