export interface Plan {
  idplan: number;
  codigo: string;
  nombre: string;
  descripcion?: string | null;
  preciomensual: number | string;
  precioanual: number | string;
  moneda: string;
  limiteusuarios: number;
  limiteunidades: number;
  limitereportesmes: number;
  limitealmacenamientomb: number;
  diastrial: number;
  activo: boolean;
  creadoen?: string;
  actualizadoen?: string;
}

export interface PlanListResponse {
  total: number;
  skip: number;
  limit: number;
  items: Plan[];
}

export interface PlanCreate {
  codigo: string;
  nombre: string;
  descripcion?: string;
  preciomensual: number;
  precioanual: number;
  moneda?: string;
  limiteusuarios?: number;
  limiteunidades?: number;
  limitereportesmes?: number;
  limitealmacenamientomb?: number;
  diastrial?: number;
  activo?: boolean;
}

export interface PlanUpdate {
  nombre?: string;
  descripcion?: string;
  preciomensual?: number;
  precioanual?: number;
  moneda?: string;
  limiteusuarios?: number;
  limiteunidades?: number;
  limitereportesmes?: number;
  limitealmacenamientomb?: number;
  diastrial?: number;
  activo?: boolean;
}

export interface Suscripcion {
  idsuscripcion: number;
  idtenant: number;
  idplan: number;
  estado: 'trial' | 'activa' | 'vencida' | 'cancelada' | 'suspendida';
  fechainicio: string;
  fechafin: string;
  renovacionautomatica: boolean;
  motivocancelacion?: string | null;
  creadoen?: string;
  actualizadoen?: string;
  plan?: Plan | null;
  nombretenant?: string | null;
  codigoplan?: string | null;
  nombreplan?: string | null;
  diasrestantes?: number;
}

export interface SuscripcionListResponse {
  total: number;
  skip: number;
  limit: number;
  items: Suscripcion[];
}

export interface SuscribirEmpresaRequest {
  idtenant: number;
  idplan: number;
  diasvigencia?: number;
  renovacionautomatica?: boolean;
}

export interface CambiarPlanRequest {
  idplan: number;
  diasvigencia?: number;
  renovacionautomatica?: boolean;
}

export interface UpdateSuscripcionEstadoRequest {
  estado: 'activa' | 'vencida' | 'cancelada' | 'suspendida';
  motivocancelacion?: string;
}

