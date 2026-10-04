export interface RecepcionDetalleItem {
  idrecepciondetalle: number;
  idvariante: number;
  sku?: string;
  producto_nombre?: string;
  cantidadesperada: number;
  cantidadrecibida: number;
  unidades_generadas: number;
}

export interface RecepcionItem {
  idrecepcion: number;
  idtenant: number;
  idcompra: number;
  numeroorden?: string;
  idproveedor?: number;
  proveedor_nombre?: string;
  idubicacion: number;
  ubicacion_nombre?: string;
  fecharecepcion?: string;
  numerodocumento: string;
  estado: 'pendiente' | 'parcial' | 'completa' | 'rechazada' | string;
  total_recibido: number;
}

export interface RecepcionDetalle extends RecepcionItem {
  detalles: RecepcionDetalleItem[];
}

export interface RecepcionDetalleInput {
  idvariante: number;
  cantidadesperada: number;
  cantidadrecibida: number;
}

export interface RecepcionCreate {
  idcompra: number;
  idubicacion: number;
  numerodocumento: string;
  estado: string;
  detalles: RecepcionDetalleInput[];
}

export interface RecepcionActionResponse {
  message: string;
  recepcion: RecepcionDetalle;
}
