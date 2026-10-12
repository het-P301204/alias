import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FlaskConical,
  Network,
  Users,
  Layers,
  GitBranch,
  Eye,
  Lock,
  Shield,
  History,
  Settings,
  ChevronRight,
  Zap,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/lab', icon: FlaskConical, label: 'Attack Lab' },
  { to: '/schema', icon: Network, label: 'Schema Explorer' },
  { to: '/alias', icon: Users, label: 'Alias Authorization' },
  { to: '/batching', icon: Layers, label: 'Batching & Rate Limits' },
  { to: '/complexity', icon: GitBranch, label: 'Query Complexity' },
  { to: '/blind-recovery', icon: Eye, label: 'Blind Schema Recovery' },
  { to: '/field-auth', icon: Lock, label: 'Field Authorization' },
  { to: '/defense', icon: Shield, label: 'Defense Center' },
  { to: '/experiments', icon: History, label: 'Experiments & Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

const breadcrumbMap: Record<string, string> = {
  '/': 'Overview',
  '/lab': 'Attack Lab',
  '/schema': 'Schema Explorer',
  '/alias': 'Alias Authorization',
  '/batching': 'Batching & Rate Limits',
  '/complexity': 'Query Complexity',
  '/blind-recovery': 'Blind Schema Recovery',
  '/field-auth': 'Field Authorization',
  '/defense': 'Defense Center',
  '/experiments': 'Experiments & Reports',
  '/settings': 'Settings',
}

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [mode] = useState<'vulnerable' | 'hardened'>('vulnerable')
  const currentPage = breadcrumbMap[location.pathname] ?? 'ALIAS'

  return (
    <div className="flex h-full bg-obsidian">
      {/* Sidebar */}
      <aside
        className="w-60 flex-shrink-0 flex flex-col border-r border-border bg-surface"
        style={{ width: 240 }}
      >
        {/* Logo */}
        <div className="flex items-center gap-2 px-5 py-4 border-b border-border">
          <div className="w-7 h-7 rounded bg-copper flex items-center justify-center">
            <Zap size={14} className="text-obsidian" />
          </div>
          <span className="font-display text-lg text-ivory tracking-wide">ALIAS</span>
          <span className="ml-auto text-xs text-ivory-dim font-mono">v1.0</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 overflow-y-auto" role="navigation" aria-label="Main navigation">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-5 py-2.5 text-sm transition-all duration-150 group relative
                ${isActive
                  ? 'text-ivory bg-graphite-light'
                  : 'text-ivory-dim hover:text-ivory hover:bg-graphite'
                }`
              }
              aria-label={label}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-4 bg-copper rounded-r" />
                  )}
                  <Icon size={15} className={isActive ? 'text-copper' : 'text-ivory-dim group-hover:text-ivory'} />
                  <span className="font-sans">{label}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom info */}
        <div className="px-5 py-3 border-t border-border">
          <p className="text-xs text-ivory-dim font-mono">GraphQL Security Lab</p>
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center gap-3 px-6 border-b border-border bg-surface h-12 flex-shrink-0">
          <div className="flex items-center gap-2 text-xs text-ivory-dim">
            <span className="text-ivory-dim">ALIAS</span>
            <ChevronRight size={12} />
            <span className="text-ivory font-medium">{currentPage}</span>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <span
              className={`px-2 py-0.5 rounded text-xs font-mono font-semibold uppercase tracking-wider
                ${mode === 'vulnerable'
                  ? 'bg-red/20 text-red-light border border-red/30'
                  : 'bg-sage/20 text-sage border border-sage/30'
                }`}
            >
              {mode}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto" role="main">
          {children}
        </main>
      </div>
    </div>
  )
}
