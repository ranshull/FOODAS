import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh');
      if (refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/auth/refresh/`, { refresh });
          localStorage.setItem('access', data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch (_) {
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(err);
  }
);

export const auth = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  register: (body) => api.post('/auth/register/', body),
  me: () => api.get('/auth/me/'),
};

export const owner = {
  apply: (body) => api.post('/owner/apply/', body),
  applicationStatus: () => api.get('/owner/application-status/'),
  upload: (file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/owner/upload/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const admin = {
  listApplications: () => api.get('/admin/owner-applications/'),
  getApplication: (id) => api.get(`/admin/owner-applications/${id}/`),
  approve: (id, review_notes = '') => api.patch(`/admin/owner-applications/${id}/approve/`, { review_notes }),
  reject: (id, review_notes = '') => api.patch(`/admin/owner-applications/${id}/reject/`, { review_notes }),
};

export const restaurants = {
  list: (params = {}) => api.get('/restaurants/', { params }),
  get: (id) => api.get(`/restaurants/${id}/`),
  me: () => api.get('/restaurants/me/'),
  updateMe: (data) => api.patch('/restaurants/me/', data),
  addPhoto: (data) => api.post('/restaurants/me/photos/', data),
  deletePhoto: (id) => api.delete(`/restaurants/me/photos/${id}/`),
};

export const superadmin = {
  listUsers: (params = {}) => api.get('/superadmin/users/', { params }),
  getUser: (id) => api.get(`/superadmin/users/${id}/`),
  updateUser: (id, data) => api.patch(`/superadmin/users/${id}/`, data),
  createUser: (data) => api.post('/superadmin/users/create/', data),
};
