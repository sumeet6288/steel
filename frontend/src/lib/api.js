import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

export const projectsAPI = {
  create: (data) => api.post('/projects/', data),
  getAll: () => api.get('/projects/'),
  getById: (id) => api.get(`/projects/${id}`),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
};

export const connectionsAPI = {
  create: (data) => api.post('/connections/', data),
  getAll: (projectId) => api.get('/connections/', { params: { project_id: projectId } }),
  getById: (id) => api.get(`/connections/${id}`),
  update: (id, data) => api.put(`/connections/${id}`, data),
  validate: (id) => api.post(`/connections/${id}/validate`),
  exportTekla: (id) => api.post(`/connections/${id}/export/tekla`),
  delete: (id) => api.delete(`/connections/${id}`),
};

export const redlinesAPI = {
  upload: (connectionId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/redlines/upload?connection_id=${connectionId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  interpret: (redlineId) => api.post(`/redlines/${redlineId}/interpret`),
  approve: (redlineId, params) => api.post(`/redlines/${redlineId}/approve`, params),
  getByConnection: (connectionId) => api.get(`/redlines/${connectionId}/list`),
};

export const auditAPI = {
  getConnectionAudit: (connectionId) => api.get(`/audit/connection/${connectionId}`),
  getMyActivity: (limit = 50) => api.get(`/audit/my-activity`, { params: { limit } }),
};

export const aiAPI = {
  suggestConnection: (requirements) => api.post('/ai/suggest-connection/', requirements),
  generateRFI: (connectionData, issue) => api.post('/ai/generate-rfi/', { connection_data: connectionData, issue }),
};

export default api;