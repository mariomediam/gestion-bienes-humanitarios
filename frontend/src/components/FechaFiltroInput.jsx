import { format } from '@formkit/tempo'
import '@components/fechaFiltro.css'

const inputClassName =
  'fecha-filtro w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50'

function textoVisible(value) {
  if (!value) return 'dd/mm/yyyy'
  return format(String(value).slice(0, 10), 'DD/MM/YYYY', 'es')
}

export default function FechaFiltroInput({ id, value, onChange, disabled }) {
  return (
    <div className="relative">
      <input
        id={id}
        type="date"
        lang="es-PE"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        className={inputClassName}
      />
      <span
        aria-hidden="true"
        className={`pointer-events-none absolute inset-y-0 left-3 right-10 flex items-center text-sm ${
          value ? (disabled ? 'text-gray-500' : 'text-gray-800') : 'text-gray-400'
        }`}
      >
        {textoVisible(value)}
      </span>
    </div>
  )
}
