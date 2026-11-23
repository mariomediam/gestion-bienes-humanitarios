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
import PersonasPage from '@features/personas/pages/PersonasPage'
import Formularios2ACargaPage from '@features/formularios2a/pages/Formularios2ACargaPage'
import Formularios2APage from '@features/formularios2a/pages/Formularios2APage'
import DevolucionFormPage from '@features/devoluciones/pages/DevolucionFormPage'
import DevolucionesPage from '@features/devoluciones/pages/DevolucionesPage'
import MovimientoFormPage from '@features/movimientos/pages/MovimientoFormPage'
import MovimientoVerPage from '@features/movimientos/pages/MovimientoVerPage'
import MovimientosPage from '@features/movimientos/pages/MovimientosPage'
import PlanillaBahFormPage from '@features/planillasBah/pages/PlanillaBahFormPage'
import PlanillaBahReportePage from '@features/planillasBah/pages/PlanillaBahReportePage'
import PlanillasBahPage from '@features/planillasBah/pages/PlanillasBahPage'
import KardexPage from '@features/kardex/pages/KardexPage'
import StockActualPage from '@features/stockActual/pages/StockActualPage'
import SinAccesoPage from '@features/auth/pages/SinAccesoPage'
import RequiereMenu from '@features/auth/components/RequiereMenu'


const MENU_CODIGOS = {
  EMERGENCIA: '0100000000',
  FORMULARIO_2A: '0200000000',
  MOVIMIENTO: '0300000000',
  PLANILLA_BAH: '0400000000',
  BIEN: '0901000000',
  PERSONA: '0902000000',
  CARGAR_FORMULARIO_2A: '0600000000',
  ALMACEN_STOCK_ACTUAL: '0700000000',
}

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
          <Route
            path="emergencias"
            element={
              <RequiereMenu menCodi={MENU_CODIGOS.EMERGENCIA}>
                <EmergenciasPage />
              </RequiereMenu>
            }
          />
          
          <Route path="formularios-2A" element={
            <RequiereMenu menCodi={MENU_CODIGOS.FORMULARIO_2A}>
              <Formularios2APage />
            </RequiereMenu>
          } />
          <Route path="formularios-2A/cargar" element={
            <RequiereMenu menCodi={MENU_CODIGOS.CARGAR_FORMULARIO_2A}>
              <Formularios2ACargaPage />
            </RequiereMenu>
          } />
          <Route path="bah-bienes" element={
            <RequiereMenu menCodi={MENU_CODIGOS.BIEN}>
              <BienesPage />
            </RequiereMenu>
          } />
          <Route path="personas" element={
            <RequiereMenu menCodi={MENU_CODIGOS.PERSONA}>
              <PersonasPage />
            </RequiereMenu>
          } />

          <Route path="alm-movimientos/nuevo" element={
            <RequiereMenu menCodi={MENU_CODIGOS.MOVIMIENTO} operacion="nuevo">
              <MovimientoFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-movimientos/:movimientoId/editar" element={
            <RequiereMenu menCodi={MENU_CODIGOS.MOVIMIENTO} operacion="modificar">
              <MovimientoFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-movimientos/:movimientoId/ver" element={
            <RequiereMenu menCodi={MENU_CODIGOS.MOVIMIENTO} operacion="imprimir">
              <MovimientoVerPage />
            </RequiereMenu>
          } />

          <Route path="alm-movimientos" element={
            <RequiereMenu menCodi={MENU_CODIGOS.MOVIMIENTO}>
              <MovimientosPage />
            </RequiereMenu>
          } />

          <Route path="alm-devolucion/nuevo/:movimientoOrigenId" element={
            <RequiereMenu menCodi={MENU_CODIGOS.DEVOLUCION} operacion="nuevo">
              <DevolucionFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-devolucion/:movimientoId/editar" element={
            <RequiereMenu menCodi={MENU_CODIGOS.DEVOLUCION} operacion="modificar">
              <DevolucionFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-devolucion" element={
            <RequiereMenu menCodi={MENU_CODIGOS.DEVOLUCION}>
              <DevolucionesPage />
            </RequiereMenu>
          } />
          <Route path="alm-planilla-bah/nuevo/:formulario2aId" element={
            <RequiereMenu menCodi={MENU_CODIGOS.PLANILLA_BAH} operacion="nuevo">
              <PlanillaBahFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-planilla-bah/:movimientoId/editar" element={
            <RequiereMenu menCodi={MENU_CODIGOS.PLANILLA_BAH} operacion="modificar">
              <PlanillaBahFormPage />
            </RequiereMenu>
          } />
          <Route path="alm-planilla-bah/:planillaEntregaId/reporte" element={
            <RequiereMenu menCodi={MENU_CODIGOS.PLANILLA_BAH} operacion="imprimir">
              <PlanillaBahReportePage />
            </RequiereMenu>
          } />
          <Route path="alm-planilla-bah" element={
            <RequiereMenu menCodi={MENU_CODIGOS.PLANILLA_BAH}>
              <PlanillasBahPage />
            </RequiereMenu>
          } />
          <Route path="alm-stock-actual/:bienId/kardex" element={
            <RequiereMenu menCodi={MENU_CODIGOS.ALMACEN_STOCK_ACTUAL}>
              <KardexPage />
            </RequiereMenu>
          } />
          <Route path="alm-stock-actual" element={
            <RequiereMenu menCodi={MENU_CODIGOS.ALMACEN_STOCK_ACTUAL}>
              <StockActualPage />
            </RequiereMenu>
          } />
          <Route path="formularios-2A/:formulario2aId/reporte" element={
            <RequiereMenu menCodi={MENU_CODIGOS.FORMULARIO_2A} operacion="imprimir">
              <Formulario2AReportePage />
            </RequiereMenu>
          } />

          <Route path="formularios-2A/:formulario2aId" element={
            <RequiereMenu menCodi={MENU_CODIGOS.FORMULARIO_2A}>
              <Formulario2ADetallePage />
            </RequiereMenu>
          } />
          <Route path="sin-acceso" element={<SinAccesoPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}

export default App
