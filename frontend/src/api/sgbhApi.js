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

  getTiposUsoInstalacion: async (params) => {
    const response = await api.get('/api/sgbh/tipos-uso-instalacion/', { params })
    return response.data
  },

  getCondicionesVivienda: async (params) => {
    const response = await api.get('/api/sgbh/condiciones-vivienda/', { params })
    return response.data
  },

  getMaterialesPared: async (params) => {
    const response = await api.get('/api/sgbh/materiales-pared/', { params })
    return response.data
  },

  getMaterialesPiso: async (params) => {
    const response = await api.get('/api/sgbh/materiales-piso/', { params })
    return response.data
  },

  getMaterialesTecho: async (params) => {
    const response = await api.get('/api/sgbh/materiales-techo/', { params })
    return response.data
  },

  buscarDistritos: async (params) => {
    const response = await api.get('/api/sgbh/distritos/buscar/', { params })
    return response.data
  },

  buscarFormularios2A: async (params) => {
    const response = await api.get('/api/sgbh/formularios-2a/buscar/', { params })
    return response.data
  },

  crearFormulario2A: async (data) => {
    const response = await api.post('/api/sgbh/formularios-2a/', data)
    return response.data
  },

  actualizarFormulario2A: async (formulario2aId, data) => {
    const response = await api.put(`/api/sgbh/formularios-2a/${formulario2aId}/`, data)
    return response.data
  },

  getFormulario2A: async (formulario2aId) => {
    const response = await api.get(`/api/sgbh/formularios-2a/${formulario2aId}/`)
    return response.data
  },

  buscarViviendas: async (params) => {
    const response = await api.get('/api/sgbh/viviendas/buscar/', { params })
    return response.data
  },

  crearVivienda: async (data) => {
    const response = await api.post('/api/sgbh/viviendas/', data)
    return response.data
  },

  actualizarVivienda: async (viviendaId, data) => {
    const response = await api.put(`/api/sgbh/viviendas/${viviendaId}/`, data)
    return response.data
  },

  eliminarVivienda: async (viviendaId) => {
    await api.delete(`/api/sgbh/viviendas/${viviendaId}/`)
  },

  buscarFamilias: async (params) => {
    const response = await api.get('/api/sgbh/familias/buscar/', { params })
    return response.data
  },

  crearFamilia: async (data) => {
    const response = await api.post('/api/sgbh/familias/', data)
    return response.data
  },

  buscarEvaluadores: async (params) => {
    const response = await api.get('/api/sgbh/personal/buscar/evaluadores/', { params })
    return response.data
  },
}
