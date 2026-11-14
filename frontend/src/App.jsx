import { useEffect, useRef, useState } from 'react'
import About from './pages/About'
import SettingsPage from './pages/Settings'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'

import {
  ShieldCheck,
  LayoutDashboard,
  Search,
  FileText,
  BrainCircuit,
  Settings,
  Bell,
  BellOff,
  ChevronDown,
  Menu,
  X,
  ChevronRight,
  Clock3,
  GitCompareArrows,
  Network,
  Sun,
  Moon,
  Contrast,
  Camera
} from 'lucide-react'

import DashboardPage from './pages/Dashboard'
import Analysis from './pages/Analysis'
import Results from './pages/Results'
import History from './pages/History'
import ExplainableAI from './pages/ExplainableAI'
import CompanyVerification from './pages/CompanyVerification'
import Compare from './pages/Compare'
import PatternIntelligence from './pages/PatternIntelligence'

const SETTINGS_KEY = 'offershield_user_settings'
const AVATAR_KEY = 'offershield_profile_avatar'
const THEME_KEY = 'offershield_theme'
const MONO_KEY = 'offershield_monochrome'
const NOTIFICATIONS_KEY = 'offershield_notifications_enabled'

function readStoredSettings() {
  try {
    const value = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}')
    return value && typeof value === 'object' ? value : {}
  } catch {
    return {}
  }
}

function readStoredBoolean(key, fallback) {
  const value = localStorage.getItem(key)
  if (value === null) return fallback
  return value === 'true'
}

const navigation = [
  { name: 'Overview', path: '/', icon: LayoutDashboard, section: 'WORKSPACE' },
  { name: 'Analyse opportunity', path: '/analyse', icon: Search, section: 'WORKSPACE' },
  { name: 'Analysis history', path: '/history', icon: Clock3, section: 'WORKSPACE' },
  { name: 'Compare Reports', path: '/compare', icon: GitCompareArrows, section: 'WORKSPACE' },
  { name: 'Explainable AI', path: '/explainable-ai', icon: BrainCircuit, section: 'INTELLIGENCE' },
  { name: 'Company Verification', path: '/company-verification', icon: ShieldCheck, section: 'INTELLIGENCE' },
  { name: 'Pattern Intelligence', path: '/patterns', icon: Network, section: 'INTELLIGENCE' },
  { name: 'About the platform', path: '/about', icon: FileText, section: 'INTELLIGENCE' }
]

function ComingSoon({ title, description, icon: Icon }) {
  return (
    <section className="coming-soon-page">
      <div className="coming-soon-icon"><Icon size={27} /></div>
      <span className="panel-overline">OFFER SHIELD INTELLIGENCE</span>
      <h1>{title}</h1>
      <p>{description}</p>
      <div className="coming-soon-status">
        <span className="coming-soon-dot" />
        This section is planned for a future update.
      </div>
    </section>
  )
}

