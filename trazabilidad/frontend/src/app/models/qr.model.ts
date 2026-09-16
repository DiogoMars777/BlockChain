export interface UnitQrItem {
  idunidad: number;
  numeroserie: string;
  imei1?: string;
  imei2?: string;
  uuidpublico: string;
  estado: string;
  producto_nombre: string;
  variante_sku: string;
  color?: string;
  almacenamiento?: string;
  tiene_qr: boolean;
  idcodigoqr?: number;
  tokenpublico?: string;
  url?: string;
  fechageneracion?: string;
}

export interface GenerateQRResult {
  idcodigoqr: number;
  idunidad: number;
  numeroserie: string;
  uuidpublico: string;
  tokenpublico: string;
  url: string;
  fechageneracion: string;
  qr_image_url: string;
  message: string;
}

export interface BulkQRResponse {
  total_generados: number;
  items: GenerateQRResult[];
}
