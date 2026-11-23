import { Link } from 'react-router-dom'


const SinAccesoPage = () => {
    return (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <p className="text-sm font-semibold text-[#1e3064]">403</p>
          <h1 className="mt-2 text-2xl font-bold text-[#1e3064]">Sin acceso</h1>
          <p className="mt-3 max-w-md text-gray-600">
            No tienes permiso para ver esta página. El intento de acceso fue registrado.
          </p>
          <Link
            to="/"
            className="mt-6 rounded-lg bg-[#1e3064] px-4 py-2 text-sm font-medium text-white hover:bg-[#16264d]"
          >
            Volver al inicio
          </Link>
        </div>
      )
}

export default SinAccesoPage