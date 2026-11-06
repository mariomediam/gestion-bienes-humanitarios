import { create } from 'zustand';

const EMPTY_FILTROS_DEVOLUCION = {
  fecha_desde: '',
  fecha_hasta: '',
  documento_referencia: '',
  numero_planilla: '',
};

const useDevolucionesBusquedaStore = create((set) => ({
  bienNombre: '',
  filtros: EMPTY_FILTROS_DEVOLUCION,
  avanzadaAbierta: false,
  searched: false,
  devoluciones: [],
  actualizarAlRegresar: false,
  devolucionCreadaId: null,

  setBienNombre: (bienNombre) => set({ bienNombre }),

  setFiltro: (name, value) =>
    set((state) => ({
      filtros: { ...state.filtros, [name]: value },
    })),

  toggleAvanzada: () =>
    set((state) => ({
      avanzadaAbierta: !state.avanzadaAbierta,
    })),

  setResultados: (devoluciones) => set({ devoluciones, searched: true }),

  quitarDevolucion: (movimientoId) =>
    set((state) => ({
      devoluciones: state.devoluciones.filter((item) => item.movimiento_id !== movimientoId),
    })),

  solicitarActualizacion: () => set({ actualizarAlRegresar: true }),

  prepararDevolucionCreada: (movimientoId) =>
    set({
      bienNombre: '',
      filtros: { ...EMPTY_FILTROS_DEVOLUCION },
      avanzadaAbierta: false,
      searched: true,
      devoluciones: [],
      actualizarAlRegresar: false,
      devolucionCreadaId: movimientoId,
    }),

  limpiar: () =>
    set({
      bienNombre: '',
      filtros: { ...EMPTY_FILTROS_DEVOLUCION },
      avanzadaAbierta: false,
      searched: false,
      devoluciones: [],
      actualizarAlRegresar: false,
      devolucionCreadaId: null,
    }),
}));

export default useDevolucionesBusquedaStore;
