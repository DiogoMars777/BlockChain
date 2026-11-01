export interface ReportarSospechaRequest {
  uuidpublico?: string;
  numeroserie?: string;
  motivo: string;
  descripcion?: string;
  evidencia?: string;
  nombrereportante?: string;
  contactoreportante?: string;
}

export interface ReporteSospechaResponse {
  idalerta: number;
  referencia: string;
  tipoalerta: string;
  estado: string;
  mensaje: string;
}

