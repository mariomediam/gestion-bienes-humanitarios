import api from '@api/axios';

export const authApi = {
  login: async (username, password) => {
    const response = await api.post('/api/auth/login/', {
      username,
      password,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me/');
    return response.data;
  },

  getUserMenus: async () => {
    const response = await api.get('/api/auth/menus/');
    return response.data;
  },

  refreshToken: async (refreshToken) => {
    const response = await api.post('/api/auth/refresh/', {
      refresh: refreshToken,
    });
    return response.data;
  },

  changePassword: async (newPassword) => {
    const response = await api.post('/api/auth/change-password/', {
      new_password: newPassword,
    });
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};
