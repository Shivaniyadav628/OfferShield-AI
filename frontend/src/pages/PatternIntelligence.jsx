
import { useEffect, useMemo, useState } from 'react'

import {
  Activity,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  BrainCircuit,
  BarChart3,
  Search,
  RefreshCw,
  Info,
  Target,
  Layers3,
  Lightbulb,
  TrendingUp,
  CalendarDays,
  Repeat2,
  Download
} from 'lucide-react'

import { jsPDF } from 'jspdf'

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
  Tooltip,
  Legend,
  LineChart,
  Line
} from 'recharts'

const HISTORY_KEY = 'offershield_analysis_history'

function getHistory() {
  try {
    const saved = JSON.parse(
      localStorage.getItem(HISTORY_KEY) || '[]'
    )

    return Array.isArray(saved) ? saved : []
  } catch {
    return []
  }
}

function getResult(item) {
  return item?.result || {}
}

function getJobData(item) {
  return item?.jobData || {}
}

function getJobTitle(item) {
  const result = getResult(item)
  const jobData = getJobData(item)

  return (
    jobData.title ||
    result.job_title ||
    result.title ||
    'Untitled Job Posting'
  )
}

function getClassification(result) {
  const riskLevel = String(result?.risk_level || '').toLowerCase()
  const resultLabel = String(result?.result || '').toLowerCase()
  const explanationLabel = String(result?.risk_classification || '').toLowerCase()
  const combined = `${riskLevel} ${resultLabel} ${explanationLabel}`

  // Prefer the three-level risk classification when it is available.
  if (riskLevel === 'medium' || combined.includes('manual review')) return 'review'
  if (riskLevel === 'high' || combined.includes('potentially fraudulent')) return 'fraud'
  if (riskLevel === 'low' || combined.includes('likely genuine')) return 'genuine'

  // Backward compatibility for older saved reports.
  const rawPrediction = result?.prediction
  if (rawPrediction !== null && rawPrediction !== undefined && rawPrediction !== '') {
    const prediction = Number(rawPrediction)
    if (prediction === 1) return 'fraud'
    if (prediction === 0) return 'genuine'
  }

  if (combined.includes('fraud') || combined.includes('suspicious')) return 'fraud'
  if (combined.includes('genuine') || combined.includes('legitimate')) return 'genuine'
  return 'unknown'
}

function getDecisionScore(result) {
  const score = result?.decision_score

  if (
    score === null ||
    score === undefined ||
    score === ''
  ) {
    return null
  }

  const parsed = Number(score)

  return Number.isFinite(parsed) ? parsed : null
}

function formatFeatureName(feature) {
  return String(feature || 'Unknown feature')
    .replaceAll('_', ' ')
    .replace(/\b\w/g, character => character.toUpperCase())
}

function getSignals(result, type) {
  const key =
    type === 'fraud'
      ? 'fraud_increasing_signals'
      : 'genuine_increasing_signals'

  return Array.isArray(result?.[key])
    ? result[key]
    : []
}

function getSignalFeature(signal) {
  const feature =
    typeof signal === 'string'
      ? signal
      : signal?.feature

  return feature ? String(feature) : null
}

function getRecurrence(count) {
  if (count >= 5) {
    return {
      label: 'Frequent',
      className: 'frequent'
    }
  }

  if (count >= 2) {
    return {
      label: 'Recurring',
      className: 'recurring'
    }
  }

  return {
    label: 'Occasional',
    className: 'occasional'
  }
}

