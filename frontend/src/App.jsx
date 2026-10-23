import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { Toaster } from 'sonner'
import useAuthStore from '@store/authStore'
import LoginPage from '@features/auth/pages/LoginPage'
import MainLayout from '@components/layout/MainLayout'
import DashboardPage from '@features/home/pages/DashboardPage'
import EmergenciasPage from '@features/emergencias/pages/EmergenciasPage'
import Formulario2ADetallePage from '@features/formularios2a/pages/Formulario2ADetallePage'
import Formulario2AReportePage from '@features/formularios2a/pages/Formulario2AReportePage'
import BienesPage from '@features/bienes/pages/BienesPage'
import Formularios2APage from '@features/formularios2a/pages/Formularios2APage'
import MovimientoFormPage from '@features/movimientos/pages/MovimientoFormPage'
import MovimientoVerPage from '@features/movimientos/pages/MovimientoVerPage'
import MovimientosPage from '@features/movimientos/pages/MovimientosPage'
import PlanillaBahFormPage from '@features/planillasBah/pages/PlanillaBahFormPage'
import PlanillaBahReportePage from '@features/planillasBah/pages/PlanillaBahReportePage'
import PlanillasBahPage from '@features/planillasBah/pages/PlanillasBahPage'
import KardexPage from '@features/kardex/pages/KardexPage'
import StockActualPage from '@features/stockActual/pages/StockActualPage'

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
          <Route path="formularios-2A" element={<Formularios2APage />} />
          <Route path="bah-bienes" element={<BienesPage />} />
          <Route path="alm-movimientos/nuevo" element={<MovimientoFormPage />} />
          <Route path="alm-movimientos/:movimientoId/editar" element={<MovimientoFormPage />} />
          <Route path="alm-movimientos/:movimientoId/ver" element={<MovimientoVerPage />} />
          <Route path="alm-movimientos" element={<MovimientosPage />} />
          <Route path="alm-planilla-bah/nuevo/:formulario2aId" element={<PlanillaBahFormPage />} />
          <Route path="alm-planilla-bah/:movimientoId/editar" element={<PlanillaBahFormPage />} />
          <Route path="alm-planilla-bah/:planillaEntregaId/reporte" element={<PlanillaBahReportePage />} />
          <Route path="alm-planilla-bah" element={<PlanillasBahPage />} />
          <Route path="alm-stock-actual/:bienId/kardex" element={<KardexPage />} />
          <Route path="alm-stock-actual" element={<StockActualPage />} />
          <Route path="formularios-2A/:formulario2aId/reporte" element={<Formulario2AReportePage />} />
          <Route path="formularios-2A/:formulario2aId" element={<Formulario2ADetallePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
