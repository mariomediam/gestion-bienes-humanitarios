import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { pathname } = useLocation()
  const esReporte = pathname.endsWith('/reporte')

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} />

        <main className={esReporte ? 'flex-1 overflow-auto bg-gray-200 p-4' : 'flex-1 overflow-y-auto p-6'}>
          <div className={esReporte ? '' : 'max-w-7xl mx-auto'}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
