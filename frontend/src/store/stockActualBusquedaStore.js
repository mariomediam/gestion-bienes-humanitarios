import { create } from 'zustand';

const useStockActualBusquedaStore = create((set) => ({
  bien: null,
  searched: false,
  filas: [],

  setBien: (bien) => set({ bien }),

  setResultados: (filas) => set({ filas, searched: true }),

  limpiar: () =>
    set({
      bien: null,
      searched: false,
      filas: [],
    }),
}));

export default useStockActualBusquedaStore;
