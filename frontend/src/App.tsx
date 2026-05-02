import { useState } from 'react'
import { useAuth } from './hooks/useAuth'
import { LandingPage } from './LandingPage'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { OnboardingPage } from './pages/OnboardingPage'

type Page = 'landing' | 'login' | 'onboarding' | 'dashboard'

export default function App() {
  const [page, setPage] = useState<Page>('landing')
  const [currentUser, setCurrentUser] = useState<any>(null)
  const { user, loading, logout } = useAuth()

  // If we have a real auth token, go to dashboard
  if (loading) return <div style={{ padding: '2rem', color: 'var(--text-dim)' }}>Chargement...</div>

  if (user && page !== 'dashboard') {
    return <DashboardPage user={user} onLogout={() => { logout(); setPage('landing') }} />
  }

  switch (page) {
    case 'login':
      return (
        <LoginPage
          onLogin={(u) => { setCurrentUser(u); setPage('dashboard') }}
        />
      )
    case 'onboarding':
      return (
        <OnboardingPage
          onComplete={async (result) => {
            // Auto-login after onboarding
            try {
              const { apiFetch } = await import('./hooks/useApi')
              const loginRes = await apiFetch('/api/v1/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email: result.email || result.identity?.email, password: '' }),
              })
              if (loginRes.access_token) {
                localStorage.setItem('cl_access_token', loginRes.access_token)
              }
            } catch { /* fallback: use result directly */ }
            setCurrentUser(result)
            setPage('dashboard')
          }}
        />
      )
    case 'dashboard':
      return (
        <DashboardPage
          user={currentUser || { email: 'demo@cortex-leman.com', role: 'admin', primary_vertical: 'comptable' }}
          onLogout={() => { setCurrentUser(null); setPage('landing') }}
        />
      )
    default:
      return (
        <LandingPage
          onLogin={() => setPage('login')}
          onStartOnboarding={() => setPage('onboarding')}
        />
      )
  }
}
