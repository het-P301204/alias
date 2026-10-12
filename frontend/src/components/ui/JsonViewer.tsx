interface JsonViewerProps {
  data: unknown
  maxHeight?: number | string
  label?: string
}

function syntaxHighlight(json: string): string {
  return json.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = 'color: #D5A45B' // number
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'color: #8EAA91' // key
        } else {
          cls = 'color: #D4966A' // string
        }
      } else if (/true|false/.test(match)) {
        cls = 'color: #B97853'
      } else if (/null/.test(match)) {
        cls = 'color: #C8C2B8'
      }
      return `<span style="${cls}">${match}</span>`
    }
  )
}

export function JsonViewer({ data, maxHeight = 400, label }: JsonViewerProps) {
  const json = JSON.stringify(data, null, 2)
  const highlighted = syntaxHighlight(json)

  return (
    <div className="rounded-lg overflow-hidden border border-border">
      {label && (
        <div className="px-3 py-1.5 bg-surface border-b border-border">
          <span className="text-xs text-ivory-dim font-mono">{label}</span>
        </div>
      )}
      <pre
        className="p-4 overflow-auto text-xs font-mono leading-relaxed bg-obsidian text-ivory"
        style={{ maxHeight }}
        dangerouslySetInnerHTML={{ __html: highlighted }}
      />
    </div>
  )
}
