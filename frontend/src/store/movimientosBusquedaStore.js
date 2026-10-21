import { create } from 'zustand';

const EMPTY_FILTROS_MOVIMIENTO = {
  fecha_desde: '',
  fecha_hasta: '',
  tipo_movimiento_id: '',
  documento_referencia: '',
  destinatario: '',
};

const useMovimientosBusquedaStore = create((set) => ({
  bienNombre: '',
  filtros: EMPTY_FILTROS_MOVIMIENTO,
  avanzadaAbierta: false,
  searched: false,
  movimientos: [],
  actualizarAlRegresar: false,
  movimientoCreadoId: null,

  setBienNombre: (bienNombre) => set({ bienNombre }),

  setFiltro: (name, value) =>
    set((state) => ({
      filtros: { ...state.filtros, [name]: value },
    })),

  toggleAvanzada: () =>
    set((state) => ({
      avanzadaAbierta: !state.avanzadaAbierta,
    })),

  setResultados: (movimientos) => set({ movimientos, searched: true }),

  quitarMovimiento: (movimientoId) =>
    set((state) => ({
      movimientos: state.movimientos.filter((item) => item.movimiento_id !== movimientoId),
    })),

  solicitarActualizacion: () => set({ actualizarAlRegresar: true }),

  prepararMovimientoCreado: (movimientoId) =>
    set({
      bienNombre: '',
      filtros: { ...EMPTY_FILTROS_MOVIMIENTO },
      avanzadaAbierta: false,
      searched: true,
      movimientos: [],
      actualizarAlRegresar: false,
      movimientoCreadoId: movimientoId,
    }),

  limpiar: () =>
    set({
      bienNombre: '',
      filtros: { ...EMPTY_FILTROS_MOVIMIENTO },
      avanzadaAbierta: false,
      searched: false,
      movimientos: [],
      actualizarAlRegresar: false,
      movimientoCreadoId: null,
    }),
}));

export default useMovimientosBusquedaStore;
