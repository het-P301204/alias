import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  BackgroundVariant,
} from 'reactflow'
import 'reactflow/dist/style.css'

interface SchemaType {
  name: string
  kind: 'QUERY' | 'MUTATION' | 'OBJECT' | 'ENUM' | 'SCALAR' | 'INPUT' | string
  fields?: string[]
}

interface SchemaGraphProps {
  types: SchemaType[]
  onTypeClick?: (typeName: string) => void
}

const kindColors: Record<string, string> = {
  QUERY: '#B97853',
  MUTATION: '#D4625A',
  OBJECT: '#8EAA91',
  ENUM: '#D5A45B',
  SCALAR: '#C8C2B8',
  INPUT: '#8EAA91',
}

function buildNodes(types: SchemaType[]): Node[] {
  const cols = Math.ceil(Math.sqrt(types.length))
  return types.map((t, i) => ({
    id: t.name,
    position: {
      x: (i % cols) * 200,
      y: Math.floor(i / cols) * 120,
    },
    data: {
      label: (
        <div className="text-xs font-mono">
          <div className="font-semibold" style={{ color: kindColors[t.kind] ?? '#C8C2B8' }}>
            {t.name}
          </div>
          <div className="text-[10px] opacity-60 mt-0.5">{t.kind}</div>
        </div>
      ),
    },
    style: {
      background: '#282624',
      border: `1px solid ${kindColors[t.kind] ?? '#3A3530'}`,
      borderRadius: 6,
      color: '#F5F0E8',
      fontSize: 11,
      padding: '8px 12px',
      minWidth: 120,
    },
  }))
}

function buildEdges(types: SchemaType[]): Edge[] {
  const edges: Edge[] = []
  const typeNames = new Set(types.map((t) => t.name))
  types.forEach((t) => {
    t.fields?.forEach((field, fi) => {
      const clean = field.replace(/[![\]]/g, '').trim()
      if (typeNames.has(clean) && clean !== t.name) {
        edges.push({
          id: `${t.name}-${clean}-${fi}`,
          source: t.name,
          target: clean,
          style: { stroke: '#3A3530', strokeWidth: 1 },
          animated: false,
        })
      }
    })
  })
  return edges
}

export function SchemaGraph({ types, onTypeClick }: SchemaGraphProps) {
  const [nodes, , onNodesChange] = useNodesState(buildNodes(types))
  const [edges, , onEdgesChange] = useEdgesState(buildEdges(types))

  return (
    <div style={{ height: 500 }} className="rounded-lg overflow-hidden border border-border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(_, node) => onTypeClick?.(node.id)}
        fitView
        attributionPosition="bottom-right"
      >
        <Background variant={BackgroundVariant.Dots} color="#3A3530" gap={20} />
        <Controls
          style={{ background: '#282624', border: '1px solid #3A3530' }}
        />
        <MiniMap
          style={{ background: '#1E1C1A', border: '1px solid #3A3530' }}
          nodeColor={(node) => {
            const kind = (node.data as { label: React.ReactElement })?.label?.props?.children?.[0]?.props?.style?.color
            return kind ?? '#3A3530'
          }}
        />
      </ReactFlow>
    </div>
  )
}
