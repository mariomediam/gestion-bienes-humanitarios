import { create } from 'zustand';

export const EMPTY_FILTROS_FORMULARIO_2A = {
  tipoPeligro: null,
  distrito: null,
  fecha_desde: '',
  fecha_hasta: '',
  localidad: '',
};

const useFormularios2ABusquedaStore = create((set) => ({
  consulta: '',
  filtros: EMPTY_FILTROS_FORMULARIO_2A,
  avanzadaAbierta: false,
  searched: false,
  formularios: [],
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

  setResultados: (formularios) => set({ formularios, searched: true }),

  solicitarActualizacion: () => set({ actualizarAlRegresar: true }),

  limpiar: () =>
    set({
      consulta: '',
      filtros: { ...EMPTY_FILTROS_FORMULARIO_2A },
      avanzadaAbierta: false,
      searched: false,
      formularios: [],
      actualizarAlRegresar: false,
    }),
}));

export default useFormularios2ABusquedaStore;
