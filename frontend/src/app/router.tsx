import { Routes, Route } from 'react-router-dom'
import OverviewPage from '../features/overview/OverviewPage'
import AttackLabPage from '../features/attack-lab/AttackLabPage'
import SchemaExplorerPage from '../features/introspection/SchemaExplorerPage'
import AliasAuthPage from '../features/alias-auth/AliasAuthPage'
import BatchingPage from '../features/batching/BatchingPage'
import QueryComplexityPage from '../features/query-complexity/QueryComplexityPage'
import BlindRecoveryPage from '../features/blind-recovery/BlindRecoveryPage'
import FieldAuthPage from '../features/field-auth/FieldAuthPage'
import DefenseCenterPage from '../features/defense-center/DefenseCenterPage'
import ExperimentsPage from '../features/experiments/ExperimentsPage'
import SettingsPage from '../features/settings/SettingsPage'

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<OverviewPage />} />
      <Route path="/lab" element={<AttackLabPage />} />
      <Route path="/schema" element={<SchemaExplorerPage />} />
      <Route path="/alias" element={<AliasAuthPage />} />
      <Route path="/batching" element={<BatchingPage />} />
      <Route path="/complexity" element={<QueryComplexityPage />} />
      <Route path="/blind-recovery" element={<BlindRecoveryPage />} />
      <Route path="/field-auth" element={<FieldAuthPage />} />
      <Route path="/defense" element={<DefenseCenterPage />} />
      <Route path="/experiments" element={<ExperimentsPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  )
}
