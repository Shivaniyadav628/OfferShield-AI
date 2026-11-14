
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BriefcaseBusiness,
  Clock3,
  FileSearch,
  Files,
  ShieldAlert,
  ShieldCheck,
  TrendingUp,
  BrainCircuit,
  RefreshCw
} from 'lucide-react'

const STORAGE_KEY = 'offershield_analysis_history'

function Dashboard() {
  const navigate = useNavigate()

  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  // Load saved analyses from localStorage
  function loadDashboardData() {
    try {
      const savedHistory = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || '[]'
      )

      setHistory(
        Array.isArray(savedHistory) ? savedHistory : []
      )
    } catch (error) {
      console.error('Dashboard data loading error:', error)
      setHistory([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboardData()

    // Update dashboard when localStorage changes in another tab
    window.addEventListener('storage', loadDashboardData)

    return () => {
      window.removeEventListener('storage', loadDashboardData)
    }
  }, [])

  // Calculate dashboard statistics
  const statistics = useMemo(() => {
    const total = history.length

    const genuine = history.filter(
      item => Number(item?.result?.prediction) === 0
    ).length

    const fraud = history.filter(
      item => Number(item?.result?.prediction) === 1
    ).length

    const genuinePercentage = total
      ? Math.round((genuine / total) * 100)
      : 0

    const fraudPercentage = total
      ? Math.round((fraud / total) * 100)
      : 0

    return {
      total,
      genuine,
      fraud,
      genuinePercentage,
      fraudPercentage
    }
  }, [history])

  // Format dates
  function formatDate(date) {
    if (!date) return 'Date unavailable'

    const parsedDate = new Date(date)

    if (Number.isNaN(parsedDate.getTime())) {
      return 'Date unavailable'
    }

    return parsedDate.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Get classification from saved prediction
  function getClassification(result) {
    if (Number(result?.prediction) === 1) {
      return 'Potential Fraud'
    }

    if (Number(result?.prediction) === 0) {
      return 'Likely Genuine'
    }

    return result?.risk_classification || 'Unknown'
  }

  // Get job title
  function getJobTitle(result) {
    return (
      result?.job_title ||
      result?.title ||
      'Untitled Job Posting'
    )
  }

  // Open an existing analysis
  function openAnalysis(item) {
    navigate('/results', {
      state: {
        result: item.result
      }
    })
  }

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading">
          <RefreshCw size={22} className="dashboard-loading-icon" />
          <p>Loading dashboard analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="dashboard-page">

      {/* Dashboard Header */}

      <section className="dashboard-header">
        <div>
          <div className="dashboard-eyebrow">
            <Activity size={15} />
            INTELLIGENCE OVERVIEW
          </div>

          <h1>Dashboard</h1>

          <p>
            Monitor job posting analyses, prediction insights,
            and fraud detection activity.
          </p>
        </div>

        <button
          className="dashboard-primary-button"
          onClick={() => navigate('/analyse')}
        >
          <FileSearch size={17} />
          Analyse New Job
        </button>
      </section>

      {/* Statistics */}

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <h2>Platform Overview</h2>
            <p>Your analysis activity at a glance.</p>
          </div>

          <button
            className="dashboard-refresh-button"
            onClick={loadDashboardData}
            title="Refresh dashboard"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        <div className="dashboard-stats-grid">

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-top">
              <div className="dashboard-stat-icon blue">
                <Files size={21} />
              </div>
              <span className="dashboard-stat-label">
                TOTAL ANALYSES
              </span>
            </div>

            <h3>{statistics.total}</h3>

            <p>Job postings analysed</p>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-top">
              <div className="dashboard-stat-icon green">
                <ShieldCheck size={21} />
              </div>
              <span className="dashboard-stat-label">
                LIKELY GENUINE
              </span>
            </div>

            <h3>{statistics.genuine}</h3>

            <p>
              {statistics.genuinePercentage}% of analysed postings
            </p>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-top">
              <div className="dashboard-stat-icon red">
                <ShieldAlert size={21} />
              </div>
              <span className="dashboard-stat-label">
                POTENTIAL FRAUD
              </span>
            </div>

            <h3>{statistics.fraud}</h3>

            <p>
              {statistics.fraudPercentage}% of analysed postings
            </p>
          </div>

          <div className="dashboard-stat-card">
            <div className="dashboard-stat-top">
              <div className="dashboard-stat-icon purple">
                <BrainCircuit size={21} />
              </div>
              <span className="dashboard-stat-label">
                ML ENGINE
              </span>
            </div>

            <h3>LinearSVC</h3>

            <p>Supervised learning model</p>
          </div>

        </div>
      </section>

      {/* Analytics */}

      <section className="dashboard-analytics-grid">

        <div className="dashboard-panel">
          <div className="dashboard-panel-heading">
            <div>
              <h2>Prediction Distribution</h2>
              <p>Classification of your analysed postings.</p>
            </div>

            <Activity size={19} />
          </div>

          {statistics.total === 0 ? (
            <div className="dashboard-chart-empty">
              <Activity size={30} />
              <p>No prediction data available yet.</p>
            </div>
          ) : (
            <div className="dashboard-distribution">

              <div className="dashboard-distribution-total">
                <span>Total Analyses</span>
                <strong>{statistics.total}</strong>
              </div>

              <div className="dashboard-distribution-bar">
                {statistics.genuine > 0 && (
                  <div
                    className="dashboard-bar-genuine"
                    style={{
                      width: `${statistics.genuinePercentage}%`
                    }}
                  />
                )}

                {statistics.fraud > 0 && (
                  <div
                    className="dashboard-bar-fraud"
                    style={{
                      width: `${statistics.fraudPercentage}%`
                    }}
                  />
                )}
              </div>

              <div className="dashboard-legend">

                <div>
                  <span className="dashboard-legend-dot genuine" />
                  <span>Likely Genuine</span>
                  <strong>{statistics.genuine}</strong>
                </div>

                <div>
                  <span className="dashboard-legend-dot fraud" />
                  <span>Potential Fraud</span>
                  <strong>{statistics.fraud}</strong>
                </div>

              </div>
            </div>
          )}
        </div>

        <div className="dashboard-panel dashboard-quick-panel">
          <div className="dashboard-panel-heading">
            <div>
              <h2>Quick Actions</h2>
              <p>Access your workspace.</p>
            </div>

            <ArrowUpRight size={19} />
          </div>

          <button
            className="dashboard-action"
            onClick={() => navigate('/analyse')}
          >
            <div className="dashboard-action-icon blue">
              <BriefcaseBusiness size={19} />
            </div>

            <div>
              <strong>Analyse a Job</strong>
              <span>Evaluate a new job posting</span>
            </div>

            <ArrowRight size={17} />
          </button>

          <button
            className="dashboard-action"
            onClick={() => navigate('/history')}
          >
            <div className="dashboard-action-icon green">
              <Clock3 size={19} />
            </div>

            <div>
              <strong>Analysis History</strong>
              <span>Review your previous analyses</span>
            </div>

            <ArrowRight size={17} />
          </button>

          <button
            className="dashboard-action"
            onClick={() => navigate('/explainable-ai')}
          >
            <div className="dashboard-action-icon purple">
              <BrainCircuit size={19} />
            </div>

            <div>
              <strong>Explainable AI</strong>
              <span>Understand model predictions</span>
            </div>

            <ArrowRight size={17} />
          </button>

        </div>

      </section>

      {/* Recent Analyses */}

      <section className="dashboard-recent-section">

        <div className="dashboard-section-heading">
          <div>
            <h2>Recent Analyses</h2>
            <p>Your latest job posting evaluations.</p>
          </div>

          <button
            className="dashboard-view-all"
            onClick={() => navigate('/history')}
          >
            View All
            <ArrowRight size={16} />
          </button>
        </div>

        {history.length === 0 ? (
          <div className="dashboard-empty">
            <div className="dashboard-empty-icon">
              <FileSearch size={27} />
            </div>

            <h3>No analyses yet</h3>

            <p>
              Start by analysing a job posting. Your recent
              activity and analytics will appear here.
            </p>

            <button
              className="dashboard-primary-button"
              onClick={() => navigate('/analyse')}
            >
              Analyse Your First Job
              <ArrowRight size={17} />
            </button>
          </div>
        ) : (
          <div className="dashboard-recent-list">

            {history.slice(0, 5).map((item) => {
              const result = item?.result || {}
              const classification = getClassification(result)
              const isFraud = Number(result.prediction) === 1

              return (
                <div
                  className="dashboard-recent-item"
                  key={item.id}
                >
                  <div className="dashboard-recent-icon">
                    <BriefcaseBusiness size={19} />
                  </div>

                  <div className="dashboard-recent-info">
                    <strong>{getJobTitle(result)}</strong>
                    <span>{formatDate(item.createdAt)}</span>
                  </div>

                  <span
                    className={`dashboard-status ${
                      isFraud ? 'fraud' : 'genuine'
                    }`}
                  >
                    {classification}
                  </span>

                  <div className="dashboard-recent-score">
                    <span>Decision Score</span>
                    <strong>
                      {Number.isFinite(Number(result.decision_score))
                        ? Number(result.decision_score).toFixed(4)
                        : 'N/A'}
                    </strong>
                  </div>

                  <button
                    className="dashboard-view-button"
                    onClick={() => openAnalysis(item)}
                    aria-label={`View ${getJobTitle(result)} report`}
                  >
                    <ArrowUpRight size={18} />
                  </button>
                </div>
              )
            })}

          </div>
        )}

      </section>

      {/* Model Information */}

      <section className="dashboard-model-note">
        <div className="dashboard-model-note-icon">
          <TrendingUp size={20} />
        </div>

        <div>
          <strong>Powered by Explainable Machine Learning</strong>

          <p>
            OfferShield AI uses a LinearSVC model trained on
            17,880 job postings and 16 input features.
            Predictions indicate estimated risk, not guaranteed
            proof of fraud or legitimacy.
          </p>
        </div>

        <button
          onClick={() => navigate('/explainable-ai')}
          aria-label="Explore Explainable AI"
        >
          Explore
          <ArrowRight size={16} />
        </button>
      </section>

    </main>
  )
}

export default Dashboard
