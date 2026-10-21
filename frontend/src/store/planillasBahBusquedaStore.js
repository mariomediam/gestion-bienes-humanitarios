import { create } from 'zustand';

const EMPTY_FILTROS_PLANILLA_BAH = {
  anio_planilla: '',
  codigo_sinpad: '',
  barrio_sector_urbanizacion: '',
  fecha_desde: '',
  fecha_hasta: '',
  documento_referencia: '',
  integrante_receptor_nombre: '',
};

const usePlanillasBahBusquedaStore = create((set) => ({
  consulta: '',
  filtros: EMPTY_FILTROS_PLANILLA_BAH,
  avanzadaAbierta: false,
  searched: false,
  planillas: [],
  actualizarAlRegresar: false,

  setConsulta: (consulta) => set({ consulta }),

  setFiltro: (name, value) =>
    set((state) => ({
      filtros: { ...state.filtros, [name]: value },
    })),

  toggleAvanzada: () =>
    set((state) => ({
      avanzadaAbierta: !state.avanzadaAbierta,
    })),

  setResultados: (planillas) => set({ planillas, searched: true }),

  quitarPlanilla: (planillaEntregaId) =>
    set((state) => ({
      planillas: state.planillas.filter((item) => item.planilla_entrega_id !== planillaEntregaId),
    })),

  solicitarActualizacion: () => set({ actualizarAlRegresar: true }),

  limpiar: () =>
    set({
      consulta: '',
      filtros: { ...EMPTY_FILTROS_PLANILLA_BAH },
      avanzadaAbierta: false,
      searched: false,
      planillas: [],
      actualizarAlRegresar: false,
    }),
}));

export default usePlanillasBahBusquedaStore;
