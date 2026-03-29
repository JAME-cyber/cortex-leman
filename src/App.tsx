import Navbar from './components/Navbar'
import Hero from './components/Hero'
import BentoGrid from './components/BentoGrid'
import Methodology from './components/Methodology'
import TrustSecurity from './components/TrustSecurity'
import Footer from './components/Footer'

export default function App() {
  return (
    <div className="min-h-screen bg-surface text-text-primary font-sans antialiased">
      <Navbar />
      <main>
        <Hero />
        <BentoGrid />
        <Methodology />
        <TrustSecurity />
      </main>
      <Footer />
    </div>
  )
}
