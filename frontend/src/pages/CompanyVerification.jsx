
import { useState } from 'react'
import {
  ShieldCheck,
  ShieldAlert,
  Building2,
  FileText,
  Mail,
  ClipboardCheck,
  BriefcaseBusiness,
  Gift,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  LoaderCircle,
  Search,
  RotateCcw,
  Info,
  BrainCircuit,
  TrendingUp,
  TrendingDown,
  Calculator,
  Lightbulb,
  ExternalLink,
  LockKeyhole,
  Wallet,
  Globe,
  Check
} from 'lucide-react'

const API_BASE_URL = 'http://127.0.0.1:8000'

const initialFormData = {
  title: '',
  location: '',
  department: '',
  salary_range: '',
  company_profile: '',
  description: '',
  requirements: '',
  benefits: '',
  telecommuting: 0,
  has_company_logo: 0,
  has_questions: 0,
  employment_type: 'Internship',
  required_experience: 'Not Specified',
  required_education: 'Not Specified',
  industry: '',
  function: ''
}

const checkIcons = {
  'Company profile': Building2,
  'Job description': FileText,
  'Contact information': Mail,
  'Application instructions': ClipboardCheck,
  'Job title': BriefcaseBusiness,
  'Benefits information': Gift
}

async function postToApi(endpoint, formData) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map(item => item.msg).join(', ')
      : data.detail || `Request to ${endpoint} failed.`

    throw new Error(message)
  }

  return data
}

function formatContribution(value) {
  const number = Number(value)

  if (!Number.isFinite(number)) return 'N/A'

  return `${number > 0 ? '+' : ''}${number.toFixed(6)}`
}

