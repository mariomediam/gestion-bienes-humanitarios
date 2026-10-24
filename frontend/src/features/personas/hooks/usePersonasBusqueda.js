import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function usePersonasBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [personas, setPersonas] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarPersonas(params)
      setPersonas(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de personas'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setPersonas([])
    setSearched(false)
  }

  function reemplazarPersona(persona) {
    setPersonas((current) =>
      current.map((item) => (item.persona_id === persona.persona_id ? persona : item)),
    )
  }

  function quitarPersona(personaId) {
    setPersonas((current) => current.filter((item) => item.persona_id !== personaId))
  }

  return {
    loading,
    searched,
    personas,
    buscar,
    limpiarResultados,
    reemplazarPersona,
    quitarPersona,
  }
}
