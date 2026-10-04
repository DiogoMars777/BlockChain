export interface CondicionTransporte {
  idcondicion: number;
  idevento: number;
  temperatura?: number;
  humedad?: number;
  presion?: number;
  nivelvibracion?: number;
  timestampregistro?: string;
  fuentedatos?: string;
}

export interface CondicionTransporteInput {
  temperatura?: number;
  humedad?: number;
  presion?: number;
  nivelvibracion?: number;
  fuentedatos?: string;
}

export interface EventoTrazabilidadItem {
  idevento: number;
  idtenant: number;
  tipoevento: string;
  fechahora: string;
  idubicacion: number;
  ubicacion_nombre?: string;
  usuario_nombre?: string;
  descripcion?: string;
  payloadhash?: string;
  estadoverificacion?: string;
  condiciones?: CondicionTransporte;
}

export interface EnvioItem {
  idenvio: number;
  idtenant: number;
  codigoenvio: string;
  idactororigen: number;
  idactordestino: number;
  idtransportista?: number;
  actor_origen_nombre?: string;
  actor_destino_nombre?: string;
  transportista_nombre?: string;
  fechasalida?: string;
  fechaestimada?: string;
  fechaentrega?: string;
  estado: 'preparacion' | 'en_transito' | 'entregado' | 'retrasado' | 'cancelado' | string;
  trackingexterno?: string;
  total_unidades: number;
}

export interface EnvioUnidadItem {
  idenviounidad: number;
  idunidad: number;
  numeroserie: string;
  idvariante?: number;
  sku?: string;
  producto_nombre?: string;
  estado?: string;
}

export interface EnvioDetalle extends EnvioItem {
  unidades: EnvioUnidadItem[];
}

export interface EnvioCreate {
  idactororigen: number;
  idactordestino: number;
  idtransportista?: number;
  codigoenvio: string;
  fechaestimada?: string;
  trackingexterno?: string;
}

export interface EnvioUpdate {
  idactordestino?: number;
  idtransportista?: number | null;
  fechaestimada?: string;
  trackingexterno?: string;
}

export interface EnvioTimelineResponse {
  envio: EnvioItem;
  eventos: EventoTrazabilidadItem[];
  unidades_numeros: string[];
}

export interface EnvioUnidadCandidateItem {
  idunidad: number;
  numeroserie: string;
  idvariante: number;
  sku?: string;
  producto_nombre?: string;
  estado?: string;
  idrecepciondetalle?: number;
}

export interface EnvioUnidadAsignadaItem extends EnvioUnidadCandidateItem {
  idenviounidad: number;
}

export interface EnvioUnidadesResponse {
  idenvio: number;
  codigoenvio: string;
  estado: string;
  asignadas: EnvioUnidadAsignadaItem[];
  disponibles: EnvioUnidadCandidateItem[];
}

export interface EnvioUnidadActionResponse {
  message: string;
  unidades: EnvioUnidadAsignadaItem[];
}

export interface CreateTransportEventPayload {
  tipoevento: string;
  idubicacion: number;
  descripcion?: string;
  idactordestino?: number;
  condiciones?: CondicionTransporteInput;
}
