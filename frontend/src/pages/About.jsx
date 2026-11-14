
import {
  ShieldCheck,
  Search,
  BrainCircuit,
  FileCheck2,
  Database,
  Server,
  Monitor,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Layers3,
  Code2
} from 'lucide-react'

const workflow = [
  {
    number: '01',
    icon: Search,
    title: 'Job posting input',
    description: 'Users submit job details such as title, company profile, description, requirements and employment information.'
  },
  {
    number: '02',
    icon: Database,
    title: 'Data preprocessing',
    description: 'Text and structured fields are transformed using the saved preprocessing pipeline.'
  },
  {
    number: '03',
    icon: BrainCircuit,
    title: 'Machine learning analysis',
    description: 'A trained Linear Support Vector Classifier evaluates the posting and produces a decision score.'
  },
  {
    number: '04',
    icon: FileCheck2,
    title: 'Risk assessment',
    description: 'The decision score is translated into a risk category, with supporting explanations and recommended next steps.'
  }
]

const capabilities = [
  {
    icon: ShieldCheck,
    title: 'Fraud risk detection',
    description: 'Identifies suspicious patterns in job and internship postings using a trained machine learning model.'
  },
  {
    icon: BrainCircuit,
    title: 'Explainable AI',
    description: 'Presents feature-level signals to help users understand which information influenced the model output.'
  },
  {
    icon: FileCheck2,
    title: 'Company profile review',
    description: 'Checks the completeness of available company and job information. It does not independently certify an employer.'
  },
  {
    icon: Layers3,
    title: 'Pattern intelligence',
    description: 'Helps users explore recurring indicators and trends across their saved analysis reports.'
  },
  {
    icon: GitCompareIcon,
    title: 'Report comparison',
    description: 'Allows users to compare previously analysed opportunities and their risk assessments.'
  },
  {
    icon: Clock3,
    title: 'Analysis history',
    description: 'Keeps previous analysis reports available for review and comparison in the browser.'
  }
]

const technologies = [
  { name: 'Python', role: 'Backend and ML development' },
  { name: 'Scikit-learn', role: 'Machine learning model' },
  { name: 'Pandas & NumPy', role: 'Data processing' },
  { name: 'FastAPI', role: 'Backend API framework' },
  { name: 'React', role: 'Frontend interface' },
  { name: 'Vite', role: 'Frontend development tooling' },
  { name: 'JavaScript', role: 'Frontend application logic' },
  { name: 'Render', role: 'Backend deployment' }
]

function GitCompareIcon(props) {
  return <Code2 {...props} />
}

