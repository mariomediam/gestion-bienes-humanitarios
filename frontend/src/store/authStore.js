import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { toast } from 'sonner';
import { authApi } from '@api/authApi';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      menus: [],
      isAuthenticated: false,
      loading: false,

      login: async (username, password) => {
        set({ loading: true });

        try {
          const data = await authApi.login(username, password);

          localStorage.setItem('access_token', data.access);
          localStorage.setItem('refresh_token', data.refresh);

          set({
            accessToken: data.access,
            refreshToken: data.refresh,
            user: data.user,
            menus: data.user.menus || [],
            isAuthenticated: true,
            loading: false,
          });

          return { success: true };
        } catch (error) {
          let errorMessage = 'Error al iniciar sesión';

          if (error.response?.status === 401) {
            errorMessage = error.response.data?.error || 'Usuario o contraseña incorrectos';
          } else if (error.response?.status === 400) {
            errorMessage = error.response.data?.error || 'Por favor verifica tus credenciales';
          } else if (error.response?.status === 503) {
            errorMessage = 'Error de conexión con el servidor de autenticación';
          } else if (!error.response) {
            errorMessage = 'Error de conexión. Verifica tu red';
          }

          toast.error(errorMessage);
          set({ loading: false });
          return { success: false, error: errorMessage };
        }
      },

      logout: () => {
        authApi.logout();
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          menus: [],
          isAuthenticated: false,
        });
      },

      checkAuth: async () => {
        set({ loading: true });
        const token = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (token && refreshToken) {
          try {
            const userData = await authApi.getCurrentUser();
            set({
              user: userData,
              isAuthenticated: true,
              accessToken: token,
              refreshToken: refreshToken,
              loading: false,
            });

            const menusData = await authApi.getUserMenus();
            set({ menus: menusData.menus || [] });
          } catch {
            authApi.logout();
            set({
              user: null,
              accessToken: null,
              refreshToken: null,
              menus: [],
              isAuthenticated: false,
              loading: false,
            });
          }
        } else {
          set({ loading: false });
        }
      },

      refreshMenus: async () => {
        try {
          const data = await authApi.getUserMenus();
          set({ menus: data.menus || [] });
        } catch {
          console.error('Error al actualizar menús');
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        menus: state.menus,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
