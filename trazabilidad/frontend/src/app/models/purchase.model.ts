export interface CompraDetalleItem {
  idcompradetalle: number;
  idcompra: number;
  idvariante: number;
  sku: string;
  producto_nombre: string;
  color?: string;
  almacenamiento?: string;
  cantidad: number;
  costounitariousd: number;
  subtotalusd: number;
}

export interface CompraItem {
  idcompra: number;
  idtenant: number;
  idproveedor: number;
  proveedor_nombre?: string;
  numeroorden: string;
  fechacompra: string;
  totalusd: number;
  estado: 'pendiente' | 'enviada' | 'recibida_parcial' | 'recibida_total' | 'cancelada' | string;
  total_items?: number;
  detalles?: CompraDetalleItem[];
}

export interface CompraListResponse {
  total: number;
  items: CompraItem[];
}

export interface ActionPurchaseResponse {
  message: string;
  compra: CompraItem;
}
