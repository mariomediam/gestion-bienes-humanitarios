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

  limpiar: () =>
    set({
      consulta: '',
      filtros: { ...EMPTY_FILTROS_FORMULARIO_2A },
      avanzadaAbierta: false,
      searched: false,
      formularios: [],
    }),
}));

export default useFormularios2ABusquedaStore;
