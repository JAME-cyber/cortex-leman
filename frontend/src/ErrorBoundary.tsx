import { Component, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { error: Error | null }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: '2rem', background: '#020617', color: '#f1f5f9', minHeight: '100vh', fontFamily: 'monospace' }}>
          <h1 style={{ color: '#fb7185', fontSize: '1.25rem', marginBottom: '1rem' }}>❌ Erreur Runtime</h1>
          <pre style={{ background: '#0f172a', padding: '1rem', borderRadius: '0.5rem', overflow: 'auto', fontSize: '0.8125rem', border: '1px solid #1e293b' }}>
            {this.state.error.message}
          </pre>
          <p style={{ marginTop: '1rem', color: '#94a3b8', fontSize: '0.8125rem' }}>
            {this.state.error.stack?.split('\n').slice(1, 6).join('\n')}
          </p>
          <button onClick={() => { this.setState({ error: null }); window.location.reload() }}
            style={{ marginTop: '1rem', padding: '0.5rem 1rem', borderRadius: '0.375rem', background: '#22d3ee', color: '#020617', border: 'none', cursor: 'pointer', fontWeight: 600 }}>
            Recharger
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