function PatternIntelligence() {
  const [history, setHistory] = useState(getHistory)
  const [searchTerm, setSearchTerm] = useState('')
  const [lastUpdated, setLastUpdated] = useState(() => new Date())

  const refreshHistory = () => {
    setHistory(getHistory())
    setLastUpdated(new Date())
  }

  useEffect(() => {
    const refreshFromStorage = () => refreshHistory()
    window.addEventListener('storage', refreshFromStorage)
    window.addEventListener('offershield:history-updated', refreshFromStorage)
    window.addEventListener('focus', refreshFromStorage)
    return () => {
      window.removeEventListener('storage', refreshFromStorage)
      window.removeEventListener('offershield:history-updated', refreshFromStorage)
      window.removeEventListener('focus', refreshFromStorage)
    }
  }, [])

  // MAIN ANALYTICS
  const analytics = useMemo(() => {
    const total = history.length

    let fraudCount = 0
    let reviewCount = 0
    let genuineCount = 0
    let unknownCount = 0

    const fraudFeatures = {}
    const genuineFeatures = {}
    const combinedFeatures = {}
    const scoreValues = []
    const trendMap = {}

    history.forEach(item => {
      const result = getResult(item)
      const classification = getClassification(result)

      if (classification === 'fraud') {
        fraudCount++
      } else if (classification === 'review') {
        reviewCount++
      } else if (classification === 'genuine') {
        genuineCount++
      } else {
        unknownCount++
      }

      const score = getDecisionScore(result)

      if (score !== null) {
        scoreValues.push(score)
      }

      // DAILY TREND
      if (item.createdAt) {
        const date = new Date(item.createdAt)

        if (!Number.isNaN(date.getTime())) {
          const dateKey = [
            date.getFullYear(),
            String(date.getMonth() + 1).padStart(2, '0'),
            String(date.getDate()).padStart(2, '0')
          ].join('-')

          if (!trendMap[dateKey]) {
            trendMap[dateKey] = {
              dateKey,
              date: date.toLocaleDateString('en-IN', {
                day: '2-digit',
                month: 'short'
              }),
              fraud: 0,
              review: 0,
              genuine: 0,
              unknown: 0
            }
          }

          trendMap[dateKey][classification]++
        }
      }

      const fraudSignals = getSignals(result, 'fraud')
      const genuineSignals = getSignals(result, 'genuine')

      // COUNT EACH FEATURE ONCE PER REPORT
      const fraudSet = new Set(
        fraudSignals
          .map(getSignalFeature)
          .filter(Boolean)
      )

      const genuineSet = new Set(
        genuineSignals
          .map(getSignalFeature)
          .filter(Boolean)
      )

      fraudSet.forEach(feature => {
        if (!fraudFeatures[feature]) {
          fraudFeatures[feature] = {
            feature,
            count: 0
          }
        }

        fraudFeatures[feature].count++

        if (!combinedFeatures[feature]) {
          combinedFeatures[feature] = {
            feature,
            fraudCount: 0,
            genuineCount: 0
          }
        }

        combinedFeatures[feature].fraudCount++
      })

      genuineSet.forEach(feature => {
        if (!genuineFeatures[feature]) {
          genuineFeatures[feature] = {
            feature,
            count: 0
          }
        }

        genuineFeatures[feature].count++

        if (!combinedFeatures[feature]) {
          combinedFeatures[feature] = {
            feature,
            fraudCount: 0,
            genuineCount: 0
          }
        }

        combinedFeatures[feature].genuineCount++
      })
    })

    const topFraudFeatures = Object.values(fraudFeatures)
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)

    const topGenuineFeatures = Object.values(genuineFeatures)
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)

    const frequencyData = Object.values(combinedFeatures)
      .sort(
        (a, b) =>
          (b.fraudCount + b.genuineCount) -
          (a.fraudCount + a.genuineCount)
      )
      .slice(0, 8)
      .map(item => ({
        ...item,
        name: formatFeatureName(item.feature)
      }))

    const averageScore =
      scoreValues.length > 0
        ? scoreValues.reduce((sum, score) => sum + score, 0) /
          scoreValues.length
        : null

    const fraudPercentage =
      total > 0 ? (fraudCount / total) * 100 : 0

    const reviewPercentage =
      total > 0 ? (reviewCount / total) * 100 : 0

    const genuinePercentage =
      total > 0 ? (genuineCount / total) * 100 : 0

    const repeatedFeatures = topFraudFeatures.filter(
      feature => feature.count >= 2
    )

    const trendData = Object.values(trendMap)
      .sort((a, b) => a.dateKey.localeCompare(b.dateKey))

    const frequentCount = Object.values(fraudFeatures)
      .filter(feature => feature.count >= 5).length

    const recurringCount = Object.values(fraudFeatures)
      .filter(
        feature => feature.count >= 2 && feature.count < 5
      ).length

    const occasionalCount = Object.values(fraudFeatures)
      .filter(feature => feature.count === 1).length

    return {
      total,
      fraudCount,
      reviewCount,
      genuineCount,
      unknownCount,
      fraudPercentage,
      reviewPercentage,
      genuinePercentage,
      averageScore,
      scoreCount: scoreValues.length,
      topFraudFeatures,
      topGenuineFeatures,
      repeatedFeatures,
      frequencyData,
      trendData,
      frequentCount,
      recurringCount,
      occasionalCount
    }
  }, [history])

  // SEARCH
  const filteredHistory = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()

    if (!query) return history

    return history.filter(item => {
      const result = getResult(item)
      const jobData = getJobData(item)

      const searchableText = [
        getJobTitle(item),
        jobData.location,
        jobData.company_profile,
        jobData.department,
        jobData.industry,
        result.risk_classification,
        result.risk_level,
        result.result
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      return searchableText.includes(query)
    })
  }, [history, searchTerm])

  // RISK DISTRIBUTION
  const chartData = [
    {
      name: 'Potentially fraudulent',
      count: analytics.fraudCount
    },
    {
      name: 'Needs manual review',
      count: analytics.reviewCount
    },
    {
      name: 'Likely genuine',
      count: analytics.genuineCount
    },
    {
      name: 'Unknown',
      count: analytics.unknownCount
    }
  ]

  // PATTERN SUMMARY
  const getPatternSummary = () => {
    if (analytics.total === 0) {
      return 'Run your first job posting analysis to start discovering patterns across your saved reports.'
    }

    if (analytics.repeatedFeatures.length === 0) {
      return 'No fraud-increasing feature has appeared in multiple saved reports yet. Analyse more postings to discover recurring patterns.'
    }

    const names = analytics.repeatedFeatures
      .slice(0, 3)
      .map(item => formatFeatureName(item.feature))
      .join(', ')

    return `The following fraud-increasing features have appeared repeatedly across your saved analyses: ${names}. These are model explanation patterns, not independent proof of fraud.`
  }

  const formatScore = score => {
    if (score === null || score === undefined) {
      return 'N/A'
    }

    return Number(score).toFixed(4)
  }

  // PROFESSIONAL PDF REPORT EXPORT
  const downloadPatternReport = () => {
    if (analytics.total === 0) {
      alert('No saved analyses are available to export.')
      return
    }

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()

    const margin = 16
    const contentWidth = pageWidth - margin * 2
    const bottomLimit = pageHeight - 21

    let y = 20

    const navy = [17, 24, 39]
    const primary = [49, 87, 213]
    const text = [31, 41, 55]
    const muted = [100, 116, 139]
    const border = [229, 233, 240]
    const red = [185, 55, 55]
    const green = [22, 130, 88]
    const lightBlue = [239, 244, 255]
    const lightRed = [254, 242, 242]
    const lightGreen = [236, 253, 245]

    const setText = (
      size = 10,
      color = text,
      bold = false
    ) => {
      doc.setFont('helvetica', bold ? 'bold' : 'normal')
      doc.setFontSize(size)
      doc.setTextColor(...color)
    }

    const drawLine = lineY => {
      doc.setDrawColor(...border)
      doc.setLineWidth(0.3)
      doc.line(
        margin,
        lineY,
        pageWidth - margin,
        lineY
      )
    }

    const checkPage = height => {
      if (y + height > bottomLimit) {
        doc.addPage()
        y = 20
        return true
      }

      return false
    }

    const addParagraph = (
      value,
      {
        size = 9,
        color = text,
        bold = false,
        gap = 3,
        indent = 0
      } = {}
    ) => {
      setText(size, color, bold)

      const lines = doc.splitTextToSize(
        String(value),
        contentWidth - indent
      )

      const lineHeight = size * 0.45 + 1.5
      const requiredHeight = lines.length * lineHeight

      checkPage(requiredHeight + gap)

      doc.text(
        lines,
        margin + indent,
        y
      )

      y += requiredHeight + gap
    }

    const addSection = (title, subtitle = '') => {
      checkPage(22)

      y += 4

      setText(12, navy, true)
      doc.text(title, margin, y)

      y += 5

      if (subtitle) {
        setText(8, muted)
        doc.text(subtitle, margin, y)
        y += 5
      }

      drawLine(y)
      y += 7
    }

    const drawKpi = (
      x,
      top,
      width,
      label,
      value,
      color
    ) => {
      doc.setFillColor(248, 250, 252)
      doc.setDrawColor(...border)

      doc.roundedRect(
        x,
        top,
        width,
        25,
        2,
        2,
        'FD'
      )

      doc.setFillColor(...color)

      doc.roundedRect(
        x,
        top,
        2,
        25,
        1,
        1,
        'F'
      )

      setText(6.5, muted, true)

      doc.text(
        label,
        x + 5,
        top + 7
      )

      setText(16, navy, true)

      doc.text(
        String(value),
        x + 5,
        top + 18
      )
    }

    const addFeatureTable = (features, type) => {
      const accent = type === 'fraud' ? red : green
      const background = type === 'fraud'
        ? lightRed
        : lightGreen

      if (!features.length) {
        addParagraph(
          'No indicators available in the saved reports.',
          { color: muted }
        )
        return
      }

      features.forEach((feature, index) => {
        const featureName = formatFeatureName(
          feature.feature
        )

        setText(8.5, text, true)

        const nameLines = doc.splitTextToSize(
          `${index + 1}. ${featureName}`,
          contentWidth - 38
        )

        const rowHeight = Math.max(
          11,
          nameLines.length * 4.5 + 5
        )

        checkPage(rowHeight + 2)

        doc.setFillColor(...background)

        doc.roundedRect(
          margin,
          y - 4,
          contentWidth,
          rowHeight,
          1.5,
          1.5,
          'F'
        )

        setText(8.5, text, true)

        doc.text(
          nameLines,
          margin + 3,
          y + 1
        )

        setText(8, accent, true)

        doc.text(
          `${feature.count} report(s)`,
          pageWidth - margin - 3,
          y + 1,
          { align: 'right' }
        )

        y += rowHeight + 1
      })

      y += 2
    }

    // REPORT HEADER
    doc.setFillColor(...navy)
    doc.rect(0, 0, pageWidth, 11, 'F')

    setText(7, [255, 255, 255], true)

    doc.text(
      'OFFERSHIELD AI  /  INTELLIGENCE REPORT',
      margin,
      7
    )

    // TITLE CARD
    doc.setFillColor(...lightBlue)

    doc.roundedRect(
      margin,
      19,
      contentWidth,
      37,
      3,
      3,
      'F'
    )

    setText(8, primary, true)

    doc.text(
      'JOB SCAM DETECTION PLATFORM',
      margin + 6,
      27
    )

    setText(19, navy, true)

    doc.text(
      'Pattern Intelligence',
      margin + 6,
      37
    )

    setText(8, muted)

    doc.text(
      'Saved analysis trends and recurring model indicators',
      margin + 6,
      44
    )

    setText(7.5, muted)

    doc.text(
      `Generated ${new Date().toLocaleString('en-IN')}`,
      margin + 6,
      50
    )

    y = 65

    // EXECUTIVE SUMMARY
    addSection(
      'Executive Summary',
      'Overview of your saved job posting analyses'
    )

    const cardGap = 4
    const cardWidth =
      (contentWidth - cardGap * 3) / 4

    drawKpi(
      margin,
      y,
      cardWidth,
      'TOTAL REPORTS',
      analytics.total,
      primary
    )

    drawKpi(
      margin + cardWidth + cardGap,
      y,
      cardWidth,
      'POTENTIALLY FRAUDULENT',
      analytics.fraudCount,
      red
    )

    drawKpi(
      margin + (cardWidth + cardGap) * 2,
      y,
      cardWidth,
      'NEEDS MANUAL REVIEW',
      analytics.reviewCount,
      [183, 121, 31]
    )

    drawKpi(
      margin + (cardWidth + cardGap) * 3,
      y,
      cardWidth,
      'LIKELY GENUINE',
      analytics.genuineCount,
      green
    )

    y += 33

    addParagraph(
      `Fraud classification share: ${analytics.fraudPercentage.toFixed(1)}%`
    )

    addParagraph(
      `Manual review share: ${analytics.reviewPercentage.toFixed(1)}%`
    )

    addParagraph(
      `Genuine classification share: ${analytics.genuinePercentage.toFixed(1)}%`
    )

    addParagraph(
      `Reports with unknown classification: ${analytics.unknownCount}`
    )

    // FRAUD INDICATORS
    addSection(
      'Fraud-Increasing Indicators',
      'Features appearing in model explanations as increasing the fraud decision score'
    )

    addFeatureTable(
      analytics.topFraudFeatures,
      'fraud'
    )

    // GENUINE INDICATORS
    addSection(
      'Genuine-Increasing Indicators',
      'Features appearing in model explanations as increasing the genuine decision score'
    )

    addFeatureTable(
      analytics.topGenuineFeatures,
      'genuine'
    )

    // RECURRENCE OVERVIEW
    addSection(
      'Pattern Recurrence Overview',
      'Frequency categories based on saved reports'
    )

    const recurrenceItems = [
      {
        label: 'Frequent',
        count: analytics.frequentCount,
        description: '5 or more reports',
        color: green
      },
      {
        label: 'Recurring',
        count: analytics.recurringCount,
        description: '2 to 4 reports',
        color: primary
      },
      {
        label: 'Occasional',
        count: analytics.occasionalCount,
        description: '1 report',
        color: muted
      }
    ]

    const recurrenceGap = 4
    const recurrenceWidth =
      (contentWidth - recurrenceGap * 2) / 3

    checkPage(32)

    recurrenceItems.forEach((item, index) => {
      const x =
        margin + index * (recurrenceWidth + recurrenceGap)

      doc.setFillColor(248, 250, 252)
      doc.setDrawColor(...border)

      doc.roundedRect(
        x,
        y,
        recurrenceWidth,
        25,
        2,
        2,
        'FD'
      )

      setText(8, item.color, true)

      doc.text(
        item.label,
        x + 4,
        y + 7
      )

      setText(15, navy, true)

      doc.text(
        String(item.count),
        x + 4,
        y + 16
      )

      setText(6.5, muted)

      doc.text(
        item.description,
        x + 4,
        y + 21
      )
    })

    y += 32

    addParagraph(
      'These frequency categories describe patterns in your saved history only. They do not measure fraud severity or establish a causal relationship.',
      { size: 8, color: muted }
    )

    // DECISION SCORE INSIGHTS
    addSection(
      'Model Decision Score Insights',
      'LinearSVC model statistics'
    )

    addParagraph(
      `Average decision score: ${formatScore(analytics.averageScore)}`,
      { bold: true }
    )

    addParagraph(
      `Reports with score data: ${analytics.scoreCount}`
    )

    addParagraph(
      `Reports without score data: ${analytics.total - analytics.scoreCount}`
    )

    addParagraph(
      'Important: LinearSVC decision scores are not probabilities. Their magnitude must not be interpreted as a percentage likelihood of fraud.',
      { size: 8, color: muted }
    )

    // SAVED ANALYSES
    addSection(
      'Analyses Included',
      'Saved job posting reports contributing to these insights'
    )

    history.forEach((item, index) => {
      const result = getResult(item)
      const classification = getClassification(result)
      const score = getDecisionScore(result)

      const status =
        classification === 'fraud'
          ? 'Potentially Fraudulent'
          : classification === 'review'
            ? 'Needs Manual Review'
            : classification === 'genuine'
              ? 'Likely Genuine'
              : 'Unknown'

      const statusColor =
        classification === 'fraud'
          ? red
          : classification === 'review'
            ? [183, 121, 31]
            : classification === 'genuine'
              ? green
              : muted

      const date = item.createdAt
        ? new Date(item.createdAt).toLocaleString('en-IN')
        : 'Date unavailable'

      checkPage(25)

      doc.setFillColor(248, 250, 252)

      doc.roundedRect(
        margin,
        y - 4,
        contentWidth,
        20,
        2,
        2,
        'F'
      )

      setText(8.5, navy, true)

      const jobTitleLines = doc.splitTextToSize(
        `${index + 1}. ${getJobTitle(item)}`,
        contentWidth - 45
      )

      doc.text(
        jobTitleLines,
        margin + 4,
        y + 2
      )

      setText(7.5, muted)

      doc.text(
        `Date: ${date}`,
        margin + 4,
        y + 8
      )

      setText(7.5, statusColor, true)

      doc.text(
        status,
        pageWidth - margin - 4,
        y + 2,
        { align: 'right' }
      )

      setText(7.5, muted)

      doc.text(
        `Decision score: ${formatScore(score)}`,
        pageWidth - margin - 4,
        y + 8,
        { align: 'right' }
      )

      y += 24
    })

    // FINAL DISCLAIMER
    addSection('Important Disclaimer')

    addParagraph(
      'This report is generated from locally saved OfferShield AI analyses. Repeated model signals do not independently verify a company, recruiter, or job posting. Always conduct independent checks before sharing personal information or accepting an offer.',
      { size: 8.5 }
    )

    // PAGE NUMBERS AND FOOTERS
    const pageCount = doc.internal.getNumberOfPages()

    for (let page = 1; page <= pageCount; page++) {
      doc.setPage(page)

      doc.setDrawColor(...border)

      doc.line(
        margin,
        pageHeight - 14,
        pageWidth - margin,
        pageHeight - 14
      )

      setText(7, muted)

      doc.text(
        'OfferShield AI | Job Scam Pattern Intelligence',
        margin,
        pageHeight - 8
      )

      doc.text(
        `Page ${page} of ${pageCount}`,
        pageWidth - margin,
        pageHeight - 8,
        { align: 'right' }
      )
    }

    doc.save(
      'OfferShield-Pattern-Intelligence-Report.pdf'
    )
  }

  // SIGNAL LIST
  const renderFeatureList = (
    features,
    emptyMessage
  ) => {
    if (features.length === 0) {
      return (
        <div className="pattern-empty-message">
          {emptyMessage}
        </div>
      )
    }

    return (
      <div className="pattern-feature-list">
        {features.map((feature, index) => {
          const recurrence = getRecurrence(feature.count)

          return (
            <div
              className="pattern-feature-row"
              key={feature.feature}
            >
              <div className="pattern-feature-rank">
                {index + 1}
              </div>

              <div className="pattern-feature-details">
                <strong>
                  {formatFeatureName(feature.feature)}
                </strong>

                <span>
                  Appeared in {feature.count}{' '}
                  {feature.count === 1
                    ? 'analysis'
                    : 'analyses'}
                </span>

                <span
                  className={`pattern-recurrence-badge ${recurrence.className}`}
                >
                  {recurrence.label}
                </span>
              </div>

              <div className="pattern-feature-count">
                {feature.count}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="pattern-page">

      {/* PAGE HEADER */}

      <div className="pattern-page-header">
        <div className="pattern-heading-content">
          <div className="pattern-heading-icon">
            <BrainCircuit size={25} />
          </div>

          <div>
            <h1>Job Scam Pattern Intelligence</h1>

            <p>
              Discover recurring risk indicators across your
              saved job posting analyses.
            </p>
          </div>
        </div>

        <div className="pattern-header-actions">
          <button
            className="pattern-refresh-button"
            onClick={downloadPatternReport}
            type="button"
            disabled={analytics.total === 0}
          >
            <Download size={16} />
            Download PDF
          </button>

          <button
            className="pattern-refresh-button"
            onClick={refreshHistory}
            type="button"
            aria-label="Refresh saved analysis data"
            title="Reload saved analyses from this browser"
          >
            <RefreshCw size={16} />
            Refresh Data
          </button>
        </div>
      </div>

      <p className="pattern-refresh-meta" aria-live="polite">
        Updated {lastUpdated.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
      </p>

      {/* INFORMATION NOTICE */}

      <div className="pattern-info-notice">
        <Info size={19} />

        <p>
          Insights are calculated from your saved OfferShield
          analyses. They represent patterns in your own analysis
          history and do not establish real-world fraud trends.
        </p>
      </div>

      {/* SUMMARY CARDS */}

      <div className="pattern-stats-grid">

        <div className="pattern-stat-card">
          <div className="pattern-stat-top">
            <span>Total Analyses</span>

            <div className="pattern-stat-icon blue">
              <Layers3 size={20} />
            </div>
          </div>

          <h2>{analytics.total}</h2>

          <p>Saved job posting reports</p>
        </div>

        <div className="pattern-stat-card">
          <div className="pattern-stat-top">
            <span>Potentially Fraudulent</span>

            <div className="pattern-stat-icon red">
              <ShieldAlert size={20} />
            </div>
          </div>

          <h2>{analytics.fraudCount}</h2>

          <p>
            {analytics.fraudPercentage.toFixed(1)}% of saved
            analyses
          </p>
        </div>

        <div className="pattern-stat-card">
          <div className="pattern-stat-top">
            <span>Needs Manual Review</span>
            <div className="pattern-stat-icon amber">
              <AlertTriangle size={20} />
            </div>
          </div>
          <h2>{analytics.reviewCount}</h2>
          <p>{analytics.reviewPercentage.toFixed(1)}% of saved analyses</p>
        </div>

        <div className="pattern-stat-card">
          <div className="pattern-stat-top">
            <span>Likely Genuine</span>

            <div className="pattern-stat-icon green">
              <ShieldCheck size={20} />
            </div>
          </div>

          <h2>{analytics.genuineCount}</h2>

          <p>
            {analytics.genuinePercentage.toFixed(1)}% of saved
            analyses
          </p>
        </div>

        <div className="pattern-stat-card">
          <div className="pattern-stat-top">
            <span>Repeated Risk Patterns</span>

            <div className="pattern-stat-icon orange">
              <Activity size={20} />
            </div>
          </div>

          <h2>{analytics.repeatedFeatures.length}</h2>

          <p>Indicators appearing more than once</p>
        </div>

      </div>

      {/* RISK DISTRIBUTION */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <BarChart3 size={20} />
              Risk Distribution
            </h2>

            <p>
              Classification breakdown of your saved analyses.
            </p>
          </div>
        </div>

        {analytics.total === 0 ? (
          <div className="pattern-empty-state">
            <BarChart3 size={35} />

            <h3>No analysis data available</h3>

            <p>
              Analyse a job posting to populate your intelligence
              dashboard.
            </p>
          </div>
        ) : (
          <div className="pattern-chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={chartData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 15
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#E5E9F0"
                />

                <XAxis
                  dataKey="name"
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />

                <Tooltip />

                <Bar
                  dataKey="count"
                  name="Analyses"
                  radius={[6, 6, 0, 0]}
                  barSize={55}
                >
                  <Cell fill="#D64545" />
                  <Cell fill="#B7791F" />
                  <Cell fill="#3157D5" />
                  <Cell fill="#16845B" />
                  <Cell fill="#94A3B8" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      {/* RISK TREND ANALYSIS */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <TrendingUp size={20} />
              Risk Trend Analysis
            </h2>

            <p>
              Daily classification trends based on the dates
              of your saved reports.
            </p>
          </div>
        </div>

        {analytics.trendData.length === 0 ? (
          <div className="pattern-empty-state">
            <CalendarDays size={32} />

            <h3>No dated analysis records</h3>

            <p>
              New analyses with saved dates will appear here.
            </p>
          </div>
        ) : (
          <div className="pattern-chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={analytics.trendData}
                margin={{
                  top: 15,
                  right: 20,
                  left: 0,
                  bottom: 15
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#E5E9F0"
                />

                <XAxis
                  dataKey="date"
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fill: '#64748B', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />

                <Tooltip />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="fraud"
                  name="Potentially fraudulent"
                  stroke="#DC5555"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="review"
                  name="Needs manual review"
                  stroke="#B7791F"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="genuine"
                  name="Likely genuine"
                  stroke="#21976B"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />

                <Line
                  type="monotone"
                  dataKey="unknown"
                  name="Unknown"
                  stroke="#94A3B8"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      {/* SIGNAL FREQUENCY ANALYSIS */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <Activity size={20} />
              Signal Frequency Analysis
            </h2>

            <p>
              Compare how frequently the model identifies
              each indicator across your saved reports.
            </p>
          </div>
        </div>

        {analytics.frequencyData.length === 0 ? (
          <div className="pattern-empty-state">
            <Activity size={32} />

            <h3>No signal frequency data</h3>

            <p>
              Run job analyses to discover recurring indicators.
            </p>
          </div>
        ) : (
          <div className="pattern-chart-container">
            <ResponsiveContainer width="100%" height={340}>
              <BarChart
                data={analytics.frequencyData}
                layout="vertical"
                margin={{
                  top: 10,
                  right: 20,
                  left: 20,
                  bottom: 10
                }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                  stroke="#E5E9F0"
                />

                <XAxis
                  type="number"
                  allowDecimals={false}
                  tick={{ fill: '#64748B', fontSize: 12 }}
                />

                <YAxis
                  type="category"
                  dataKey="name"
                  width={190}
                  tick={{ fill: '#64748B', fontSize: 11 }}
                />

                <Tooltip />

                <Legend />

                <Bar
                  dataKey="fraudCount"
                  name="Fraud-increasing"
                  fill="#DC5555"
                  radius={[0, 4, 4, 0]}
                />

                <Bar
                  dataKey="genuineCount"
                  name="Genuine-increasing"
                  fill="#21976B"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </section>

      {/* PATTERN RECURRENCE SUMMARY */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <Repeat2 size={20} />
              Pattern Recurrence Overview
            </h2>

            <p>
              Frequency categories based on the number of
              saved reports containing each fraud-increasing
              indicator.
            </p>
          </div>
        </div>

        <div className="pattern-recurrence-grid">

          <div className="pattern-recurrence-card">
            <span className="pattern-recurrence-badge frequent">
              Frequent
            </span>

            <h2>{analytics.frequentCount}</h2>

            <p>Appearing in 5 or more reports</p>
          </div>

          <div className="pattern-recurrence-card">
            <span className="pattern-recurrence-badge recurring">
              Recurring
            </span>

            <h2>{analytics.recurringCount}</h2>

            <p>Appearing in 2 to 4 reports</p>
          </div>

          <div className="pattern-recurrence-card">
            <span className="pattern-recurrence-badge occasional">
              Occasional
            </span>

            <h2>{analytics.occasionalCount}</h2>

            <p>Appearing in 1 report</p>
          </div>

        </div>

        <div className="pattern-score-disclaimer">
          <Info size={17} />

          <p>
            These categories describe observed frequency in
            your saved history only. They do not measure
            fraud severity or establish a causal relationship.
          </p>
        </div>
      </section>

      {/* FRAUD AND GENUINE SIGNAL LISTS */}

      <div className="pattern-two-column">

        <section className="pattern-section">
          <div className="pattern-section-heading">
            <div>
              <h2>
                <AlertTriangle size={20} />
                Top Fraud-Increasing Indicators
              </h2>

              <p>
                Features most frequently appearing in
                fraud-increasing explanations.
              </p>
            </div>
          </div>

          {renderFeatureList(
            analytics.topFraudFeatures,
            'No fraud-increasing signals are available yet. Run more analyses to build this report.'
          )}
        </section>

        <section className="pattern-section">
          <div className="pattern-section-heading">
            <div>
              <h2>
                <ShieldCheck size={20} />
                Genuine-Increasing Indicators
              </h2>

              <p>
                Features most frequently appearing in
                genuine-increasing explanations.
              </p>
            </div>
          </div>

          {renderFeatureList(
            analytics.topGenuineFeatures,
            'No genuine-increasing signals are available yet.'
          )}
        </section>

      </div>

      {/* DECISION SCORE INSIGHTS */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <Target size={20} />
              Model Decision Score Insights
            </h2>

            <p>
              Summary of decision scores returned by the
              LinearSVC model.
            </p>
          </div>
        </div>

        <div className="pattern-score-grid">

          <div className="pattern-score-card">
            <span>Average Decision Score</span>

            <strong>
              {formatScore(analytics.averageScore)}
            </strong>

            <p>
              {analytics.scoreCount} reports with available scores
            </p>
          </div>

          <div className="pattern-score-card">
            <span>Reports With Score Data</span>

            <strong>{analytics.scoreCount}</strong>

            <p>Valid numerical decision scores</p>
          </div>

          <div className="pattern-score-card">
            <span>Reports Without Score Data</span>

            <strong>
              {analytics.total - analytics.scoreCount}
            </strong>

            <p>Missing or unavailable scores</p>
          </div>

        </div>

        <div className="pattern-score-disclaimer">
          <Info size={17} />

          <p>
            A LinearSVC decision score is not a probability.
            Its magnitude should not be interpreted as a
            percentage likelihood of fraud.
          </p>
        </div>
      </section>

      {/* PATTERN SUMMARY */}

      <section className="pattern-insight-section">
        <div className="pattern-insight-icon">
          <Lightbulb size={23} />
        </div>

        <div>
          <h2>Pattern Intelligence Summary</h2>

          <p>{getPatternSummary()}</p>
        </div>
      </section>

      {/* SAVED ANALYSES */}

      <section className="pattern-section">
        <div className="pattern-section-heading">
          <div>
            <h2>
              <Search size={20} />
              Analyses Included
            </h2>

            <p>
              Explore the reports contributing to these insights.
            </p>
          </div>
        </div>

        <div className="pattern-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search job title, location or company information..."
            value={searchTerm}
            onChange={event => setSearchTerm(event.target.value)}
          />
        </div>

        {filteredHistory.length === 0 ? (
          <div className="pattern-empty-state">
            <Search size={30} />

            <h3>No matching analyses</h3>

            <p>
              Try another search term or clear your search.
            </p>
          </div>
        ) : (
          <div className="pattern-analysis-list">
            {filteredHistory.map((item, index) => {
              const result = getResult(item)
              const classification = getClassification(result)
              const score = getDecisionScore(result)

              return (
                <div
                  className="pattern-analysis-row"
                  key={item.id || `${getJobTitle(item)}-${index}`}
                >
                  <div className="pattern-analysis-main">
                    <div className="pattern-analysis-icon">
                      <BarChart3 size={19} />
                    </div>

                    <div>
                      <strong>{getJobTitle(item)}</strong>

                      <span>
                        {item.createdAt
                          ? new Date(item.createdAt).toLocaleString()
                          : 'Date unavailable'}
                      </span>
                    </div>
                  </div>

                  <div className="pattern-analysis-meta">
                    <span
                      className={`pattern-status ${
                        classification === 'fraud'
                          ? 'fraud'
                          : classification === 'review'
                            ? 'review'
                            : classification === 'genuine'
                              ? 'genuine'
                              : 'unknown'
                      }`}
                    >
                      {classification === 'fraud'
                        ? 'Potentially Fraudulent'
                        : classification === 'review'
                          ? 'Needs Manual Review'
                          : classification === 'genuine'
                            ? 'Likely Genuine'
                            : 'Unknown'}
                    </span>

                    <span className="pattern-analysis-score">
                      Score: {formatScore(score)}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* FOOTER DISCLAIMER */}

      <div className="pattern-footer-disclaimer">
        <Info size={17} />

        <p>
          Pattern Intelligence is an analytical view of your
          locally saved reports. Repeated model signals do not
          independently verify a company, recruiter or job
          posting. Always conduct independent checks before
          sharing personal information or accepting an offer.
        </p>
      </div>

    </div>
  )
}

export default PatternIntelligence