import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { Toaster } from 'sonner'
import useAuthStore from '@store/authStore'
import LoginPage from '@features/auth/pages/LoginPage'
import MainLayout from '@components/layout/MainLayout'
import DashboardPage from '@features/home/pages/DashboardPage'
import EmergenciasPage from '@features/emergencias/pages/EmergenciasPage'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />
}

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  return isAuthenticated ? <Navigate to="/" replace /> : children
}

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        richColors
        closeButton
        expand={false}
        duration={4000}
      />
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="emergencias" element={<EmergenciasPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
