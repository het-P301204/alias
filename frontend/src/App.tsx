import { AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import Layout from './app/Layout'
import AppRouter from './app/router'

export default function App() {
  const location = useLocation()

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <AppRouter key={location.pathname} />
      </AnimatePresence>
    </Layout>
  )
}
