import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { authApi } from '@api/authApi'

export default function RequiereMenu({ menCodi, operacion, children }) {
  const [estado, setEstado] = useState('cargando')

  useEffect(() => {
    let activo = true

    authApi.getMenuAccess(menCodi)
      .then((acceso) => {
        if (!activo) return
        const permitido = !operacion || Boolean(acceso[operacion])
        setEstado(permitido ? 'permitido' : 'denegado')
      })
      .catch(() => {
        if (activo) setEstado('denegado')
      })

    return () => {
      activo = false
    }
  }, [menCodi, operacion])

  if (estado === 'cargando') {
    return (
      <div className="flex items-center justify-center py-24">
        <p className="text-gray-600">Verificando acceso...</p>
      </div>
    )
  }

  if (estado === 'denegado') {
    return <Navigate to="/sin-acceso" replace />
  }

  return children
}