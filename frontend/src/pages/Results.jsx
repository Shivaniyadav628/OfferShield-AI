
import { useLocation, useNavigate } from 'react-router-dom'

import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Calculator,
  CheckCircle2,
  XCircle,
  Info
} from 'lucide-react'

function Results() {
  const location = useLocation()
  const navigate = useNavigate()

  const result = location.state?.result

  // Return to analysis if no result is available
  if (!result) {
    return (
      <div className="results-page">
        <div className="empty-state">
          <ShieldAlert size={40} />

          <h2>No Analysis Results Found</h2>

          <p>
            Please analyse a job posting to view its results.
          </p>

          <button
            className="btn btn-primary"
            onClick={() => navigate('/analyse')}
          >
            Analyse a Job
          </button>
        </div>
      </div>
    )
  }

  // Risk configuration with fallback for older history records
  const decisionScore = Number(result.decision_score ?? 0)
  const fraudThreshold = Number(result.threshold ?? 0.1)
  const reviewThreshold = Number(result.review_threshold ?? -0.4)

  let riskLevel = result.risk_level
  let riskClassification = result.result

  if (!riskLevel) {
    if (decisionScore >= fraudThreshold) {
      riskLevel = 'high'
      riskClassification = 'Potentially Fraudulent'
    } else if (decisionScore >= reviewThreshold) {
      riskLevel = 'medium'
      riskClassification = 'Needs Manual Review'
    } else {
      riskLevel = 'low'
      riskClassification = 'Likely Genuine'
    }
  }

  const riskConfiguration = {
    high: {
      title: 'Potentially Fraudulent',
      description:
        'The model detected signals associated with fraudulent job postings. Investigate carefully before proceeding.',
      icon: ShieldAlert,
      className: 'high'
    },

    medium: {
      title: 'Needs Manual Review',
      description:
        'The posting falls within the manual-review range. Verify the employer and job details before proceeding.',
      icon: AlertTriangle,
      className: 'medium'
    },

    low: {
      title: 'Likely Genuine',
      description:
        'The model indicates a lower fraud risk. Independent verification is still recommended.',
      icon: ShieldCheck,
      className: 'low'
    }
  }

  const risk = riskConfiguration[riskLevel] || riskConfiguration.medium
  const RiskIcon = risk.icon

  const verification = result.mathematical_verification

  // Format decision score
  function formatScore(value) {
    const number = Number(value)

    return Number.isFinite(number)
      ? number.toFixed(4)
      : 'N/A'
  }

  // Render feature contribution signals
  function renderSignals(signals, emptyMessage) {
    if (!signals || signals.length === 0) {
      return (
        <p className="empty-signals">
          {emptyMessage}
        </p>
      )
    }

    return (
      <div className="signal-list">
        {signals.map((signal, index) => (
          <div className="signal-item" key={signal.feature || index}>
            <div>
              <strong>
                {signal.feature || 'Feature'}
              </strong>

              {signal.description && (
                <p>{signal.description}</p>
              )}
            </div>

            <span>
              {formatScore(signal.contribution)}
            </span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="results-page">

      {/* Page heading */}
      <div className="results-page-heading">

        <button
          className="back-button"
          onClick={() => navigate('/analyse')}
        >
          <ArrowLeft size={18} />
          Back to Analysis
        </button>

        <p className="eyebrow">ANALYSIS REPORT</p>

        <h1>Job Screening Results</h1>

        <p>
          Review the machine learning prediction, risk assessment
          and explainable signals for this job posting.
        </p>

      </div>

      {/* Risk classification */}
      <section className={`result-risk-card result-${risk.className}`}>

        <div className="result-risk-icon">
          <RiskIcon size={30} />
        </div>

        <div className="result-risk-content">

          <span className="result-risk-label">
            RISK CLASSIFICATION
          </span>

          <h2>{risk.title}</h2>

          <p>{risk.description}</p>

        </div>

      </section>

      {/* Job title */}
      <section className="result-job-card">

        <div>
          <span className="result-section-label">
            ANALYSED JOB POSTING
          </span>

          <h2>
            {result.job_title || 'Job Posting'}
          </h2>
        </div>

        <span className={`result-status-badge result-badge-${risk.className}`}>
          {risk.title}
        </span>

      </section>

      {/* Recommendation */}
      <section className="result-recommendation">

        <div className="recommendation-icon">
          <Info size={20} />
        </div>

        <div>
          <h3>Recommended Action</h3>

          <p>
            {result.recommendation ||
              'Independently verify the employer and job posting before proceeding.'}
          </p>
        </div>

      </section>

      {/* Model metrics */}
      <section className="result-section">

        <div className="result-section-heading">
          <div>
            <p className="eyebrow">MODEL ASSESSMENT</p>
            <h2>Prediction Metrics</h2>
          </div>
        </div>

        <div className="result-metrics-grid">

          <div className="result-metric-card">
            <span>Decision Score</span>

            <strong>
              {formatScore(decisionScore)}
            </strong>

            <small>
              SVM model decision score
            </small>
          </div>

          <div className="result-metric-card">
            <span>Fraud Threshold</span>

            <strong>
              {formatScore(fraudThreshold)}
            </strong>

            <small>
              Potential fraud boundary
            </small>
          </div>

          <div className="result-metric-card">
            <span>Review Threshold</span>

            <strong>
              {formatScore(reviewThreshold)}
            </strong>

            <small>
              Manual review boundary
            </small>
          </div>

          <div className="result-metric-card">
            <span>Binary Prediction</span>

            <strong>
              {result.prediction === 1
                ? 'Fraud'
                : 'Below Fraud Threshold'}
            </strong>

            <small>
              Original binary model output
            </small>
          </div>

        </div>

        <p className="result-metric-note">
          Decision scores are not probabilities. A score at or above
          the fraud threshold is classified as potentially fraudulent.
          Scores between the review and fraud thresholds require manual
          review.
        </p>

      </section>

      {/* Feature explanations */}
      <section className="result-section">

        <div className="result-section-heading">
          <div>
            <p className="eyebrow">MODEL EXPLAINABILITY</p>
            <h2>Why Did the Model Make This Prediction?</h2>

            <p>
              These signals show which features influenced the model's
              decision score.
            </p>
          </div>
        </div>

        <div className="result-signals-grid">

          {/* Fraud signals */}
          <div className="result-signals-card">

            <div className="signals-card-heading fraud-signals-heading">
              <TrendingUp size={20} />

              <div>
                <h3>Fraud-Increasing Signals</h3>

                <p>
                  Features pushing the score towards fraud.
                </p>
              </div>
            </div>

            {renderSignals(
              result.fraud_increasing_signals,
              'No significant fraud-increasing signals were identified.'
            )}

          </div>

          {/* Genuine signals */}
          <div className="result-signals-card">

            <div className="signals-card-heading genuine-signals-heading">
              <TrendingDown size={20} />

              <div>
                <h3>Genuine-Increasing Signals</h3>

                <p>
                  Features pushing the score away from fraud.
                </p>
              </div>
            </div>

            {renderSignals(
              result.genuine_increasing_signals,
              'No significant genuine-increasing signals were identified.'
            )}

          </div>

        </div>

      </section>

      {/* Mathematical verification */}
      {verification && (
        <section className="result-section">

          <div className="result-section-heading">
            <div>
              <p className="eyebrow">TRANSPARENCY & AUDIT</p>

              <h2>Mathematical Verification</h2>

              <p>
                Verification of the relationship between the model's
                feature contributions and its decision score.
              </p>
            </div>
          </div>

          <div className="verification-card">

            <div className="verification-heading">
              <Calculator size={21} />

              <h3>Decision Score Reconstruction</h3>
            </div>

            <div className="verification-values">

              <div>
                <span>Actual Model Score</span>

                <strong>
                  {formatScore(verification.actual_score)}
                </strong>
              </div>

              <div>
                <span>Contribution Sum</span>

                <strong>
                  {formatScore(verification.contribution_sum)}
                </strong>
              </div>

              <div>
                <span>Model Intercept</span>

                <strong>
                  {formatScore(verification.intercept)}
                </strong>
              </div>

              <div>
                <span>Reconstructed Score</span>

                <strong>
                  {formatScore(verification.reconstructed_score)}
                </strong>
              </div>

              <div>
                <span>Difference</span>

                <strong>
                  {formatScore(verification.difference)}
                </strong>
              </div>

            </div>

            <div className={`verification-status ${
              verification.verified ? 'verified' : 'not-verified'
            }`}>

              {verification.verified ? (
                <CheckCircle2 size={19} />
              ) : (
                <XCircle size={19} />
              )}

              <span>
                {verification.verified
                  ? 'Mathematical verification passed'
                  : 'Mathematical verification did not pass'}
              </span>

            </div>

          </div>

        </section>
      )}

      {/* Disclaimer */}
      <section className="result-disclaimer">

        <ShieldCheck size={20} />

        <div>
          <h3>Important Disclaimer</h3>

          <p>
            OfferShield AI provides a machine learning-based risk
            assessment, not a guarantee that a job posting is genuine
            or fraudulent. A lower-risk classification does not prove
            that an employer is legitimate. Always independently verify
            the company, recruiter, contact details and opportunity.
          </p>
        </div>

      </section>

      {/* Actions */}
      <div className="results-actions">

        <button
          className="btn btn-secondary"
          onClick={() => navigate('/history')}
        >
          View Analysis History
        </button>

        <button
          className="btn btn-primary"
          onClick={() => navigate('/analyse')}
        >
          Analyse Another Job
        </button>

      </div>

    </div>
  )
}

export default Results
