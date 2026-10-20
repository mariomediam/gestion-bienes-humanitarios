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

  getRolesFamiliares: async (params) => {
    const response = await api.get('/api/sgbh/roles-familiares/', { params })
    return response.data
  },

  getCondicionesPersona: async (params) => {
    const response = await api.get('/api/sgbh/condiciones-persona/', { params })
    return response.data
  },

  getUnidadesMedida: async (params) => {
    const response = await api.get('/api/sgbh/unidades-medida/', { params })
    return response.data
  },

  getCategoriasBienes: async (params) => {
    const response = await api.get('/api/sgbh/categorias-bienes/', { params })
    return response.data
  },

  buscarBienes: async (params) => {
    const response = await api.get('/api/sgbh/bienes/buscar/', { params })
    return response.data
  },

  crearBien: async (data) => {
    const response = await api.post('/api/sgbh/bienes/', data)
    return response.data
  },

  actualizarBien: async (bienId, data) => {
    const response = await api.patch(`/api/sgbh/bienes/${bienId}/`, data)
    return response.data
  },

  eliminarBien: async (bienId) => {
    await api.delete(`/api/sgbh/bienes/${bienId}/`)
  },

  getCategoriasMediosVida: async (params) => {
    const response = await api.get('/api/sgbh/categorias-medios-vida/', { params })
    return response.data
  },

  getTiposMediosVida: async (params) => {
    const response = await api.get('/api/sgbh/tipos-medios-vida/', { params })
    return response.data
  },

  getTiposMovimiento: async (params) => {
    const response = await api.get('/api/sgbh/tipos-movimiento/', { params })
    return response.data
  },

  crearMovimiento: async (data) => {
    const response = await api.post('/api/sgbh/movimientos/', data)
    return response.data
  },

  actualizarMovimiento: async (movimientoId, data) => {
    const response = await api.put(`/api/sgbh/movimientos/${movimientoId}/`, data)
    return response.data
  },

  eliminarMovimiento: async (movimientoId) => {
    await api.delete(`/api/sgbh/movimientos/${movimientoId}/`)
  },

  buscarMovimientos: async (params) => {
    const response = await api.get('/api/sgbh/movimientos/buscar/', { params })
    return response.data
  },

  buscarPlanillasBah: async (params) => {
    const response = await api.get('/api/sgbh/movimientos/buscar-planilla-bah/', { params })
    return response.data
  },

  getTiposDanioPersonal: async (params) => {
    const response = await api.get('/api/sgbh/tipos-danio-personal/', { params })
    return response.data
  },

  getGradosLesion: async (params) => {
    const response = await api.get('/api/sgbh/grados-lesion/', { params })
    return response.data
  },

  getTiposDiscapacidad: async (params) => {
    const response = await api.get('/api/sgbh/tipos-discapacidad/', { params })
    return response.data
  },

  getTiposDocumento: async (params) => {
    const response = await api.get('/api/sgbh/tipos-documento/', { params })
    return response.data
  },

  getEnfermedadesCronicas: async (params) => {
    const response = await api.get('/api/sgbh/enfermedades-cronicas/', { params })
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

  getFormulario2AReporte: async (formulario2aId) => {
    const response = await api.get(`/api/sgbh/formularios-2a/${formulario2aId}/reporte/`)
    return response.data
  },

  formulario2ATienePlanillaBah: async (formulario2aId) => {
    const response = await api.get(
      `/api/sgbh/formularios-2a/${formulario2aId}/tiene-planilla-bah/`,
    )
    return response.data
  },

  crearPlanillaBah: async (data) => {
    const response = await api.post('/api/sgbh/planillas-bah/', data)
    return response.data
  },

  actualizarPlanillaBah: async (planillaEntregaId, data) => {
    const response = await api.put(`/api/sgbh/planillas-bah/${planillaEntregaId}/`, data)
    return response.data
  },

  eliminarPlanillaBah: async (planillaEntregaId) => {
    await api.delete(`/api/sgbh/planillas-bah/${planillaEntregaId}/`)
  },

  getPlanillaBahReporte: async (planillaEntregaId) => {
    const response = await api.get(`/api/sgbh/planillas-bah/${planillaEntregaId}/reporte/`)
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

  eliminarFamilia: async (familiaId) => {
    await api.delete(`/api/sgbh/familias/${familiaId}/`)
  },

  buscarIntegrantes: async (params) => {
    const response = await api.get('/api/sgbh/integrantes/buscar/', { params })
    return response.data
  },

  crearIntegrante: async (data) => {
    const response = await api.post('/api/sgbh/integrantes/', data)
    return response.data
  },

  actualizarIntegrante: async (integranteId, data) => {
    const response = await api.put(`/api/sgbh/integrantes/${integranteId}/`, data)
    return response.data
  },

  eliminarIntegrante: async (integranteId) => {
    await api.delete(`/api/sgbh/integrantes/${integranteId}/`)
  },

  buscarMediosVida: async (params) => {
    const response = await api.get('/api/sgbh/medios-vida/buscar/', { params })
    return response.data
  },

  crearMedioVida: async (data) => {
    const response = await api.post('/api/sgbh/medios-vida/', data)
    return response.data
  },

  actualizarMedioVida: async (medioVidaId, data) => {
    const response = await api.put(`/api/sgbh/medios-vida/${medioVidaId}/`, data)
    return response.data
  },

  eliminarMedioVida: async (medioVidaId) => {
    await api.delete(`/api/sgbh/medios-vida/${medioVidaId}/`)
  },

  buscarPersonas: async (params) => {
    const response = await api.get('/api/sgbh/personas/buscar/', { params })
    return response.data
  },

  crearPersona: async (data) => {
    const response = await api.post('/api/sgbh/personas/', data)
    return response.data
  },

  actualizarPersona: async (personaId, data) => {
    const response = await api.put(`/api/sgbh/personas/${personaId}/`, data)
    return response.data
  },

  buscarEvaluadores: async (params) => {
    const response = await api.get('/api/sgbh/personal/buscar/evaluadores/', { params })
    return response.data
  },

  buscarEncargadosAlmacen: async (params) => {
    const response = await api.get('/api/sgbh/personal/buscar/encargados-almacen/', { params })
    return response.data
  },
}
