
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? 'https://offershield-ai.onrender.com'
    : 'http://127.0.0.1:8000')

// Shared API request handler
async function makeRequest(endpoint, jobData) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(jobData)
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const errorMessage = Array.isArray(data.detail)
      ? data.detail.map(error => error.msg).join(', ')
      : data.detail || 'Unable to analyse this job posting.'

    throw new Error(errorMessage)
  }

  return data
}

// Get feature signals and mathematical explanation
export async function analyzeJob(jobData) {
  return makeRequest('/explain', jobData)
}

// Get three-level risk classification
export async function predictJob(jobData) {
  return makeRequest('/predict', jobData)
}
