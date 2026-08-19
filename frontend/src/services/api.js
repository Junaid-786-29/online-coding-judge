
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  getAuthHeader() {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 204) {
        return null;
      }

      let data;
      try {
        data = await response.json();
      } catch (err) {
        data = null;
      }

      if (!response.ok) {

        if (response.status === 401) {
          localStorage.removeItem('token');
          window.dispatchEvent(new CustomEvent('auth:unauthorized'));
        }

        const errorMessage = data?.detail || `Request failed with status ${response.status}`;
        const error = new Error(errorMessage);
        error.status = response.status;
        error.data = data;
        throw error;
      }

      return data;
    } catch (err) {
      if (err.status) {
        throw err;
      }
      throw new Error(`Network error: Unable to connect to judge backend at ${this.baseUrl}`);
    }
  }

  async register(username, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password }),
    });
  }

  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async getHealth() {
    return this.request('/health');
  }

  async getProblems() {
    return this.request('/problems/');
  }

  async getProblemById(problemId) {
    return this.request(`/problems/${problemId}`);
  }

  async getProblemStats(problemId) {
    return this.request(`/problems/${problemId}/stats`);
  }

  async getProblemTestCases(problemId) {
    return this.request(`/problems/${problemId}/test-cases/`);
  }

  async createSubmission(problemId, sourceCode, language = 'python') {
    return this.request('/submissions', {
      method: 'POST',
      body: JSON.stringify({
        problem_id: Number(problemId),
        source_code: sourceCode,
        language: language,
      }),
    });
  }

  async getSubmissionById(submissionId) {
    return this.request(`/submissions/${submissionId}`);
  }

  async getMySubmissions({ page = 1, pageSize = 10, status = null, problemId = null } = {}) {
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('page_size', pageSize);
    if (status) params.append('status', status);
    if (problemId) params.append('problem_id', problemId);

    return this.request(`/submissions/me?${params.toString()}`);
  }

  async getProblemSubmissions(problemId, { page = 1, pageSize = 10, status = null } = {}) {
    const params = new URLSearchParams();
    params.append('page', page);
    params.append('page_size', pageSize);
    if (status) params.append('status', status);

    return this.request(`/problems/${problemId}/submissions?${params.toString()}`);
  }

  async getMyStats() {
    return this.request('/submissions/stats');
  }
}

export const api = new ApiService(API_BASE_URL);
