import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { jsPDF } from 'jspdf'
import JSZip from 'jszip'

import {
  Clock3,
  ShieldCheck,
  ShieldAlert,
  FileSearch,
  Trash2,
  ArrowUpRight,
  BriefcaseBusiness,
  CalendarDays,
  AlertTriangle,
  Download,
  Archive,
  Search,
  SlidersHorizontal,
  RotateCcw
} from 'lucide-react'

const STORAGE_KEY = 'offershield_analysis_history'

function History() {
  const navigate = useNavigate()

  const [history, setHistory] = useState([])
  const [isExporting, setIsExporting] = useState(false)

  // Search and filter states
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortOrder, setSortOrder] = useState('newest')

  // Load saved analysis history
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem(STORAGE_KEY)

      if (savedHistory) {
        const parsedHistory = JSON.parse(savedHistory)

        if (Array.isArray(parsedHistory)) {
          setHistory(parsedHistory)
        }
      }
    } catch (error) {
      console.error('Unable to load analysis history:', error)
      setHistory([])
    }
  }, [])

  // Search, filter and sort history
  const filteredHistory = useMemo(() => {
    let records = [...history]

    const search = searchTerm.trim().toLowerCase()

    if (search) {
      records = records.filter(item => {
        const result = item.result || {}

        const searchableText = [
          result.job_title,
          result.company_name,
          result.company,
          result.location,
          result.department,
          result.industry,
          result.company_profile
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        return searchableText.includes(search)
      })
    }

    if (statusFilter === 'fraudulent') {
      records = records.filter(
        item => item.result?.prediction === 1
      )
    } else if (statusFilter === 'genuine') {
      records = records.filter(
        item => item.result?.prediction === 0
      )
    }

    records.sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime() || 0
      const dateB = new Date(b.createdAt).getTime() || 0

      return sortOrder === 'newest'
        ? dateB - dateA
        : dateA - dateB
    })

    return records
  }, [history, searchTerm, statusFilter, sortOrder])

  // Check whether any filters are active
  const hasActiveFilters =
    searchTerm.trim() !== '' ||
    statusFilter !== 'all' ||
    sortOrder !== 'newest'

  // Clear all filters
  function handleClearFilters() {
    setSearchTerm('')
    setStatusFilter('all')
    setSortOrder('newest')
  }

  // Delete an individual analysis
  function handleDelete(id) {
    const updatedHistory = history.filter(
      item => item.id !== id
    )

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(updatedHistory)
    )

    setHistory(updatedHistory)
  }

  // Open a previous analysis report
  function handleViewResult(item) {
    navigate('/results', {
      state: {
        result: item.result
      }
    })
  }

  // Format the saved date
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

  // Generate a safe PDF filename
  function getSafeFilename(item, index = 0) {
    const title = item.result?.job_title || 'job-analysis'

    const safeTitle = title
      .replace(/[^a-z0-9]/gi, '-')
      .replace(/-+/g, '-')
      .toLowerCase()
      .slice(0, 45)

    return `OfferShield-${safeTitle || 'report'}-${index + 1}.pdf`
  }

  // Safely add wrapped text to PDF pages
  function addPdfText(doc, text, x, y, maxWidth = 175) {
    const lines = doc.splitTextToSize(String(text), maxWidth)

    for (const line of lines) {
      if (y > 275) {
        doc.addPage()
        y = 20
      }

      doc.text(line, x, y)
      y += 7
    }

    return y
  }

  // Generate an analysis PDF
  function generatePDF(item) {
    const result = item.result || {}
    const doc = new jsPDF()

    let y = 20

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(20)
    doc.text('OfferShield AI', 15, y)

    y += 10

    doc.setFontSize(11)
    doc.setFont('helvetica', 'normal')
    doc.text('JOB FRAUD DETECTION REPORT', 15, y)

    y += 12

    doc.setDrawColor(210, 215, 225)
    doc.line(15, y, 195, y)

    y += 12

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.text('Job Information', 15, y)

    y += 9

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)

    y = addPdfText(
      doc,
      `Job Title: ${result.job_title || 'Untitled job posting'}`,
      15,
      y
    )

    y = addPdfText(
      doc,
      `Analysis Date: ${formatDate(item.createdAt)}`,
      15,
      y
    )

    y += 5

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.text('AI Prediction', 15, y)

    y += 9

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(10)

    y = addPdfText(
      doc,
      `Classification: ${result.risk_classification || 'Not available'}`,
      15,
      y
    )

    y = addPdfText(
      doc,
      `Prediction: ${
        result.prediction === 1
          ? 'Potentially Fraudulent'
          : 'Genuine'
      }`,
      15,
      y
    )

    y = addPdfText(
      doc,
      `Decision Score: ${
        Number.isFinite(Number(result.decision_score))
          ? Number(result.decision_score).toFixed(6)
          : 'Not available'
      }`,
      15,
      y
    )

    y = addPdfText(
      doc,
      `Model Threshold: ${
        Number.isFinite(Number(result.threshold))
          ? Number(result.threshold).toFixed(6)
          : 'Not available'
      }`,
      15,
      y
    )

    y += 5

    const explanation =
      result.explanation ||
      result.explainability ||
      {}

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(14)
    doc.text('Explainable AI Signals', 15, y)

    y += 9

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(10)
    doc.text('Fraud-increasing signals', 15, y)

    y += 7

    doc.setFont('helvetica', 'normal')

    const fraudSignals =
      explanation.fraud_increasing_signals || []

    if (fraudSignals.length > 0) {
      fraudSignals.forEach(signal => {
        const name =
          typeof signal === 'string'
            ? signal
            : signal.feature || signal.name || JSON.stringify(signal)

        y = addPdfText(doc, `- ${name}`, 18, y)
      })
    } else {
      y = addPdfText(
        doc,
        'Signal details were not available in the saved report.',
        18,
        y
      )
    }

    y += 3

    doc.setFont('helvetica', 'bold')
    doc.text('Genuine-increasing signals', 15, y)

    y += 7

    doc.setFont('helvetica', 'normal')

    const genuineSignals =
      explanation.genuine_increasing_signals || []

    if (genuineSignals.length > 0) {
      genuineSignals.forEach(signal => {
        const name =
          typeof signal === 'string'
            ? signal
            : signal.feature || signal.name || JSON.stringify(signal)

        y = addPdfText(doc, `- ${name}`, 18, y)
      })
    } else {
      y = addPdfText(
        doc,
        'Signal details were not available in the saved report.',
        18,
        y
      )
    }

    const verification =
      result.mathematical_verification ||
      explanation.mathematical_verification

    if (verification) {
      y += 5

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(14)
      doc.text('Mathematical Verification', 15, y)

      y += 9

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(10)

      y = addPdfText(
        doc,
        `Verification Status: ${
          verification.verified === true
            ? 'Verified'
            : 'Not verified'
        }`,
        15,
        y
      )

      if (verification.reconstructed_score !== undefined) {
        y = addPdfText(
          doc,
          `Reconstructed Score: ${verification.reconstructed_score}`,
          15,
          y
        )
      }

      if (verification.difference !== undefined) {
        y = addPdfText(
          doc,
          `Difference: ${verification.difference}`,
          15,
          y
        )
      }
    }

    y += 8

    doc.setFont('helvetica', 'bold')
    doc.setFontSize(12)
    doc.text('Important Disclaimer', 15, y)

    y += 8

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)

    addPdfText(
      doc,
      'OfferShield AI provides a machine learning-based risk assessment, not a definitive determination of fraud. Decision scores are not probabilities. A genuine prediction does not guarantee that an employer or job posting is legitimate. Independently verify employers, recruiters, contact details and application links before sharing personal information or accepting an offer.',
      15,
      y
    )

    const pageCount = doc.internal.getNumberOfPages()

    for (let page = 1; page <= pageCount; page++) {
      doc.setPage(page)
      doc.setFontSize(8)
      doc.setTextColor(120)

      doc.text(
        `OfferShield AI | Page ${page} of ${pageCount}`,
        105,
        290,
        { align: 'center' }
      )
    }

    return doc
  }

  // Download an individual analysis PDF
  function handleDownloadPDF(item) {
    try {
      const doc = generatePDF(item)
      doc.save(getSafeFilename(item))
    } catch (error) {
      console.error('PDF generation failed:', error)
      alert('Unable to generate the PDF report. Please try again.')
    }
  }

  // Download all analysis reports inside one ZIP
  async function handleDownloadAll() {
    if (history.length === 0 || isExporting) {
      return
    }

    setIsExporting(true)

    try {
      const zip = new JSZip()

      history.forEach((item, index) => {
        const doc = generatePDF(item)

        zip.file(
          getSafeFilename(item, index),
          doc.output('blob')
        )
      })

      const zipBlob = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: {
          level: 6
        }
      })

      const downloadUrl = URL.createObjectURL(zipBlob)
      const link = document.createElement('a')

      link.href = downloadUrl
      link.download = 'OfferShield-All-Reports.zip'

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      setTimeout(() => {
        URL.revokeObjectURL(downloadUrl)
      }, 1000)

    } catch (error) {
      console.error('Bulk export failed:', error)
      alert('Unable to export all reports. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="history-page">

      <div className="history-page-heading">
        <div>
          <p className="eyebrow">YOUR ANALYSIS RECORDS</p>
          <h1>Analysis History</h1>
          <p>
            Review previously analysed job opportunities
            and revisit their machine learning reports.
          </p>
        </div>

        <div className="history-heading-icon">
          <Clock3 size={27} />
        </div>
      </div>

      <section className="history-summary">
        <div className="history-summary-icon">
          <BriefcaseBusiness size={21} />
        </div>

        <div>
          <span>TOTAL ANALYSES</span>
          <h2>{history.length}</h2>
          <p>Saved job analysis reports</p>
        </div>
      </section>

      <section className="history-content">

        <div className="history-section-heading">
          <div>
            <h2>Previous analyses</h2>
            <p>
              Showing {filteredHistory.length} of {history.length} reports.
            </p>
          </div>

          {history.length > 0 && (
            <button
              type="button"
              className="history-view-button"
              onClick={handleDownloadAll}
              disabled={isExporting}
              title="Download all reports as a ZIP file"
            >
              {isExporting ? (
                <>
                  Preparing ZIP...
                  <Archive size={16} />
                </>
              ) : (
                <>
                  Download All
                  <Download size={16} />
                </>
              )}
            </button>
          )}
        </div>

        {/* Search and filters */}
        {history.length > 0 && (
          <div className="history-filters">

            <div className="history-search-box">
              <Search size={18} />

              <input
                type="text"
                placeholder="Search job title, company or location..."
                value={searchTerm}
                onChange={event => setSearchTerm(event.target.value)}
              />
            </div>

            <div className="history-filter-control">
              <SlidersHorizontal size={17} />

              <select
                value={statusFilter}
                onChange={event => setStatusFilter(event.target.value)}
                aria-label="Filter by prediction status"
              >
                <option value="all">All statuses</option>
                <option value="genuine">Genuine</option>
                <option value="fraudulent">Potentially Fraudulent</option>
              </select>
            </div>

            <div className="history-filter-control">
              <CalendarDays size={17} />

              <select
                value={sortOrder}
                onChange={event => setSortOrder(event.target.value)}
                aria-label="Sort analysis history"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </div>

            {hasActiveFilters && (
              <button
                type="button"
                className="history-clear-filters"
                onClick={handleClearFilters}
              >
                <RotateCcw size={15} />
                Clear filters
              </button>
            )}

          </div>
        )}

        {history.length === 0 ? (

          <div className="history-empty-state">
            <div className="history-empty-icon">
              <FileSearch size={30} />
            </div>

            <h3>No analysis history yet</h3>

            <p>
              Your completed job analyses will appear here.
              Start by analysing your first job opportunity.
            </p>

            <button
              className="btn btn-primary"
              onClick={() => navigate('/analyse')}
            >
              Analyse a job
              <ArrowUpRight size={17} />
            </button>
          </div>

        ) : filteredHistory.length === 0 ? (

          <div className="history-empty-state">
            <div className="history-empty-icon">
              <Search size={30} />
            </div>

            <h3>No matching analyses found</h3>

            <p>
              Try changing your search or filter settings.
            </p>

            <button
              className="btn btn-primary"
              onClick={handleClearFilters}
            >
              <RotateCcw size={16} />
              Clear filters
            </button>
          </div>

        ) : (

          <div className="history-list">
            {filteredHistory.map(item => {
              const result = item.result || {}
              const isFraudulent = result.prediction === 1

              return (
                <article
                  className="history-card"
                  key={item.id}
                >
                  <div className={`history-result-icon ${
                    isFraudulent
                      ? 'history-fraud-icon'
                      : 'history-genuine-icon'
                  }`}>
                    {isFraudulent
                      ? <ShieldAlert size={22} />
                      : <ShieldCheck size={22} />
                    }
                  </div>

                  <div className="history-card-main">
                    <div className="history-card-title">
                      <h3>
                        {result.job_title || 'Untitled job posting'}
                      </h3>

                      <span className={`history-classification ${
                        isFraudulent
                          ? 'history-classification-fraud'
                          : 'history-classification-genuine'
                      }`}>
                        {result.risk_classification || 'Not available'}
                      </span>
                    </div>

                    <div className="history-card-meta">
                      <span>
                        <CalendarDays size={14} />
                        {formatDate(item.createdAt)}
                      </span>

                      <span>
                        Decision score:{' '}
                        {Number.isFinite(Number(result.decision_score))
                          ? Number(result.decision_score).toFixed(4)
                          : 'Not available'}
                      </span>
                    </div>
                  </div>

                  <div className="history-card-actions">
                    <button
                      className="history-view-button"
                      onClick={() => handleViewResult(item)}
                    >
                      View report
                      <ArrowUpRight size={16} />
                    </button>

                    <button
                      className="history-view-button"
                      onClick={() => handleDownloadPDF(item)}
                      title="Download PDF report"
                    >
                      PDF
                      <Download size={16} />
                    </button>

                    <button
                      className="history-delete-button"
                      onClick={() => handleDelete(item.id)}
                      aria-label={`Delete ${result.job_title || 'analysis'}`}
                      title="Delete analysis"
                    >
                      <Trash2 size={17} />
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        )}

      </section>

      <div className="history-disclaimer">
        <AlertTriangle size={18} />

        <p>
          History is stored locally in this browser.
          Clearing browser storage may permanently remove these records.
        </p>
      </div>

    </div>
  )
}

export default History