function ContributionList({ title, signals, type }) {
  const isFraud = type === 'fraud'
  const Icon = isFraud ? TrendingUp : TrendingDown

  return (
    <div className={`explanation-signal-section ${isFraud ? 'fraud-signals' : 'genuine-signals'}`}>
      <div className="explanation-signal-heading">
        <Icon size={20} />
        <div>
          <h3>{title}</h3>
          <p>
            {isFraud
              ? 'Features pushing the model towards a fraudulent prediction.'
              : 'Features pushing the model towards a genuine prediction.'}
          </p>
        </div>
      </div>

      {Array.isArray(signals) && signals.length > 0 ? (
        <div className="explanation-signal-list">
          {signals.map((signal, index) => (
            <div
              className="explanation-signal-item"
              key={`${signal.feature}-${index}`}
            >
              <div className="explanation-signal-information">
                <span>{signal.feature}</span>
                <strong>{formatContribution(signal.contribution)}</strong>
              </div>

              <div className="explanation-contribution-track">
                <div
                  className={`explanation-contribution-fill ${isFraud ? 'fraud-fill' : 'genuine-fill'}`}
                  style={{
                    width: `${Math.min(Math.abs(Number(signal.contribution)) * 100, 100)}%`
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="explanation-empty">
          No signal information is available for this category.
        </p>
      )}
    </div>
  )
}

function CompanyVerification() {
  const [formData, setFormData] = useState(initialFormData)
  const [result, setResult] = useState(null)
  const [aiResult, setAiResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function handleChange(event) {
    const { name, value } = event.target

    setFormData(previous => ({
      ...previous,
      [name]: value
    }))
  }

  function handleCheckboxChange(event) {
    const { name, checked } = event.target

    setFormData(previous => ({
      ...previous,
      [name]: checked ? 1 : 0
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setError('')
    setResult(null)
    setAiResult(null)

    try {
      const [companyReview, aiPrediction] = await Promise.all([
        postToApi('/verify-company', formData),
        postToApi('/explain', formData)
      ])

      setResult(companyReview)
      setAiResult(aiPrediction)
    } catch (err) {
      console.error('OfferShield Analysis Error:', err)

      setError(
        err.message ||
        'Unable to analyse this job posting. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  function resetForm() {
    setFormData(initialFormData)
    setResult(null)
    setAiResult(null)
    setError('')
  }

  function getStatusIcon(status) {
    if (['provided', 'passed', 'verified'].includes(status)) {
      return CheckCircle2
    }

    if (['missing', 'incomplete', 'not_found'].includes(status)) {
      return AlertTriangle
    }

    return Info
  }

  function getStatusClass(status) {
    if (['provided', 'passed', 'verified'].includes(status)) {
      return 'verification-status-success'
    }

    if (['missing', 'incomplete', 'not_found'].includes(status)) {
      return 'verification-status-warning'
    }

    return 'verification-status-neutral'
  }

  const isFraudulent = aiResult?.prediction === 1

  const predictionLabel = aiResult
    ? (
        aiResult.risk_classification ||
        (isFraudulent ? 'Likely Fraudulent' : 'Likely Genuine')
      )
    : ''

  const math = aiResult?.mathematical_verification

  // SMART SAFETY RECOMMENDATIONS

  const safetyActions = []

  if (aiResult) {
    if (isFraudulent) {
      safetyActions.push({
        id: 'ai-risk',
        level: 'high',
        title: 'Exercise extreme caution before proceeding',
        description:
          'The machine-learning model detected patterns associated with fraudulent job postings. Do not proceed until you have independently investigated the employer and opportunity.',
        icon: ShieldAlert
      })

      safetyActions.push({
        id: 'payment',
        level: 'high',
        title: 'Never pay recruitment or interview fees',
        description:
          'Do not pay registration fees, interview fees, security deposits or training charges to obtain this job or internship.',
        icon: Wallet
      })

      safetyActions.push({
        id: 'documents',
        level: 'high',
        title: 'Protect your sensitive personal information',
        description:
          'Do not share banking credentials, OTPs, passwords, or sensitive identity documents with an unverified recruiter.',
        icon: LockKeyhole
      })
    } else {
      safetyActions.push({
        id: 'ai-caution',
        level: 'normal',
        title: 'Continue with independent verification',
        description:
          'The model classified this posting as likely genuine. This is not proof of legitimacy. Verify the employer, recruiter and application process independently before proceeding.',
        icon: ShieldCheck
      })

      safetyActions.push({
        id: 'official-link',
        level: 'normal',
        title: 'Check the official application link',
        description:
          'Find the employer’s careers page independently and confirm that the job title and application link match the opportunity you received.',
        icon: Globe
      })
    }

    const checks = result?.checks || []

    const companyProfile = checks.find(
      check => check.name === 'Company profile'
    )

    const jobDescription = checks.find(
      check => check.name === 'Job description'
    )

    const contactInformation = checks.find(
      check => check.name === 'Contact information'
    )

    const applicationInstructions = checks.find(
      check => check.name === 'Application instructions'
    )

    const benefitsInformation = checks.find(
      check => check.name === 'Benefits information'
    )

    if (
      companyProfile &&
      ['missing', 'incomplete', 'not_found'].includes(companyProfile.status)
    ) {
      safetyActions.push({
        id: 'company-profile',
        level: 'warning',
        title: 'Research the company independently',
        description:
          'The company profile is missing or incomplete. Look up the employer’s official website, business presence and independently published company information.',
        icon: Building2
      })
    }

    if (
      jobDescription &&
      ['missing', 'incomplete', 'not_found'].includes(jobDescription.status)
    ) {
      safetyActions.push({
        id: 'job-description',
        level: 'warning',
        title: 'Request a complete job description',
        description:
          'Ask the recruiter for clear responsibilities, required skills, working arrangements and selection stages before committing to the opportunity.',
        icon: FileText
      })
    }

    if (
      contactInformation &&
      ['missing', 'incomplete', 'not_found'].includes(contactInformation.status)
    ) {
      safetyActions.push({
        id: 'contact',
        level: 'warning',
        title: 'Find independently verifiable contact details',
        description:
          'The posting does not contain sufficient contact information. Find contact details through the employer’s independently located official website.',
        icon: Mail
      })
    }

    if (
      applicationInstructions &&
      ['missing', 'incomplete', 'not_found'].includes(applicationInstructions.status)
    ) {
      safetyActions.push({
        id: 'application',
        level: 'warning',
        title: 'Confirm the application process',
        description:
          'Application instructions are missing or incomplete. Ask how to apply and verify the process through the employer’s official careers channel.',
        icon: ClipboardCheck
      })
    }

    if (
      benefitsInformation &&
      ['missing', 'incomplete', 'not_found', 'not_provided'].includes(benefitsInformation.status)
    ) {
      safetyActions.push({
        id: 'benefits',
        level: 'normal',
        title: 'Clarify compensation and internship conditions',
        description:
          'The posting does not provide complete benefits information. Ask about stipend or salary, working hours, duration, mentorship and other employment conditions. Missing benefits alone do not establish fraud.',
        icon: Gift
      })
    }

    safetyActions.push({
      id: 'recruiter',
      level: 'normal',
      title: 'Verify the recruiter’s identity',
      description:
        'Check whether the recruiter is associated with the employer. Contact the company through independently obtained official contact details if you are uncertain.',
      icon: CheckCircle2
    })
  }

  return (
    <div className="company-verification-page">

      {/* PAGE HEADER */}

      <div className="company-verification-header">
        <div>
          <span className="panel-overline">
            OFFER SHIELD INTELLIGENCE
          </span>

          <h1>Company Verification</h1>

          <p>
            Analyse job postings using AI fraud detection and
            company information checks.
          </p>
        </div>

        <div className="company-verification-header-icon">
          <ShieldCheck size={30} />
        </div>
      </div>

      {/* INFORMATION NOTICE */}

      <div className="company-verification-notice">
        <Info size={19} />

        <p>
          OfferShield provides an ML-based risk prediction and a
          separate review of information completeness. Neither
          assessment independently confirms employer legitimacy.
        </p>
      </div>

      {/* INPUT FORM */}

      <form
        className="company-verification-form"
        onSubmit={handleSubmit}
      >
        <div className="verification-section-heading">
          <div>
            <h2>Job and Company Details</h2>
            <p>
              Enter the job posting information you want to analyse.
            </p>
          </div>

          <button
            type="button"
            className="verification-reset-button"
            onClick={resetForm}
          >
            <RotateCcw size={15} />
            Reset
          </button>
        </div>

        {/* JOB INFORMATION */}

        <div className="verification-form-section">
          <h3>
            <BriefcaseBusiness size={18} />
            Job Information
          </h3>

          <div className="verification-form-grid">
            <div className="verification-field">
              <label htmlFor="company-title">Job Title *</label>
              <input
                id="company-title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="Software Engineer Intern"
                required
              />
            </div>

            <div className="verification-field">
              <label htmlFor="company-location">Job Location *</label>
              <input
                id="company-location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="Bangalore, India"
                required
              />
            </div>

            <div className="verification-field">
              <label htmlFor="company-department">Department</label>
              <input
                id="company-department"
                name="department"
                value={formData.department}
                onChange={handleChange}
                placeholder="Engineering"
              />
            </div>

            <div className="verification-field">
              <label htmlFor="company-salary">Salary Range</label>
              <input
                id="company-salary"
                name="salary_range"
                value={formData.salary_range}
                onChange={handleChange}
                placeholder="30000-50000"
              />
            </div>
          </div>
        </div>

        {/* COMPANY INFORMATION */}

        <div className="verification-form-section">
          <h3>
            <Building2 size={18} />
            Company Information
          </h3>

          <div className="verification-field">
            <label htmlFor="company-profile">Company Profile</label>
            <textarea
              id="company-profile"
              name="company_profile"
              value={formData.company_profile}
              onChange={handleChange}
              placeholder="Describe the company, its services, industry, website and background..."
              rows={4}
            />
          </div>

          <div className="verification-field">
            <label htmlFor="company-industry">Industry</label>
            <input
              id="company-industry"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              placeholder="Information Technology"
            />
          </div>
        </div>

        {/* JOB DESCRIPTION */}

        <div className="verification-form-section">
          <h3>
            <FileText size={18} />
            Job Description
          </h3>

          <div className="verification-field">
            <label htmlFor="company-description">Job Description *</label>
            <textarea
              id="company-description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter the complete job description, responsibilities and application instructions..."
              rows={6}
              required
            />
          </div>

          <div className="verification-field">
            <label htmlFor="company-requirements">Requirements</label>
            <textarea
              id="company-requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              placeholder="Enter the required skills and qualifications..."
              rows={3}
            />
          </div>

          <div className="verification-field">
            <label htmlFor="company-benefits">Benefits</label>
            <textarea
              id="company-benefits"
              name="benefits"
              value={formData.benefits}
              onChange={handleChange}
              placeholder="Enter salary benefits, internship certificate, mentorship, etc."
              rows={3}
            />
          </div>
        </div>

        {/* EMPLOYMENT DETAILS */}

        <div className="verification-form-section">
          <h3>
            <ClipboardCheck size={18} />
            Employment Details
          </h3>

          <div className="verification-form-grid">
            <div className="verification-field">
              <label htmlFor="company-employment">Employment Type</label>
              <select
                id="company-employment"
                name="employment_type"
                value={formData.employment_type}
                onChange={handleChange}
              >
                <option>Internship</option>
                <option>Full-time</option>
                <option>Part-time</option>
                <option>Contract</option>
                <option>Temporary</option>
                <option>Other</option>
              </select>
            </div>

            <div className="verification-field">
              <label htmlFor="company-experience">Required Experience</label>
              <select
                id="company-experience"
                name="required_experience"
                value={formData.required_experience}
                onChange={handleChange}
              >
                <option>Not Specified</option>
                <option>Internship</option>
                <option>Entry Level</option>
                <option>Mid-Senior Level</option>
                <option>Director</option>
                <option>Executive</option>
              </select>
            </div>

            <div className="verification-field">
              <label htmlFor="company-education">Required Education</label>
              <select
                id="company-education"
                name="required_education"
                value={formData.required_education}
                onChange={handleChange}
              >
                <option>Not Specified</option>
                <option>High School</option>
                <option>Associate Degree</option>
                <option>Bachelor's Degree</option>
                <option>Master's Degree</option>
                <option>Doctorate</option>
              </select>
            </div>

            <div className="verification-field">
              <label htmlFor="company-function">Job Function</label>
              <input
                id="company-function"
                name="function"
                value={formData.function}
                onChange={handleChange}
                placeholder="Engineering"
              />
            </div>
          </div>

          <div className="verification-checkbox-group">
            <label>
              <input
                type="checkbox"
                name="telecommuting"
                checked={Boolean(formData.telecommuting)}
                onChange={handleCheckboxChange}
              />
              Remote work available
            </label>

            <label>
              <input
                type="checkbox"
                name="has_company_logo"
                checked={Boolean(formData.has_company_logo)}
                onChange={handleCheckboxChange}
              />
              Company logo included
            </label>

            <label>
              <input
                type="checkbox"
                name="has_questions"
                checked={Boolean(formData.has_questions)}
                onChange={handleCheckboxChange}
              />
              Screening questions included
            </label>
          </div>
        </div>

        {/* ERROR MESSAGE */}

        {error && (
          <div className="verification-error">
            <XCircle size={19} />
            <span>{error}</span>
          </div>
        )}

        {/* SUBMIT BUTTON */}

        <div className="verification-submit-area">
          <button
            type="submit"
            className="verification-submit-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <LoaderCircle className="verification-spinner" size={19} />
                Analysing Job Posting...
              </>
            ) : (
              <>
                <Search size={19} />
                Analyse Job Posting
              </>
            )}
          </button>
        </div>
      </form>

      {/* AI FRAUD DETECTION RESULTS */}

      {aiResult && (
        <section className="company-ai-results">
          <div className="verification-results-header">
            <div>
              <span className="panel-overline">
                MACHINE LEARNING REPORT
              </span>
              <h2>AI Fraud Detection</h2>
              <p>
                Prediction generated by the trained LinearSVC model.
              </p>
            </div>

            <div className="verification-report-icon">
              <BrainCircuit size={27} />
            </div>
          </div>

          <div className={`company-ai-prediction ${
            isFraudulent ? 'ai-fraudulent' : 'ai-genuine'
          }`}>
            {isFraudulent ? (
              <ShieldAlert size={30} />
            ) : (
              <ShieldCheck size={30} />
            )}

            <div>
              <span>AI Prediction</span>
              <strong>{predictionLabel}</strong>
              <p>
                {isFraudulent
                  ? 'The model identified patterns associated with fraudulent job postings.'
                  : 'The model identified patterns associated with genuine job postings.'}
              </p>
            </div>
          </div>

          <div className="verification-summary-grid">
            <div className="verification-summary-card">
              <span>Decision Score</span>
              <strong>
                {Number(aiResult.decision_score).toFixed(4)}
              </strong>
            </div>

            <div className="verification-summary-card">
              <span>Model Threshold</span>
              <strong>
                {Number(aiResult.threshold).toFixed(4)}
              </strong>
            </div>

            <div className="verification-summary-card">
              <span>Predicted Class</span>
              <strong>
                {isFraudulent ? 'Fraudulent (1)' : 'Genuine (0)'}
              </strong>
            </div>
          </div>

          {/* EXPLAINABLE AI FEATURE CONTRIBUTIONS */}

          <div className="explanation-panel">
            <div className="explanation-panel-header">
              <div className="explanation-panel-icon">
                <BrainCircuit size={23} />
              </div>

              <div>
                <span className="panel-overline">
                  MODEL INTERPRETABILITY
                </span>
                <h2>Why did the AI make this prediction?</h2>
                <p>
                  These feature contributions explain which inputs
                  influenced the LinearSVC decision score.
                </p>
              </div>
            </div>

            <ContributionList
              title="Fraud-increasing signals"
              signals={aiResult.fraud_increasing_signals}
              type="fraud"
            />

            <ContributionList
              title="Genuine-increasing signals"
              signals={aiResult.genuine_increasing_signals}
              type="genuine"
            />
          </div>

          {/* MATHEMATICAL VERIFICATION */}

          {math && (
            <div className="explanation-math-panel">
              <div className="explanation-math-heading">
                <Calculator size={21} />
                <div>
                  <h3>Mathematical Verification</h3>
                  <p>
                    Checking whether the feature contributions
                    reconstruct the model decision score.
                  </p>
                </div>
              </div>

              <div className="explanation-math-grid">
                <div className="explanation-math-item">
                  <span>Actual Decision Score</span>
                  <strong>{Number(math.actual_score).toFixed(10)}</strong>
                </div>

                <div className="explanation-math-item">
                  <span>Contribution Sum</span>
                  <strong>{Number(math.contribution_sum).toFixed(10)}</strong>
                </div>

                <div className="explanation-math-item">
                  <span>Model Intercept</span>
                  <strong>{Number(math.intercept).toFixed(10)}</strong>
                </div>

                <div className="explanation-math-item">
                  <span>Reconstructed Score</span>
                  <strong>{Number(math.reconstructed_score).toFixed(10)}</strong>
                </div>
              </div>

              <div className={`explanation-math-verdict ${
                math.verified ? 'math-verified' : 'math-not-verified'
              }`}>
                {math.verified ? (
                  <CheckCircle2 size={19} />
                ) : (
                  <AlertTriangle size={19} />
                )}

                <div>
                  <strong>
                    {math.verified
                      ? 'Mathematical Verification Passed'
                      : 'Mathematical Verification Needs Review'}
                  </strong>

                  <p>
                    Difference: {Number(math.difference).toExponential(4)}
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="company-ai-disclaimer">
            <Info size={18} />
            <p>
              This is a machine-learning prediction, not a guarantee.
              Feature contributions describe how inputs affect the
              model score; they do not establish causation.
              The decision score is not a probability or percentage.
              Always independently research an employer before sharing
              personal information or accepting an offer.
            </p>
          </div>
        </section>
      )}

      {/* COMPANY INFORMATION RESULTS */}

      {result && (
        <section className="company-verification-results">
          <div className="verification-results-header">
            <div>
              <span className="panel-overline">
                VERIFICATION REPORT
              </span>
              <h2>Company Information Review</h2>
              <p>
                Review the completeness of the supplied information.
              </p>
            </div>

            <div className="verification-report-icon">
              <ShieldCheck size={27} />
            </div>
          </div>

          {/* SUMMARY CARDS */}

          <div className="verification-summary-grid">
            <div className="verification-summary-card">
              <span>Total Checks</span>
              <strong>{result.total_checks}</strong>
            </div>

            <div className="verification-summary-card success">
              <span>Information Provided</span>
              <strong>{result.passed_checks}</strong>
            </div>

            <div className="verification-summary-card warning">
              <span>Warnings</span>
              <strong>{result.warning_checks}</strong>
            </div>
          </div>

          {/* OVERALL STATUS */}

          <div className={`verification-overall-status ${
            result.warning_checks > 0 ? 'has-warnings' : 'all-clear'
          }`}>
            {result.warning_checks > 0 ? (
              <ShieldAlert size={22} />
            ) : (
              <ShieldCheck size={22} />
            )}

            <div>
              <strong>{result.status}</strong>
              <p>
                {result.warning_checks > 0
                  ? 'Some information requires further attention.'
                  : 'All information checks passed. Independent company verification has not been performed.'}
              </p>
            </div>
          </div>

          {/* INDIVIDUAL CHECKS */}

          <div className="verification-checks-section">
            <h3>Verification Checks</h3>

            <div className="verification-check-list">
              {result.checks.map((check, index) => {
                const Icon = checkIcons[check.name] || Info
                const StatusIcon = getStatusIcon(check.status)

                return (
                  <div
                    className="verification-check-item"
                    key={`${check.name}-${index}`}
                  >
                    <div className="verification-check-icon">
                      <Icon size={20} />
                    </div>

                    <div className="verification-check-content">
                      <strong>{check.name}</strong>
                      <p>{check.message}</p>
                    </div>

                    <div className={`verification-check-status ${getStatusClass(check.status)}`}>
                      <StatusIcon size={15} />
                      <span>{check.status.replaceAll('_', ' ')}</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* DISCLAIMER */}

          <div className="verification-disclaimer">
            <AlertTriangle size={19} />
            <div>
              <strong>Important Notice</strong>
              <p>{result.disclaimer}</p>
            </div>
          </div>
        </section>
      )}

      {/* SMART SAFETY RECOMMENDATIONS */}

      {aiResult && (
        <section className="safety-recommendations-section">
          <div className="verification-results-header">
            <div>
              <span className="panel-overline">
                PERSONALIZED JOB SAFETY GUIDE
              </span>
              <h2>Recommended Safety Actions</h2>
              <p>
                Practical steps based on the AI prediction and
                the information available in this job posting.
              </p>
            </div>

            <div className="verification-report-icon">
              <Lightbulb size={27} />
            </div>
          </div>

          <div className="safety-recommendations-notice">
            <Info size={18} />
            <p>
              These are precautionary recommendations, not independent
              verification of the employer or recruiter.
            </p>
          </div>

          <div className="safety-recommendations-list">
            {safetyActions.map((action, index) => {
              const Icon = action.icon

              return (
                <div
                  className={`safety-recommendation-card safety-${action.level}`}
                  key={action.id}
                >
                  <div className="safety-recommendation-icon">
                    <Icon size={21} />
                  </div>

                  <div className="safety-recommendation-content">
                    <div className="safety-recommendation-topline">
                      <span className="safety-recommendation-number">
                        ACTION {String(index + 1).padStart(2, '0')}
                      </span>

                      <span className={`safety-priority safety-priority-${action.level}`}>
                        {action.level === 'high'
                          ? 'High Priority'
                          : action.level === 'warning'
                            ? 'Needs Attention'
                            : 'Recommended'}
                      </span>
                    </div>

                    <h3>{action.title}</h3>
                    <p>{action.description}</p>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="safety-final-checklist">
            <div className="safety-final-checklist-heading">
              <Check size={20} />
              <h3>Before You Apply: Final Safety Checklist</h3>
            </div>

            <ul>
              <li>Confirm the job exists on the employer's official careers website.</li>
              <li>Verify the recruiter using independently obtained company contact details.</li>
              <li>Never pay money to secure an interview, job or internship.</li>
              <li>Never share passwords, OTPs or banking credentials.</li>
              <li>Read the offer letter and employment conditions carefully.</li>
            </ul>
          </div>
        </section>
      )}

    </div>
  )
}

export default CompanyVerification
