import { useState } from 'react'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import PersonaEliminarModal from '@features/personas/components/PersonaEliminarModal'
import {
  textoActivo,
  textoCelda,
  textoDocumentoPersona,
  textoFechaNacimiento,
  textoNombrePersona,
  textoSexo,
} from '@features/personas/presentacion'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

export default function PersonasResultados({ personas, onModificar, onEliminado }) {
  const [personaAEliminar, setPersonaAEliminar] = useState(null)

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Nombre</th>
              <th scope="col" className="px-5 py-3 font-medium">Documento</th>
              <th scope="col" className="px-5 py-3 font-medium">Fecha de nacimiento</th>
              <th scope="col" className="px-5 py-3 font-medium">Sexo</th>
              <th scope="col" className="px-5 py-3 font-medium">Teléfono</th>
              <th scope="col" className="px-5 py-3 font-medium">Correo</th>
              <th scope="col" className="px-5 py-3 font-medium">Activo</th>
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {personas.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron personas
                </td>
              </tr>
            ) : (
              personas.map((persona) => (
                <tr key={persona.persona_id} className="border-t border-gray-100">
                  <td className="px-5 py-3 text-gray-800">{textoCelda(textoNombrePersona(persona))}</td>
                  <td className="px-5 py-3 text-gray-800">{textoCelda(textoDocumentoPersona(persona))}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {textoCelda(textoFechaNacimiento(persona.fecha_nacimiento))}
                  </td>
                  <td className="px-5 py-3 text-gray-800">{textoCelda(textoSexo(persona.sexo))}</td>
                  <td className="px-5 py-3 text-gray-800">{textoCelda(persona.telefono)}</td>
                  <td className="px-5 py-3 text-gray-800">{textoCelda(persona.correo)}</td>
                  <td className="px-5 py-3 text-gray-800">{textoActivo(persona.esta_activo)}</td>
                  <td className="relative z-10 px-5 py-3 whitespace-nowrap">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        aria-label="Modificar"
                        onClick={() => onModificar(persona)}
                        className={actionButtonClassName}
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Modificar
                        </span>
                      </button>
                      <button
                        type="button"
                        aria-label="Eliminar"
                        onClick={() => setPersonaAEliminar(persona)}
                        className={deleteButtonClassName}
                      >
                        <TrashIcon className="w-4 h-4" />
                        <span className={deleteTooltipClassName} aria-hidden="true">
                          Eliminar
                        </span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <PersonaEliminarModal
        isOpen={personaAEliminar !== null}
        persona={personaAEliminar}
        onClose={() => setPersonaAEliminar(null)}
        onEliminado={onEliminado}
      />
    </section>
  )
}
