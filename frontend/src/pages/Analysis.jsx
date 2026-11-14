
import { useState } from 'react'

import { useNavigate } from 'react-router-dom'

import {
  BriefcaseBusiness,
  Building2,
  FileText,
  GraduationCap,
  ArrowRight,
  ShieldCheck
} from 'lucide-react'

import {
  analyzeJob,
  predictJob
} from '../services/api'

function Analysis() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
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
    employment_type: 'Full-time',
    required_experience: 'Not Specified',
    required_education: 'Not Specified',
    industry: '',
    function: ''
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Handle text inputs and dropdowns
  function handleChange(event) {
    const { name, value } = event.target

    setFormData(previous => ({
      ...previous,
      [name]: value
    }))
  }

  // Submit job information and save complete analysis history
  async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setError('')

    try {
      // Preserve the original submitted job information
      const submittedJobData = { ...formData }

      // Call both backend endpoints simultaneously
      const [explanationData, predictionData] = await Promise.all([
        analyzeJob(submittedJobData),
        predictJob(submittedJobData)
      ])

      console.log('Explanation Result:', explanationData)
      console.log('Prediction Result:', predictionData)

      // Combine both API responses
      // Prediction fields take priority for risk classification.
      const completeResult = {
        ...explanationData,
        ...predictionData,

        // Preserve explanation-specific information
        job_title:
          explanationData.job_title || submittedJobData.title,

        fraud_increasing_signals:
          explanationData.fraud_increasing_signals || [],

        genuine_increasing_signals:
          explanationData.genuine_increasing_signals || [],

        mathematical_verification:
          explanationData.mathematical_verification || null
      }

      console.log('Complete AI Analysis Result:', completeResult)

      // Create a complete history record
      const historyItem = {
        id: crypto.randomUUID(),
        createdAt: new Date().toISOString(),

        // Original job posting information
        jobData: submittedJobData,

        // Combined prediction and explanation response
        result: completeResult
      }

      // Retrieve previously saved analyses
      const savedHistory = JSON.parse(
        localStorage.getItem('offershield_analysis_history') || '[]'
      )

      const existingHistory = Array.isArray(savedHistory)
        ? savedHistory
        : []

      // Save the latest analysis at the beginning
      localStorage.setItem(
        'offershield_analysis_history',
        JSON.stringify([historyItem, ...existingHistory])
      )

      // Navigate to Results page with complete analysis
      navigate('/results', {
        state: {
          result: completeResult
        }
      })

    } catch (err) {
      console.error('Analysis Error:', err)

      setError(
        err.message ||
        'Unable to analyse this job posting. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="analysis-page">

      <div className="analysis-page-heading">
        <div>
          <p className="eyebrow">AI-POWERED JOB SCREENING</p>

          <h1>Analyse a Job Posting</h1>

          <p>
            Enter job information to evaluate potential fraud
            signals using our machine learning model.
          </p>
        </div>

        <div className="analysis-page-icon">
          <ShieldCheck size={27} />
        </div>
      </div>

      <form className="job-form" onSubmit={handleSubmit}>

        {/* Job Information */}
        <section className="form-section">

          <div className="form-section-heading">
            <BriefcaseBusiness size={20} />

            <div>
              <h2>Job Information</h2>
              <p>Basic details about the opportunity.</p>
            </div>
          </div>

          <div className="form-grid">

            <div className="form-field">
              <label htmlFor="title">Job Title *</label>

              <input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g. Software Engineer Intern"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="location">Job Location *</label>

              <input
                id="location"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="e.g. Bangalore, India"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="department">Department</label>

              <input
                id="department"
                name="department"
                value={formData.department}
                onChange={handleChange}
                placeholder="e.g. Engineering"
              />
            </div>

            <div className="form-field">
              <label htmlFor="salary_range">Salary Range</label>

              <input
                id="salary_range"
                name="salary_range"
                value={formData.salary_range}
                onChange={handleChange}
                placeholder="e.g. 5 LPA - 8 LPA"
              />
            </div>

          </div>
        </section>

        {/* Company Information */}
        <section className="form-section">

          <div className="form-section-heading">
            <Building2 size={20} />

            <div>
              <h2>Company Information</h2>
              <p>Details about the hiring organisation.</p>
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="company_profile">Company Profile</label>

            <textarea
              id="company_profile"
              name="company_profile"
              value={formData.company_profile}
              onChange={handleChange}
              placeholder="Enter the company description and background..."
              rows={4}
            />
          </div>

        </section>

        {/* Job Description */}
        <section className="form-section">

          <div className="form-section-heading">
            <FileText size={20} />

            <div>
              <h2>Job Description</h2>
              <p>Responsibilities, expectations and benefits.</p>
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="description">Job Description *</label>

            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the role and responsibilities..."
              rows={5}
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="requirements">Requirements</label>

            <textarea
              id="requirements"
              name="requirements"
              value={formData.requirements}
              onChange={handleChange}
              placeholder="Enter required skills, qualifications and experience..."
              rows={4}
            />
          </div>

          <div className="form-field">
            <label htmlFor="benefits">Benefits</label>

            <textarea
              id="benefits"
              name="benefits"
              value={formData.benefits}
              onChange={handleChange}
              placeholder="Enter salary benefits, insurance, paid leave, etc."
              rows={3}
            />
          </div>

        </section>

        {/* Employment Details */}
        <section className="form-section">

          <div className="form-section-heading">
            <GraduationCap size={20} />

            <div>
              <h2>Employment Details</h2>
              <p>Additional job and eligibility information.</p>
            </div>
          </div>

          <div className="form-grid">

            <div className="form-field">
              <label htmlFor="employment_type">Employment Type</label>

              <select
                id="employment_type"
                name="employment_type"
                value={formData.employment_type}
                onChange={handleChange}
              >
                <option value="Not Specified">Not Specified</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Temporary">Temporary</option>
                <option value="Internship">Internship</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="required_experience">
                Required Experience
              </label>

              <select
                id="required_experience"
                name="required_experience"
                value={formData.required_experience}
                onChange={handleChange}
              >
                <option value="Not Specified">Not Specified</option>
                <option value="Internship">Internship</option>
                <option value="Entry level">Entry level</option>
                <option value="Associate">Associate</option>
                <option value="Mid-Senior level">Mid-Senior level</option>
                <option value="Director">Director</option>
                <option value="Executive">Executive</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="required_education">
                Required Education
              </label>

              <select
                id="required_education"
                name="required_education"
                value={formData.required_education}
                onChange={handleChange}
              >
                <option value="Not Specified">Not Specified</option>
                <option value="High School or equivalent">High School</option>
                <option value="Bachelor's Degree">Bachelor's Degree</option>
                <option value="Master's Degree">Master's Degree</option>
                <option value="Unspecified">Unspecified</option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="industry">Industry</label>

              <input
                id="industry"
                name="industry"
                value={formData.industry}
                onChange={handleChange}
                placeholder="e.g. Information Technology"
              />
            </div>

            <div className="form-field">
              <label htmlFor="function">Job Function</label>

              <input
                id="function"
                name="function"
                value={formData.function}
                onChange={handleChange}
                placeholder="e.g. Engineering"
              />
            </div>

          </div>

          {/* Additional job indicators */}
          <div className="form-options">

            <label>
              <input
                type="checkbox"
                checked={formData.telecommuting === 1}
                onChange={event => setFormData(previous => ({
                  ...previous,
                  telecommuting: event.target.checked ? 1 : 0
                }))}
              />

              Remote work available
            </label>

            <label>
              <input
                type="checkbox"
                checked={formData.has_company_logo === 1}
                onChange={event => setFormData(previous => ({
                  ...previous,
                  has_company_logo: event.target.checked ? 1 : 0
                }))}
              />

              Company logo present
            </label>

            <label>
              <input
                type="checkbox"
                checked={formData.has_questions === 1}
                onChange={event => setFormData(previous => ({
                  ...previous,
                  has_questions: event.target.checked ? 1 : 0
                }))}
              />

              Screening questions included
            </label>

          </div>

        </section>

        {/* Error message */}
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}

        {/* Submit button */}
        <div className="form-submit-area">

          <p>
            <ShieldCheck size={16} />
            Your job information will be evaluated by the ML model.
          </p>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Analysing...' : 'Analyse Job Posting'}

            <ArrowRight size={18} />
          </button>

        </div>

      </form>

    </div>
  )
}

export default Analysis
