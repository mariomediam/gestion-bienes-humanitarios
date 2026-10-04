import Card from '@components/ui/Card'
import EmergenciaIcon from '@components/icons/EmergenciaIcon'
import FormularioIcon from '@components/icons/FormularioIcon'
import PlanillaIcon from '@components/icons/PlanillaIcon'
import PersonasIcon from '@components/icons/PersonasIcon'
import TipoPeligroIcon from '@components/icons/TipoPeligroIcon'
import useDashboard from '@features/home/hooks/useDashboard'
import EmergenciasUltimoMes from '@features/home/components/EmergenciasUltimoMes'

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Cargando dashboard...</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { loading, totales, tiposPeligro, emergencias } = useDashboard()

  if (loading) {
    return <LoadingState />
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1e3064]">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Card title="Emergencias registradas" value={totales.emergencias ?? '—'} icon={EmergenciaIcon} iconClassName="bg-red-100 text-red-600" />
        <Card title="Formularios EDAN 2A" value={totales.formularios2a ?? '—'} icon={FormularioIcon} iconClassName="bg-blue-100 text-blue-600" />
        <Card title="Planillas BAH" value={totales.planillasBah ?? '—'} icon={PlanillaIcon} iconClassName="bg-emerald-100 text-emerald-600" />
        <Card title="Personas atendidas" value={totales.integrantes ?? '—'} icon={PersonasIcon} iconClassName="bg-violet-100 text-violet-600" />
      </div>

      <Card title="Tipos de peligro" icon={TipoPeligroIcon} iconClassName="bg-amber-100 text-amber-600">
        {tiposPeligro.length === 0 ? (
          <p className="mt-3 text-sm text-gray-500">No hay tipos de peligro registrados</p>
        ) : (
          <ul className="mt-3 divide-y divide-gray-100">
            {tiposPeligro.map((tipo) => (
              <li key={tipo.tipo_peligro_id} className="flex items-center justify-between gap-4 py-2 text-sm">
                <span className="text-gray-700">{tipo.nombre_peligro}</span>
                <span className="font-semibold text-[#1e3064]">{tipo.total}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <EmergenciasUltimoMes emergencias={emergencias} />
    </div>
  )
}
