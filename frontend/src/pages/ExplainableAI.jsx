
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  BrainCircuit,
  ShieldCheck,
  ShieldAlert,
  Activity,
  Calculator,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  ArrowDownRight,
  FileSearch,
  Info,
  Database,
  Clock3
} from 'lucide-react'

const STORAGE_KEY = 'offershield_analysis_history'

function formatScore(value) {
  const number = Number(value)

  return Number.isFinite(number) ? number.toFixed(4) : 'N/A'
}

function ExplainableAI() {
  const navigate = useNavigate()

  const [history, setHistory] = useState([])
  const [selectedId, setSelectedId] = useState('')

  useEffect(() => {
    try {
      const savedHistory = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || '[]'
      )

      if (Array.isArray(savedHistory)) {
        setHistory(savedHistory)

        if (savedHistory.length > 0) {
          setSelectedId(savedHistory[0].id)
        }
      }
    } catch (error) {
      console.error('Unable to load analysis history:', error)
      setHistory([])
    }
  }, [])

  const selectedItem = history.find(
    item => item.id === selectedId
  )

  const result = selectedItem?.result

  const verification = result?.mathematical_verification

  const fraudSignals = result?.fraud_increasing_signals || []

  const genuineSignals = result?.genuine_increasing_signals || []

  const isFraudulent = result?.prediction === 1

  function formatDate(dateValue) {
    const date = new Date(dateValue)

    if (Number.isNaN(date.getTime())) {
      return 'Date unavailable'
    }

    return date.toLocaleString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="explainable-page">

      {/* PAGE HEADER */}

      <div className="explainable-header">
        <div>
          <div className="eyebrow">MODEL INTELLIGENCE</div>

          <h1>Explainable AI</h1>

          <p>
            Understand how OfferShield AI evaluates job postings
            and explains its machine learning decisions.
          </p>
        </div>

        <div className="explainable-header-icon">
          <BrainCircuit size={27} />
        </div>
      </div>

      {/* MODEL OVERVIEW */}

      <div className="explainable-section-heading">
        <div>
          <h2>Model overview</h2>
          <p>Technical information about the prediction engine.</p>
        </div>
      </div>

      <div className="explainable-overview-grid">

        <div className="explainable-overview-card">
          <div className="explainable-card-icon blue">
            <BrainCircuit size={20} />
          </div>

          <div>
            <span>ML Algorithm</span>
            <h3>LinearSVC</h3>
            <p>Supervised machine learning</p>
          </div>
        </div>

        <div className="explainable-overview-card">
          <div className="explainable-card-icon purple">
            <Database size={20} />
          </div>

          <div>
            <span>Training Dataset</span>
            <h3>17,880</h3>
            <p>Job postings</p>
          </div>
        </div>

        <div className="explainable-overview-card">
          <div className="explainable-card-icon green">
            <Activity size={20} />
          </div>

          <div>
            <span>Input Features</span>
            <h3>16</h3>
            <p>Job and company attributes</p>
          </div>
        </div>

        <div className="explainable-overview-card">
          <div className="explainable-card-icon orange">
            <Calculator size={20} />
          </div>

          <div>
            <span>Explanation Method</span>
            <h3>Linear Contributions</h3>
            <p>Feature value × model coefficient</p>
          </div>
        </div>

      </div>

      {/* ANALYSIS SELECTOR */}

      <div className="explainable-section-heading">
        <div>
          <h2>Prediction explanation</h2>
          <p>Select an existing analysis to inspect its model explanation.</p>
        </div>
      </div>

      {history.length === 0 ? (

        <div className="explainable-empty">

          <div className="explainable-empty-icon">
            <FileSearch size={29} />
          </div>

          <h3>No analysis available</h3>

          <p>
            Complete a job analysis first. Its prediction signals
            and mathematical explanation will appear here.
          </p>

          <button
            className="btn btn-primary"
            onClick={() => navigate('/analyse')}
          >
            Analyse a job posting
          </button>

        </div>

      ) : (

        <>

          <div className="explainable-selector">

            <label htmlFor="analysis-select">
              Select analysis
            </label>

            <select
              id="analysis-select"
              value={selectedId}
              onChange={event => setSelectedId(event.target.value)}
            >
              {history.map(item => (
                <option key={item.id} value={item.id}>
                  {item.result?.job_title || 'Untitled job'} —{' '}
                  {formatDate(item.createdAt)}
                </option>
              ))}
            </select>

          </div>

          {result && (

            <>

              {/* PREDICTION SUMMARY */}

              <div className="explainable-result-card">

                <div className="explainable-result-heading">

                  <div>
                    <span className="eyebrow">ANALYSIS REPORT</span>

                    <h2>
                      {result.job_title || 'Untitled job'}
                    </h2>

                    <p>
                      <Clock3 size={13} />
                      {formatDate(selectedItem.createdAt)}
                    </p>
                  </div>

                  <div className={`explainable-classification ${
                    isFraudulent ? 'fraud' : 'genuine'
                  }`}>

                    {isFraudulent ? (
                      <ShieldAlert size={19} />
                    ) : (
                      <ShieldCheck size={19} />
                    )}

                    {result.risk_classification}

                  </div>

                </div>

                <div className="explainable-score-grid">

                  <div>
                    <span>Decision Score</span>
                    <strong>{formatScore(result.decision_score)}</strong>
                  </div>

                  <div>
                    <span>Model Threshold</span>
                    <strong>{formatScore(result.threshold)}</strong>
                  </div>

                  <div>
                    <span>Prediction</span>
                    <strong>{result.prediction}</strong>
                    <small>
                      {isFraudulent ? 'Fraudulent class' : 'Genuine class'}
                    </small>
                  </div>

                </div>

              </div>

              {/* FEATURE SIGNALS */}

              <div className="explainable-section-heading">
                <div>
                  <h2>Feature contribution analysis</h2>
                  <p>
                    See which features pushed the model toward each class.
                  </p>
                </div>
              </div>

              <div className="explainable-signals-grid">

                <div className="explainable-signals-card">

                  <div className="explainable-signals-heading fraud">
                    <ShieldAlert size={19} />
                    <div>
                      <h3>Fraud-increasing signals</h3>
                      <p>Features pushing the decision toward fraud.</p>
                    </div>
                  </div>

                  {fraudSignals.length === 0 ? (

                    <p className="explainable-no-signals">
                      No fraud-increasing signals returned.
                    </p>

                  ) : (

                    <div className="explainable-signal-list">

                      {fraudSignals.map((signal, index) => (
                        <div
                          className="explainable-signal-row"
                          key={`${signal.feature}-${index}`}
                        >
                          <div>
                            <strong>{signal.feature}</strong>
                            <span>Feature contribution</span>
                          </div>

                          <strong className="signal-value fraud">
                            {formatScore(signal.contribution)}
                          </strong>
                        </div>
                      ))}

                    </div>

                  )}

                </div>

                <div className="explainable-signals-card">

                  <div className="explainable-signals-heading genuine">
                    <ShieldCheck size={19} />
                    <div>
                      <h3>Genuine-increasing signals</h3>
                      <p>Features pushing the decision toward genuine.</p>
                    </div>
                  </div>

                  {genuineSignals.length === 0 ? (

                    <p className="explainable-no-signals">
                      No genuine-increasing signals returned.
                    </p>

                  ) : (

                    <div className="explainable-signal-list">

                      {genuineSignals.map((signal, index) => (
                        <div
                          className="explainable-signal-row"
                          key={`${signal.feature}-${index}`}
                        >
                          <div>
                            <strong>{signal.feature}</strong>
                            <span>Feature contribution</span>
                          </div>

                          <strong className="signal-value genuine">
                            {formatScore(signal.contribution)}
                          </strong>
                        </div>
                      ))}

                    </div>

                  )}

                </div>

              </div>

              {/* MATHEMATICAL VERIFICATION */}

              <div className="explainable-section-heading">
                <div>
                  <h2>Mathematical verification</h2>
                  <p>
                    Verify that the feature contributions reconstruct
                    the model's decision score.
                  </p>
                </div>
              </div>

              {verification && (

                <div className="explainable-verification-card">

                  <div className="explainable-verification-heading">

                    <div className="explainable-card-icon blue">
                      <Calculator size={21} />
                    </div>

                    <div>
                      <h3>Decision score reconstruction</h3>
                      <p>
                        Contribution sum + intercept = reconstructed score
                      </p>
                    </div>

                    <div className={`explainable-verification-status ${
                      verification.verified ? 'verified' : 'failed'
                    }`}>
                      {verification.verified ? (
                        <CheckCircle2 size={16} />
                      ) : (
                        <XCircle size={16} />
                      )}

                      {verification.verified ? 'Verified' : 'Not verified'}
                    </div>

                  </div>

                  <div className="explainable-equation">

                    <div>
                      <span>Contribution Sum</span>
                      <strong>{formatScore(verification.contribution_sum)}</strong>
                    </div>

                    <span className="equation-symbol">+</span>

                    <div>
                      <span>Intercept</span>
                      <strong>{formatScore(verification.intercept)}</strong>
                    </div>

                    <span className="equation-symbol">=</span>

                    <div className="equation-result">
                      <span>Reconstructed Score</span>
                      <strong>
                        {formatScore(verification.reconstructed_score)}
                      </strong>
                    </div>

                  </div>

                  <div className="explainable-verification-details">

                    <div>
                      <span>Actual Model Score</span>
                      <strong>{formatScore(verification.actual_score)}</strong>
                    </div>

                    <div>
                      <span>Difference</span>
                      <strong>{formatScore(verification.difference)}</strong>
                    </div>

                  </div>

                </div>

              )}

              {/* MODEL DISCLAIMER */}

              <div className="explainable-disclaimer">

                <Info size={18} />

                <div>
                  <strong>Understanding model explanations</strong>

                  <p>
                    Feature contributions describe how the trained
                    LinearSVC model's decision score is influenced by
                    the input features. They do not establish causation
                    or prove that a company or job posting is fraudulent.
                    The decision score is not a probability.
                  </p>
                </div>

              </div>

            </>

          )}

        </>

      )}

    </div>
  )
}

export default ExplainableAI
