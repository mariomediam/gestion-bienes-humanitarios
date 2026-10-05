import api from '@api/axios'

export const sgbhApi = {
  getTotalEmergencias: async () => {
    const response = await api.get('/api/sgbh/emergencias/total/')
    return response.data
  },

  getTotalFormularios2A: async () => {
    const response = await api.get('/api/sgbh/formularios-2a/total/')
    return response.data
  },

  getTotalPlanillasBah: async () => {
    const response = await api.get('/api/sgbh/planillas-bah/total/')
    return response.data
  },

  getTotalIntegrantes: async () => {
    const response = await api.get('/api/sgbh/integrantes/total/')
    return response.data
  },

  getTotalPorTipoPeligro: async () => {
    const response = await api.get('/api/sgbh/emergencias/total-por-tipo-peligro/')
    return response.data
  },

  getEmergencias: async (params) => {
    const response = await api.get('/api/sgbh/emergencias/', { params })
    return response.data
  },

  buscarEmergencias: async (params) => {
    const response = await api.get('/api/sgbh/emergencias/buscar/', { params })
    return response.data
  },

  crearEmergencia: async (data) => {
    const response = await api.post('/api/sgbh/emergencias/', data)
    return response.data
  },

  actualizarEmergencia: async (emergenciaId, data) => {
    const response = await api.put(`/api/sgbh/emergencias/${emergenciaId}/`, data)
    return response.data
  },

  eliminarEmergencia: async (emergenciaId) => {
    await api.delete(`/api/sgbh/emergencias/${emergenciaId}/`)
  },

  getTiposPeligro: async (params) => {
    const response = await api.get('/api/sgbh/tipos-peligro/', { params })
    return response.data
  },
}
