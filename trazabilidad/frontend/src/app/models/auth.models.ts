export interface Tenant {
  idtenant: number;
  nombre: string;
  razonsocial: string;
  nit: string;
  email: string;
  telefono?: string;
  activo?: boolean;
  fechacreacion?: string;

  // Fallback / legacy UI getters
  id?: string | number;
  name?: string;
  slug?: string;
}

export interface TenantCreate {
  nombre: string;
  razonsocial: string;
  nit: string;
  email: string;
  telefono?: string;
  activo?: boolean;
}

export interface TenantUpdate {
  nombre?: string;
  razonsocial?: string;
  nit?: string;
  email?: string;
  telefono?: string;
  activo?: boolean;
}

export interface TenantListResponse {
  total: number;
  items: Tenant[];
}

export interface User {
  idusuario: number;
  nombrecompleto: string;
  email: string;
  activo?: boolean;
  fecharegistro?: string;
  tenant?: Tenant;

  // Fallback / legacy UI getters
  id?: string | number;
  tenant_id?: string | number;
  first_name?: string;
  last_name?: string;
}

export interface UserCreate {
  nombrecompleto: string;
  email: string;
  contrasena: string;
  idtenant?: number;
  activo?: boolean;
}

export interface UserUpdate {
  nombrecompleto?: string;
  email?: string;
  contrasena?: string;
  activo?: boolean;
}

export interface UserListResponse {
  total: number;
  items: User[];
}

export interface Role {
  idrol: number;
  nombrerol: string;
  descripcion?: string;
}

export interface Permission {
  idpermiso: number;
  nombrepermiso: string;
  descripcion?: string;
  modulo?: string;
}

export interface RolePermissionsResponse {
  role: Role;
  permissions: Permission[];
}

export interface UserRolesResponse {
  idusuario: number;
  idusuariotenant: number;
  nombrecompleto: string;
  roles: Role[];
}

export interface BitacoraItem {
  idbitacora: number;
  idusuariotenant: number;
  accion: string;
  entidad: string;
  identidad?: number;
  ip?: string;
  fechahora: string;
}

export interface BitacoraListResponse {
  total: number;
  items: BitacoraItem[];
}

export interface NotificacionItem {
  idnotificacion: number;
  idusuariotenant: number;
  titulo: string;
  contenido: string;
  leida: boolean;
  fechaenvio: string;
  fechalectura?: string;
  enlaceaccion?: string;
}

export interface NotificacionListResponse {
  total: number;
  unread_count: number;
  items: NotificacionItem[];
}

// Category models (CU-009)
export interface Category {
  idcategoria: number;
  nombrecategoria: string;
  descripcion?: string;
}

export interface CategoryCreate {
  nombrecategoria: string;
  descripcion?: string;
}

export interface CategoryUpdate {
  nombrecategoria?: string;
  descripcion?: string;
}

// Variant models (CU-006)
export interface Variant {
  idvariante: number;
  idproducto: number;
  capacidad?: string;
  color?: string;
  sku: string;
  preciousd: number;
}

export interface VariantCreate {
  capacidad?: string;
  color?: string;
  sku: string;
  preciousd: number;
}

export interface VariantUpdate {
  capacidad?: string;
  color?: string;
  sku?: string;
  preciousd?: number;
}

// Product models (CU-006)
export interface Product {
  idproducto: number;
  idcategoria?: number;
  nombre: string;
  modelo?: string;
  paisorigen?: string;
  descripcion?: string;
  imagenurl?: string;
  fechacreacion: string;
  activo: boolean;
  categoria?: Category;
  variantes: Variant[];
}

export interface ProductCreate {
  nombre: string;
  idcategoria?: number;
  modelo?: string;
  paisorigen?: string;
  descripcion?: string;
  imagenurl?: string;
  activo?: boolean;
}

export interface ProductUpdate {
  nombre?: string;
  idcategoria?: number;
  modelo?: string;
  paisorigen?: string;
  descripcion?: string;
  imagenurl?: string;
  activo?: boolean;
}

export interface ProductListResponse {
  total: number;
  items: Product[];
}

// Certification models (CU-007)
export interface Certification {
  idcertificacion: number;
  nombre: string;
  entidademisora?: string;
  descripcion?: string;
  logourl?: string;
}

export interface CertificationCreate {
  nombre: string;
  entidademisora?: string;
  descripcion?: string;
  logourl?: string;
}

export interface CertificationUpdate {
  nombre?: string;
  entidademisora?: string;
  descripcion?: string;
  logourl?: string;
}

export interface ProductCertificationAssign {
  idcertificacion: number;
  fechaobtencion?: string;
}

export interface ProductCertification {
  idproductocertificacion: number;
  idproducto: number;
  idcertificacion: number;
  fechaobtencion?: string;
  certificacion?: Certification;
}

// Tenant Catalog models (CU-008)
export interface TenantCatalogItem {
  idcatalogotenant: number;
  idtenant: number;
  idvariante: number;
  skuinterno?: string;
  precioventa: number;
  costopromedio?: number;
  activo: boolean;
  variante?: Variant;
}

export interface TenantCatalogCreate {
  idvariante: number;
  idtenant?: number;
  skuinterno?: string;
  precioventa: number;
  costopromedio?: number;
  activo?: boolean;
}

export interface TenantCatalogUpdate {
  skuinterno?: string;
  precioventa?: number;
  costopromedio?: number;
  activo?: boolean;
}

export interface TenantCatalogListResponse {
  total: number;
  items: TenantCatalogItem[];
}

export interface LoginRequest {
  tenant_slug: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ForgotPasswordRequest {
  tenant_slug: string;
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  confirm_password: string;
}

export interface MessageResponse {
  message: string;
}

// Actor models (CU-013)
export interface Actor {
  idactor: number;
  idtenant: number;
  nombre: string;
  razonsocial?: string;
  nit?: string;
  email?: string;
  telefono?: string;
  tipoactor: string;
}

export interface ActorCreate {
  nombre: string;
  razonsocial?: string;
  nit?: string;
  email?: string;
  telefono?: string;
  tipoactor: string;
}

export interface ActorListResponse {
  total: number;
  items: Actor[];
}

// Location models (CU-014)
export interface LocationItem {
  idubicacion: number;
  idtenant: number;
  idactor?: number;
  nombre: string;
  direccion?: string;
  latitud?: number;
  longitud?: number;
  ciudad?: string;
  pais?: string;
  tipo: string;
  actor?: Actor;
}

export interface LocationCreate {
  nombre: string;
  idactor?: number;
  direccion?: string;
  latitud?: number;
  longitud?: number;
  ciudad?: string;
  pais?: string;
  tipo: string;
}

export interface LocationListResponse {
  total: number;
  items: LocationItem[];
}

// Unit models (CU-015)
export interface UnitItem {
  idunidad: number;
  idtenant: number;
  idvariante: number;
  idrecepciondetalle?: number;
  numeroserie: string;
  imei1?: string;
  imei2?: string;
  eid?: string;
  uuidpublico: string;
  idcustodioactual?: number;
  idubicacionactual?: number;
  estado?: string;
  fechaingreso: string;
  fechaventa?: string;
  variante?: Variant;
  custodio?: Actor;
  ubicacion?: LocationItem;
}

export interface UnitCreate {
  idvariante: number;
  idrecepciondetalle?: number;
  numeroserie: string;
  imei1?: string;
  imei2?: string;
  eid?: string;
  idcustodioactual?: number;
  idubicacionactual?: number;
  estado?: string;
}

export interface UnitListResponse {
  total: number;
  items: UnitItem[];
}

