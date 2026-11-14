
import { useEffect, useMemo, useState } from 'react'

import {
  ArrowLeftRight,
  ShieldCheck,
  ShieldAlert,
  GitCompareArrows,
  AlertTriangle,
  CheckCircle2,
  Info,
  BriefcaseBusiness
} from 'lucide-react'

const STORAGE_KEY = 'offershield_analysis_history'

function Compare() {
  const [history, setHistory] = useState([])
  const [firstId, setFirstId] = useState('')
  const [secondId, setSecondId] = useState('')

  // Load saved analyses
  useEffect(() => {
    try {
      const saved = JSON.parse(
        localStorage.getItem(STORAGE_KEY) || '[]'
      )

      if (Array.isArray(saved)) {
        setHistory(saved)
      }
    } catch (error) {
      console.error('Unable to load analysis history:', error)
      setHistory([])
    }
  }, [])

  const firstItem = history.find(
    item => String(item.id) === firstId
  )

  const secondItem = history.find(
    item => String(item.id) === secondId
  )

  const first = firstItem?.result
  const second = secondItem?.result

  // Original submitted job information
  const jobA = firstItem?.jobData || {}
  const jobB = secondItem?.jobData || {}

  // Extract signals directly from the API response
  const fraudSignalsA = first?.fraud_increasing_signals || []
  const fraudSignalsB = second?.fraud_increasing_signals || []

  const genuineSignalsA = first?.genuine_increasing_signals || []
  const genuineSignalsB = second?.genuine_increasing_signals || []

  // Support both string and object signal formats
  function getSignalName(signal) {
    if (typeof signal === 'string') {
      return signal.replaceAll('_', ' ')
    }

    return (
      signal?.feature ||
      signal?.name ||
      'Unknown signal'
    ).replaceAll('_', ' ')
  }

  function getSignalNames(signals) {
    return signals.map(getSignalName)
  }

  function getScore(value) {
    if (value === null || value === undefined || value === '') {
      return 'Not available'
    }

    const number = Number(value)

    return Number.isFinite(number)
      ? number.toFixed(6)
      : 'Not available'
  }

  function getClassification(result) {
    return result?.risk_classification || 'Not available'
  }

  function getJobTitle(result, jobData) {
    return jobData?.title || result?.job_title || 'Untitled job'
  }

  function getDate(item) {
    return item?.createdAt
      ? new Date(item.createdAt).toLocaleDateString('en-IN')
      : 'Unknown date'
  }

  // Compare original job posting information
  const postingDifferences = useMemo(() => {
    if (!first || !second) return []

    const fields = [
      ['Job Title', 'title'],
      ['Location', 'location'],
      ['Department', 'department'],
      ['Employment Type', 'employment_type'],
      ['Required Experience', 'required_experience'],
      ['Required Education', 'required_education'],
      ['Industry', 'industry'],
      ['Function', 'function'],
      ['Salary Range', 'salary_range'],
      ['Company Profile', 'company_profile'],
      ['Job Description', 'description'],
      ['Requirements', 'requirements'],
      ['Benefits', 'benefits'],
      ['Remote Work', 'telecommuting'],
      ['Company Logo', 'has_company_logo'],
      ['Screening Questions', 'has_questions']
    ]

    return fields.map(([label, key]) => {
      const valueA = jobA[key]
      const valueB = jobB[key]

      const displayA =
        valueA === undefined || valueA === null || valueA === ''
          ? 'Not provided'
          : typeof valueA === 'number' && [
              'telecommuting',
              'has_company_logo',
              'has_questions'
            ].includes(key)
            ? valueA === 1 ? 'Yes' : 'No'
            : String(valueA)

      const displayB =
        valueB === undefined || valueB === null || valueB === ''
          ? 'Not provided'
          : typeof valueB === 'number' && [
              'telecommuting',
              'has_company_logo',
              'has_questions'
            ].includes(key)
            ? valueB === 1 ? 'Yes' : 'No'
            : String(valueB)

      return {
        label,
        valueA: displayA,
        valueB: displayB,
        isDifferent:
          String(valueA ?? '').trim().toLowerCase() !==
          String(valueB ?? '').trim().toLowerCase()
      }
    })
  }, [first, second, jobA, jobB])

  const differentFieldCount = postingDifferences.filter(
    field => field.isDifferent
  ).length

  // Compare signal lists
  function getSignalComparison(signalsA, signalsB) {
    const namesA = getSignalNames(signalsA)
    const namesB = getSignalNames(signalsB)

    return {
      onlyA: namesA.filter(name => !namesB.includes(name)),
      onlyB: namesB.filter(name => !namesA.includes(name)),
      common: namesA.filter(name => namesB.includes(name))
    }
  }

  function renderSignalList(signals) {
    if (!signals || signals.length === 0) {
      return (
        <p className="compare-no-data">
          No contributing signals available.
        </p>
      )
    }

    return (
      <ul className="compare-signal-list">
        {signals.map((signal, index) => (
          <li key={`${getSignalName(signal)}-${index}`}>
            <span>{getSignalName(signal)}</span>

            {typeof signal === 'object' &&
              signal?.contribution !== undefined && (
                <strong>
                  {Number(signal.contribution) > 0 ? '+' : ''}
                  {getScore(signal.contribution)}
                </strong>
              )}
          </li>
        ))}
      </ul>
    )
  }

  function renderSignalComparison(title, signalsA, signalsB) {
    const comparison = getSignalComparison(signalsA, signalsB)

    return (
      <section className="compare-section">
        <div className="compare-section-heading">
          <h2>{title}</h2>
          <p>Compare the signals identified in each analysis.</p>
        </div>

        <div className="compare-columns">
          <div className="compare-panel">
            <h3>Job A</h3>
            {renderSignalList(signalsA)}
          </div>

          <div className="compare-panel">
            <h3>Job B</h3>
            {renderSignalList(signalsB)}
          </div>
        </div>

        <div className="compare-signal-summary">
          <div>
            <span>Common signals</span>
            <strong>{comparison.common.length}</strong>
          </div>

          <div>
            <span>Only in Job A</span>
            <strong>{comparison.onlyA.length}</strong>
          </div>

          <div>
            <span>Only in Job B</span>
            <strong>{comparison.onlyB.length}</strong>
          </div>
        </div>
      </section>
    )
  }

  return (
    <div className="compare-page">

      {/* Page heading */}
      <div className="compare-page-heading">
        <div>
          <p className="eyebrow">ANALYTICAL INSIGHTS</p>
          <h1>Analysis Comparison</h1>
          <p>
            Compare two saved job analyses and examine their
            machine learning results.
          </p>
        </div>

        <div className="compare-heading-icon">
          <GitCompareArrows size={27} />
        </div>
      </div>

      {history.length < 2 ? (
        <div className="compare-empty-state">
          <BriefcaseBusiness size={34} />

          <h2>More analyses needed</h2>

          <p>
            You need at least two saved job analyses to use
            the comparison feature.
          </p>
        </div>
      ) : (
        <>
          {/* Select reports */}
          <section className="compare-selection-section">
            <div className="compare-section-heading">
              <h2>Select job analyses</h2>
              <p>Choose two different reports from your history.</p>
            </div>

            <div className="compare-selection-grid">

              <div className="compare-select-card">
                <label htmlFor="compare-first">Job A</label>

                <select
                  id="compare-first"
                  value={firstId}
                  onChange={event => setFirstId(event.target.value)}
                >
                  <option value="">Select first analysis</option>

                  {history.map(item => (
                    <option
                      key={item.id}
                      value={String(item.id)}
                      disabled={String(item.id) === secondId}
                    >
                      {getJobTitle(item.result, item.jobData)}
                      {' — '}
                      {getDate(item)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="compare-middle-icon">
                <ArrowLeftRight size={23} />
              </div>

              <div className="compare-select-card">
                <label htmlFor="compare-second">Job B</label>

                <select
                  id="compare-second"
                  value={secondId}
                  onChange={event => setSecondId(event.target.value)}
                >
                  <option value="">Select second analysis</option>

                  {history.map(item => (
                    <option
                      key={item.id}
                      value={String(item.id)}
                      disabled={String(item.id) === firstId}
                    >
                      {getJobTitle(item.result, item.jobData)}
                      {' — '}
                      {getDate(item)}
                    </option>
                  ))}
                </select>
              </div>

            </div>
          </section>

          {first && second && (
            <>
              {/* Risk classification */}
              <section className="compare-section">
                <div className="compare-section-heading">
                  <h2>Risk classification</h2>
                  <p>Side-by-side AI prediction results.</p>
                </div>

                <div className="compare-columns">
                  {[first, second].map((result, index) => {
                    const fraudulent = result.prediction === 1

                    const jobData = index === 0 ? jobA : jobB

                    return (
                      <div
                        className="compare-risk-card"
                        key={index}
                      >
                        <span className="compare-job-label">
                          Job {index === 0 ? 'A' : 'B'}
                        </span>

                        <div className={`compare-risk-icon ${
                          fraudulent
                            ? 'compare-risk-fraud'
                            : 'compare-risk-genuine'
                        }`}>
                          {fraudulent
                            ? <ShieldAlert size={25} />
                            : <ShieldCheck size={25} />
                          }
                        </div>

                        <h3>{getJobTitle(result, jobData)}</h3>

                        <strong>
                          {getClassification(result)}
                        </strong>

                        <p>
                          {fraudulent
                            ? 'The model classified this posting as potentially fraudulent.'
                            : 'The model classified this posting as genuine.'}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </section>

              {/* Decision scores */}
              <section className="compare-section">
                <div className="compare-section-heading">
                  <h2>Model score comparison</h2>
                  <p>
                    Compare the decision scores and configured thresholds.
                  </p>
                </div>

                <div className="compare-metrics-grid">

                  <div className="compare-metric-card">
                    <span>Job A decision score</span>
                    <strong>{getScore(first.decision_score)}</strong>
                    <small>
                      Threshold: {getScore(first.threshold)}
                    </small>
                  </div>

                  <div className="compare-metric-card">
                    <span>Job B decision score</span>
                    <strong>{getScore(second.decision_score)}</strong>
                    <small>
                      Threshold: {getScore(second.threshold)}
                    </small>
                  </div>

                </div>

                <div className="compare-info-note">
                  <Info size={17} />

                  <p>
                    Decision scores are model outputs, not fraud
                    probabilities. Compare each score against its
                    own model threshold; do not interpret the
                    difference as a percentage risk difference.
                  </p>
                </div>
              </section>

              {/* Fraud signals */}
              {renderSignalComparison(
                'Fraud-increasing signals',
                fraudSignalsA,
                fraudSignalsB
              )}

              {/* Genuine signals */}
              {renderSignalComparison(
                'Genuine-increasing signals',
                genuineSignalsA,
                genuineSignalsB
              )}

              {/* Job posting differences */}
              <section className="compare-section">
                <div className="compare-section-heading">
                  <h2>Job posting differences</h2>
                  <p>
                    Compare the information provided in both job postings.
                  </p>
                </div>

                <div className="compare-difference-summary">
                  <strong>{differentFieldCount}</strong>
                  <span>
                    of {postingDifferences.length} fields differ
                  </span>
                </div>

                <div className="compare-difference-list">
                  {postingDifferences.map(field => (
                    <div
                      className={`compare-difference-row ${
                        field.isDifferent
                          ? 'compare-field-different'
                          : 'compare-field-same'
                      }`}
                      key={field.label}
                    >
                      <div className="compare-difference-label">

                        {field.isDifferent
                          ? <AlertTriangle size={16} />
                          : <CheckCircle2 size={16} />
                        }

                        <strong>{field.label}</strong>

                        <span>
                          {field.isDifferent ? 'Different' : 'Same'}
                        </span>
                      </div>

                      <div className="compare-columns">

                        <div>
                          <small>Job A</small>
                          <p>{field.valueA}</p>
                        </div>

                        <div>
                          <small>Job B</small>
                          <p>{field.valueB}</p>
                        </div>

                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Disclaimer */}
              <div className="compare-disclaimer">
                <AlertTriangle size={18} />

                <p>
                  This comparison presents differences between saved
                  job posting information and model outputs. It does
                  not establish whether an employer is legitimate or
                  whether either job is fraudulent.
                </p>
              </div>
            </>
          )}
        </>
      )}

    </div>
  )
}

export default Compare
