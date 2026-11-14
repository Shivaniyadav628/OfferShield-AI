
import { useEffect, useState } from 'react'
import {
  UserRound,
  BriefcaseBusiness,
  Save,
  Trash2,
  ShieldCheck,
  Database,
  Info,
  Settings2
} from 'lucide-react'

const SETTINGS_KEY = 'offershield_user_settings'
const HISTORY_KEY = 'offershield_analysis_history'

const defaultSettings = {
  displayName: 'Student',
  role: 'Student',
  workspace: 'Workspace'
}

function Settings() {
  const [profile, setProfile] = useState(defaultSettings)
  const [historyCount, setHistoryCount] = useState(0)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    try {
      const storedSettings = localStorage.getItem(SETTINGS_KEY)
      const storedHistory = localStorage.getItem(HISTORY_KEY)

      if (storedSettings) {
        setProfile({
          ...defaultSettings,
          ...JSON.parse(storedSettings)
        })
      }

      if (storedHistory) {
        const history = JSON.parse(storedHistory)
        setHistoryCount(Array.isArray(history) ? history.length : 0)
      }
    } catch (error) {
      console.error('Unable to load settings:', error)
    }
  }, [])

  const handleChange = (event) => {
    const { name, value } = event.target

    setProfile((previous) => ({
      ...previous,
      [name]: value
    }))

    setSaved(false)
  }

  const handleSave = (event) => {
    event.preventDefault()

    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(profile))
      setSaved(true)
    } catch (error) {
      console.error('Unable to save settings:', error)
      alert('Unable to save your settings in this browser.')
    }
  }

  const handleClearHistory = () => {
    const confirmed = window.confirm(
      'Are you sure you want to permanently clear all saved analysis history from this browser?'
    )

    if (!confirmed) return

    try {
      localStorage.removeItem(HISTORY_KEY)
      setHistoryCount(0)
      alert('Analysis history has been cleared from this browser.')
    } catch (error) {
      console.error('Unable to clear history:', error)
      alert('Unable to clear analysis history.')
    }
  }

  return (
    <div className="settings-page">
      <div className="settings-page-header">
        <div>
          <div className="settings-eyebrow">
            <Settings2 size={15} />
            PREFERENCES
          </div>

          <h1>Settings</h1>

          <p>
            Manage your workspace information and local application data.
          </p>
        </div>
      </div>

      <div className="settings-layout">
        <div className="settings-main">

          {/* Profile settings */}
          <section className="settings-card">
            <div className="settings-card-heading">
              <div className="settings-heading-icon">
                <UserRound size={19} />
              </div>

              <div>
                <h2>Profile & Workspace</h2>
                <p>Customise the information associated with your workspace.</p>
              </div>
            </div>

            <form onSubmit={handleSave}>
              <div className="settings-form-grid">
                <div className="settings-field">
                  <label htmlFor="displayName">Display name</label>
                  <input
                    id="displayName"
                    name="displayName"
                    type="text"
                    value={profile.displayName}
                    onChange={handleChange}
                    placeholder="Enter your display name"
                    maxLength={50}
                  />
                </div>

                <div className="settings-field">
                  <label htmlFor="role">Role</label>
                  <input
                    id="role"
                    name="role"
                    type="text"
                    value={profile.role}
                    onChange={handleChange}
                    placeholder="e.g. Student"
                    maxLength={50}
                  />
                </div>

                <div className="settings-field settings-field-full">
                  <label htmlFor="workspace">Workspace name</label>
                  <div className="settings-input-icon">
                    <BriefcaseBusiness size={17} />
                    <input
                      id="workspace"
                      name="workspace"
                      type="text"
                      value={profile.workspace}
                      onChange={handleChange}
                      placeholder="Enter workspace name"
                      maxLength={60}
                    />
                  </div>
                </div>
              </div>

              <div className="settings-form-footer">
                <span className="settings-save-message" aria-live="polite">
                  {saved ? 'Your settings have been saved.' : ''}
                </span>

                <button className="settings-save-button" type="submit">
                  <Save size={16} />
                  Save changes
                </button>
              </div>
            </form>
          </section>

          {/* Data management */}
          <section className="settings-card">
            <div className="settings-card-heading">
              <div className="settings-heading-icon">
                <Database size={19} />
              </div>

              <div>
                <h2>Data management</h2>
                <p>Review and manage analysis data stored in this browser.</p>
              </div>
            </div>

            <div className="settings-storage-row">
              <div>
                <span className="settings-storage-label">
                  Saved analysis reports
                </span>
                <p>Your locally stored analysis history.</p>
              </div>

              <span className="settings-count">
                {historyCount}
              </span>
            </div>

            <div className="settings-danger-area">
              <div>
                <h3>Clear analysis history</h3>
                <p>
                  Permanently delete all saved reports from this browser.
                  This action cannot be undone.
                </p>
              </div>

              <button
                type="button"
                className="settings-clear-button"
                onClick={handleClearHistory}
                disabled={historyCount === 0}
              >
                <Trash2 size={16} />
                Clear history
              </button>
            </div>
          </section>
        </div>

        {/* Information panel */}
        <aside className="settings-side">
          <section className="settings-info-card">
            <div className="settings-info-icon">
              <ShieldCheck size={21} />
            </div>

            <h2>Your data, your control</h2>

            <p>
              Profile preferences and analysis history are stored locally
              in your browser. Clearing browser storage may remove this data.
            </p>
          </section>

          <section className="settings-info-card settings-about-card">
            <div className="settings-info-icon">
              <Info size={21} />
            </div>

            <h2>About these settings</h2>

            <p>
              These preferences currently apply to this browser only.
              They are not connected to a cloud account or shared across devices.
            </p>

            <span className="settings-version">OfferShield AI</span>
          </section>
        </aside>
      </div>
    </div>
  )
}

export default Settings
