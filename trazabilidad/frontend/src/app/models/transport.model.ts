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

export interface EnvioTimelineResponse {
  envio: EnvioItem;
  eventos: EventoTrazabilidadItem[];
  unidades_numeros: string[];
}

export interface CreateTransportEventPayload {
  tipoevento: string;
  idubicacion: number;
  descripcion?: string;
  idactordestino?: number;
  condiciones?: CondicionTransporteInput;
}
