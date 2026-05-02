import { useState } from 'react'

export function LoginPage({ onLogin }: { onLogin: (user: any) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const DEMO_ACCOUNTS = [
    { email: 'admin@cortex-leman.com', password: 'C0rt3xL3m4n!', label: 'Admin', color: '--cyan' },
    { email: 'expert@dupont-comptable.fr', password: 'comptable', label: 'Comptable', color: '--emerald' },
    { email: 'avocat@martin-avocat.ch', password: 'avocat', label: 'Avocat', color: '--violet' },
    { email: 'medecin@hopital-geneve.ch', password: 'sante', label: 'Médecin', color: '--amber' },
    { email: 'analyste@ubank.ch', password: 'banque', label: 'Banquier', color: '--amber' },
    { email: 'cto@startup-paris.fr', password: 'startup', label: 'Startup', color: '--orange' },
    { email: 'drh@groupe-rh.fr', password: 'rh', label: 'RH', color: '--rose' },
  ]

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { auth } = await import('../lib/api')
      const res = await auth.login(email, password)
      if (res.access_token) localStorage.setItem('cl_access_token', res.access_token)
      onLogin(res.user || res)
    } catch (err: any) {
      setError(err.message || 'Identifiants invalides')
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = async (email: string, password: string) => {
    setEmail(email)
    setPassword(password)
    setError('')
    setLoading(true)
    try {
      const { auth } = await import('../lib/api')
      const res = await auth.login(email, password)
      if (res.access_token) localStorage.setItem('cl_access_token', res.access_token)
      onLogin(res.user || res)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
      {/* Background glow */}
      <div style={{ position: 'absolute', width: 400, height: 400, borderRadius: '50%', background: 'rgba(34,211,238,0.06)', filter: 'blur(80px)', top: '20%', left: '30%' }} />

      <div style={{ position: 'relative', zIndex: 1, width: '100%', maxWidth: 420, padding: '1.5rem' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{ width: 48, height: 48, borderRadius: '0.75rem', background: 'linear-gradient(135deg, var(--cyan), var(--emerald))', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: 700, color: 'var(--bg)' }}>CL</div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 700, marginTop: '0.75rem' }}>Cortex Leman v5</h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Infrastructure de Confiance IA — Connexion</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} style={{
          background: 'var(--bg-card-solid)', border: '1px solid var(--border)', borderRadius: '1rem', padding: '1.5rem',
        }}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.375rem' }}>EMAIL</label>
            <input
              type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="votre@email.com"
              style={{ width: '100%', padding: '0.625rem 0.75rem', borderRadius: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)', fontSize: '0.8125rem', outline: 'none' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', fontWeight: 600, display: 'block', marginBottom: '0.375rem' }}>MOT DE PASSE</label>
            <input
              type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{ width: '100%', padding: '0.625rem 0.75rem', borderRadius: '0.5rem', background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)', fontSize: '0.8125rem', outline: 'none' }}
            />
          </div>

          {error && <div style={{ padding: '0.5rem', borderRadius: '0.375rem', background: 'rgba(251,113,133,0.1)', border: '1px solid rgba(251,113,133,0.2)', color: 'var(--rose)', fontSize: '0.75rem', marginBottom: '1rem' }}>{error}</div>}

          <button type="submit" disabled={loading} style={{
            width: '100%', padding: '0.75rem', borderRadius: '0.5rem',
            background: loading ? 'var(--text-dim)' : 'var(--cyan)', color: 'var(--bg)',
            fontWeight: 700, fontSize: '0.875rem', border: 'none', cursor: loading ? 'not-allowed' : 'pointer',
          }}>
            {loading ? 'Connexion...' : 'Se connecter →'}
          </button>
        </form>

        {/* Demo accounts */}
        <div style={{ marginTop: '1.5rem' }}>
          <p style={{ fontSize: '0.6875rem', color: 'var(--text-dim)', textAlign: 'center', marginBottom: '0.75rem' }}>Comptes démo — clic rapide</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '0.5rem' }}>
            {DEMO_ACCOUNTS.map((a, i) => (
              <button key={i} onClick={() => quickLogin(a.email, a.password)} style={{
                padding: '0.5rem', borderRadius: '0.5rem', border: `1px solid var(${a.color})25`,
                background: `var(${a.color})08`, cursor: 'pointer', textAlign: 'center',
              }}>
                <div style={{ fontSize: '0.6875rem', fontWeight: 600, color: `var(${a.color})` }}>{a.label}</div>
                <div style={{ fontSize: '0.5625rem', color: 'var(--text-dim)', marginTop: '0.125rem' }}>{a.email.split('@')[0]}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
