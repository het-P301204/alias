import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'

interface DrawerProps {
  open: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  width?: number
}

export function Drawer({ open, onClose, title, children, width = 480 }: DrawerProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    if (open) document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-obsidian/60 z-40"
            aria-hidden="true"
          />
          <motion.div
            initial={{ x: width }}
            animate={{ x: 0 }}
            exit={{ x: width }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 h-full bg-graphite border-l border-border z-50 flex flex-col"
            style={{ width }}
            role="dialog"
            aria-modal="true"
            aria-label={title}
          >
            {title && (
              <div className="flex items-center justify-between px-5 py-4 border-b border-border">
                <h2 className="font-display text-lg text-ivory">{title}</h2>
                <button
                  onClick={onClose}
                  className="text-ivory-dim hover:text-ivory p-1 rounded transition-colors"
                  aria-label="Close drawer"
                >
                  <X size={18} />
                </button>
              </div>
            )}
            <div className="flex-1 overflow-auto p-5">{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