function App() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [profile, setProfile] = useState(readStoredSettings)
  const [avatar, setAvatar] = useState(() => localStorage.getItem(AVATAR_KEY) || '')
  const [theme, setTheme] = useState(() => localStorage.getItem(THEME_KEY) || 'light')
  const [monochrome, setMonochrome] = useState(() => readStoredBoolean(MONO_KEY, false))
  const [notificationsEnabled, setNotificationsEnabled] = useState(
    () => readStoredBoolean(NOTIFICATIONS_KEY, true)
  )
  const avatarInputRef = useRef(null)

  const navigate = useNavigate()
  const location = useLocation()

  const activeItem = navigation.find(item => item.path === location.pathname)
  const activePage = location.pathname === '/results'
    ? 'Analysis Results'
    : location.pathname === '/settings'
      ? 'Settings'
      : activeItem?.name || 'Overview'

  function navigateTo(path) {
    navigate(path)
    setMenuOpen(false)
  }

  function syncProfile() {
    setProfile(readStoredSettings())
    setAvatar(localStorage.getItem(AVATAR_KEY) || '')
  }

  useEffect(() => {
    syncProfile()
  }, [location.pathname])

  useEffect(() => {
    const handleStorage = event => {
      if (!event.key || event.key === SETTINGS_KEY || event.key === AVATAR_KEY) syncProfile()
    }
    const handleProfileUpdate = () => syncProfile()
    window.addEventListener('storage', handleStorage)
    window.addEventListener('offershield:profile-updated', handleProfileUpdate)
    return () => {
      window.removeEventListener('storage', handleStorage)
      window.removeEventListener('offershield:profile-updated', handleProfileUpdate)
    }
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  useEffect(() => {
    document.documentElement.dataset.monochrome = String(monochrome)
    localStorage.setItem(MONO_KEY, String(monochrome))
  }, [monochrome])

  useEffect(() => {
    localStorage.setItem(NOTIFICATIONS_KEY, String(notificationsEnabled))
  }, [notificationsEnabled])

  function handleAvatarUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      window.alert('Please choose an image file.')
      event.target.value = ''
      return
    }

    if (file.size > 2 * 1024 * 1024) {
      window.alert('Please choose an image smaller than 2 MB.')
      event.target.value = ''
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const imageData = String(reader.result || '')
      try {
        localStorage.setItem(AVATAR_KEY, imageData)
        setAvatar(imageData)
        window.dispatchEvent(new Event('offershield:profile-updated'))
      } catch {
        window.alert('This image could not be saved. Please choose a smaller image.')
      }
      event.target.value = ''
    }
    reader.readAsDataURL(file)
  }

  const displayName = String(profile.displayName || profile.name || 'Student').trim() || 'Student'
  const displayRole = String(profile.role || 'Student').trim() || 'Student'
  const displayWorkspace = String(profile.workspace || 'Workspace').trim() || 'Workspace'
  const avatarInitial = displayName.charAt(0).toUpperCase()

  return (
    <div className={`app-shell ${monochrome ? 'monochrome-mode' : ''}`} data-theme={theme}>
      {menuOpen && (
        <button className="sidebar-backdrop" onClick={() => setMenuOpen(false)} aria-label="Close navigation menu" />
      )}

      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark"><ShieldCheck size={23} strokeWidth={2.2} /></div>
          <div className="brand-details">
            <h2>OfferShield</h2>
            <span>SECURITY INTELLIGENCE</span>
          </div>
          <button className="mobile-close" onClick={() => setMenuOpen(false)} aria-label="Close navigation">
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-navigation">
          <p className="sidebar-section-label">WORKSPACE</p>
          {navigation.filter(item => item.section === 'WORKSPACE').map(item => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <button key={item.path} className={`sidebar-nav-item ${isActive ? 'active' : ''}`} onClick={() => navigateTo(item.path)}>
                <Icon size={19} strokeWidth={1.9} />
                <span>{item.name}</span>
                {isActive && <span className="active-indicator" />}
              </button>
            )
          })}

          <p className="sidebar-section-label intelligence-label">INTELLIGENCE</p>
          {navigation.filter(item => item.section === 'INTELLIGENCE').map(item => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <button key={item.path} className={`sidebar-nav-item ${isActive ? 'active' : ''}`} onClick={() => navigateTo(item.path)}>
                <Icon size={19} strokeWidth={1.9} />
                <span>{item.name}</span>
                {isActive && <span className="active-indicator" />}
              </button>
            )
          })}
        </div>

        <div className="sidebar-bottom">
          <div className="sidebar-security-card">
            <div className="sidebar-security-icon"><ShieldCheck size={19} /></div>
            <div>
              <strong>Stay informed</strong>
              <p>Review opportunities before you apply.</p>
            </div>
          </div>

          <button
            className={`sidebar-nav-item settings-nav-item ${location.pathname === '/settings' ? 'active' : ''}`}
            onClick={() => navigateTo('/settings')}
          >
            <Settings size={19} />
            <span>Settings</span>
            {location.pathname === '/settings' && <span className="active-indicator" />}
          </button>

          <div className="sidebar-footer">
            <span className="sidebar-footer-dot" />
            <span>OfferShield AI · v1.0.0</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setMenuOpen(true)} aria-label="Open navigation">
              <Menu size={21} />
            </button>
            <div className="topbar-page-info">
              <div className="breadcrumb">
                <span>Workspace</span>
                <ChevronRight size={13} />
                <span className="breadcrumb-current">{activePage}</span>
              </div>
              <h2>{activePage}</h2>
            </div>
          </div>

          <div className="topbar-right">
            <div className="topbar-platform-status">
              <span className="topbar-status-dot" />
              System configured
            </div>
            <div className="topbar-divider" />

            <button
              className={`topbar-icon-button ${notificationsEnabled ? '' : 'is-disabled'}`}
              type="button"
              aria-label={notificationsEnabled ? 'Turn notifications off' : 'Turn notifications on'}
              aria-pressed={notificationsEnabled}
              title={notificationsEnabled ? 'Notifications are on — click to turn off' : 'Notifications are off — click to turn on'}
              onClick={() => setNotificationsEnabled(value => !value)}
            >
              {notificationsEnabled ? <Bell size={19} /> : <BellOff size={19} />}
            </button>

            <button
              className={`topbar-icon-button ${monochrome ? 'is-selected' : ''}`}
              type="button"
              aria-label={monochrome ? 'Turn monochrome mode off' : 'Turn monochrome mode on'}
              aria-pressed={monochrome}
              title={monochrome ? 'Monochrome mode on' : 'Monochrome mode off'}
              onClick={() => setMonochrome(value => !value)}
            >
              <Contrast size={19} />
            </button>

            <button
              className="topbar-icon-button"
              type="button"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              onClick={() => setTheme(value => value === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? <Sun size={19} /> : <Moon size={19} />}
            </button>

            <input
              ref={avatarInputRef}
              className="profile-avatar-input"
              type="file"
              accept="image/*"
              onChange={handleAvatarUpload}
              aria-label="Upload profile picture"
            />
            <button
              className="topbar-profile"
              type="button"
              onClick={() => avatarInputRef.current?.click()}
              title="Click to upload or change your profile photo"
            >
              <span className="profile-avatar">
                {avatar ? <img src={avatar} alt="Profile" /> : avatarInitial}
                <span className="profile-avatar-camera"><Camera size={11} /></span>
              </span>
              <span className="profile-details">
                <strong>{displayName}</strong>
                <span>{displayRole} · {displayWorkspace}</span>
              </span>
              <ChevronDown size={16} />
            </button>
          </div>
        </header>

        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/analyse" element={<Analysis />} />
            <Route path="/results" element={<Results />} />
            <Route path="/history" element={<History />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/explainable-ai" element={<ExplainableAI />} />
            <Route path="/company-verification" element={<CompanyVerification />} />
            <Route path="/patterns" element={<PatternIntelligence />} />
            <Route path="/about" element={<About />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<DashboardPage />} />
          </Routes>

          <footer className="page-footer">
            <span>© 2026 OfferShield AI</span>
            <span>Built with machine learning and explainable AI</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App
