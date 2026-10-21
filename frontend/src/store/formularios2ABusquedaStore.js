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
  formularioCreadoId: null,

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

  quitarFormulario: (formulario2aId) =>
    set((state) => ({
      formularios: state.formularios.filter(
        (item) => item.formulario_2a_id !== formulario2aId,
      ),
    })),

  solicitarActualizacion: () => set({ actualizarAlRegresar: true }),

  prepararFormularioCreado: (formulario2aId) =>
    set({
      consulta: '',
      filtros: { ...EMPTY_FILTROS_FORMULARIO_2A },
      avanzadaAbierta: false,
      searched: true,
      formularios: [],
      actualizarAlRegresar: false,
      formularioCreadoId: formulario2aId,
    }),

  limpiar: () =>
    set({
      consulta: '',
      filtros: { ...EMPTY_FILTROS_FORMULARIO_2A },
      avanzadaAbierta: false,
      searched: false,
      formularios: [],
      actualizarAlRegresar: false,
      formularioCreadoId: null,
    }),
}));

export default useFormularios2ABusquedaStore;