function About() {
  return (
    <div className="about-page">

      <section className="about-hero">
        <div className="about-hero-content">
          <span className="about-eyebrow">
            <ShieldCheck size={15} />
            THE OFFER SHIELD PLATFORM
          </span>

          <h1>
            Make informed career decisions with
            <span> intelligent opportunity screening.</span>
          </h1>

          <p>
            OfferShield AI is an explainable machine learning platform
            designed to help students, fresh graduates and job seekers
            assess potential risks in online job and internship postings.
          </p>

          <div className="about-hero-tags">
            <span><BrainCircuit size={14} /> Machine Learning</span>
            <span><ShieldCheck size={14} /> Risk Intelligence</span>
            <span><FileCheck2 size={14} /> Explainable AI</span>
          </div>
        </div>

        <div className="about-hero-visual">
          <div className="about-shield-orbit orbit-one" />
          <div className="about-shield-orbit orbit-two" />
          <div className="about-shield-center">
            <ShieldCheck size={65} strokeWidth={1.5} />
          </div>
          <div className="about-floating-card">
            <CheckCircle2 size={17} />
            <div>
              <strong>Risk intelligence</strong>
              <span>Explainable assessment</span>
            </div>
          </div>
        </div>
      </section>

      <section className="about-intro-grid">
        <div className="about-section-heading">
          <span className="about-section-label">01 / INTRODUCTION</span>
          <h2>Why OfferShield AI exists</h2>
        </div>

        <div className="about-intro-copy">
          <p>
            Online platforms have made finding jobs and internships easier,
            but fraudulent opportunities can expose applicants to financial
            loss, identity theft and misuse of personal information.
          </p>
          <p>
            OfferShield AI aims to make opportunity screening more
            understandable by combining machine learning predictions,
            explainable signals and company information checks in one place.
          </p>
        </div>
      </section>

      <section className="about-workflow-section">
        <div className="about-section-heading">
          <span className="about-section-label">02 / PROCESS</span>
          <h2>How the platform works</h2>
          <p>
            From a job posting to an interpretable risk assessment.
          </p>
        </div>

        <div className="about-workflow-grid">
          {workflow.map((step) => {
            const Icon = step.icon

            return (
              <article className="about-workflow-card" key={step.number}>
                <div className="about-workflow-top">
                  <span>{step.number}</span>
                  <Icon size={23} />
                </div>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </article>
            )
          })}
        </div>
      </section>

      <section className="about-risk-section">
        <div className="about-section-heading">
          <span className="about-section-label">03 / RISK ENGINE</span>
          <h2>Three levels of risk assessment</h2>
          <p>
            Model decision scores are grouped into three categories to help
            users decide what to investigate next.
          </p>
        </div>

        <div className="about-risk-grid">
          <article className="about-risk-card risk-low">
            <span className="about-risk-indicator" />
            <span className="about-risk-label">LOW RISK</span>
            <h3>Likely Genuine</h3>
            <p>
              The model indicates a lower-risk posting. Independent
              verification is still recommended.
            </p>
            <span className="about-risk-range">Score below -0.4</span>
          </article>

          <article className="about-risk-card risk-medium">
            <span className="about-risk-indicator" />
            <span className="about-risk-label">REVIEW REQUIRED</span>
            <h3>Needs Manual Review</h3>
            <p>
              The posting falls within the review range. Check the employer,
              contact information and job details carefully.
            </p>
            <span className="about-risk-range">Score from -0.4 to below 0.1</span>
          </article>

          <article className="about-risk-card risk-high">
            <span className="about-risk-indicator" />
            <span className="about-risk-label">HIGH RISK</span>
            <h3>Potentially Fraudulent</h3>
            <p>
              The model identifies elevated fraud risk. Investigate the
              opportunity before sharing personal information.
            </p>
            <span className="about-risk-range">Score 0.1 or above</span>
          </article>
        </div>

        <div className="about-info-note">
          <AlertTriangle size={18} />
          <p>
            These categories are model-based risk indicators, not guarantees
            of legitimacy or fraud. Decision scores are not probabilities.
          </p>
        </div>
      </section>

      <section className="about-capabilities-section">
        <div className="about-section-heading">
          <span className="about-section-label">04 / CAPABILITIES</span>
          <h2>One platform. Multiple intelligence tools.</h2>
        </div>

        <div className="about-capabilities-grid">
          {capabilities.map((item) => {
            const Icon = item.icon

            return (
              <article className="about-capability-card" key={item.title}>
                <div className="about-capability-icon">
                  <Icon size={21} />
                </div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            )
          })}
        </div>
      </section>

      <section className="about-architecture-section">
        <div className="about-section-heading">
          <span className="about-section-label">05 / ARCHITECTURE</span>
          <h2>Built with a modular architecture</h2>
          <p>
            A React frontend communicates with a FastAPI backend, which
            connects to the saved machine learning pipeline.
          </p>
        </div>

        <div className="about-architecture">
          <div className="about-architecture-node">
            <Monitor size={25} />
            <strong>Frontend</strong>
            <span>React + Vite</span>
          </div>

          <ArrowRight className="about-architecture-arrow" size={23} />

          <div className="about-architecture-node">
            <Server size={25} />
            <strong>Backend API</strong>
            <span>FastAPI + Pydantic</span>
          </div>

          <ArrowRight className="about-architecture-arrow" size={23} />

          <div className="about-architecture-node">
            <BrainCircuit size={25} />
            <strong>ML engine</strong>
            <span>LinearSVC + Scikit-learn</span>
          </div>
        </div>
      </section>

      <section className="about-tech-section">
        <div className="about-section-heading">
          <span className="about-section-label">06 / TECHNOLOGY</span>
          <h2>Technology stack</h2>
          <p>
            The technologies used to develop and deploy the application.
          </p>
        </div>

        <div className="about-tech-grid">
          {technologies.map((tech) => (
            <article className="about-tech-item" key={tech.name}>
              <Code2 size={19} />
              <div>
                <strong>{tech.name}</strong>
                <span>{tech.role}</span>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="about-limitations">
        <div className="about-limitations-icon">
          <AlertTriangle size={22} />
        </div>
        <div>
          <span className="about-section-label">IMPORTANT INFORMATION</span>
          <h2>Designed to support decisions, not replace them.</h2>
          <p>
            OfferShield AI analyses information supplied in a job posting.
            Its predictions depend on the dataset, training process and
            information available. Company profile completeness checks do
            not establish that a company is registered, trustworthy or
            legitimate. Always verify employers through independent,
            authoritative sources before sharing sensitive information
            or accepting an offer.
          </p>
        </div>
      </section>

      <section className="about-closing">
        <ShieldCheck size={26} />
        <div>
          <strong>OfferShield AI</strong>
          <p>More clarity. Better screening. More informed career decisions.</p>
        </div>
        <span>VERSION 1.0.0</span>
      </section>

    </div>
  )
}

export default About
