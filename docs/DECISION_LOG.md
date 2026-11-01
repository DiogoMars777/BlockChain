# Registro de Decisiones de Arquitectura (Architecture Decision Log)

> **Documento:** Registro Canónico de Decisiones Técnicas (ADR / Diátaxis Explicación)  
> **Ubicación:** `docs/DECISION_LOG.md`  
> **Audiencia:** Equipo de Ingeniería, Scrum Master, Arquitectos y Auditores  

Este documento registra cronológicamente las decisiones arquitectónicas fundamentales tomadas para la plataforma de trazabilidad de dispositivos Apple, detallando contexto, alternativas evaluadas y consecuencias.

---

## Índice de Decisiones (ADRs)

* [ADR-001: Estrategia de Aislamiento Multi-Tenant por Columna Discriminadora](#adr-001-estrategia-de-aislamiento-multi-tenant-por-columna-discriminadora)
* [ADR-002: Modelo Híbrido de Trazabilidad: Notarización On-Chain vs. Persistencia Off-Chain](#adr-002-modelo-híbrido-de-trazabilidad-notarización-on-chain-vs-persistencia-off-chain)
* [ADR-003: Organización en 7 Paquetes mediante Fachadas de Enrutamiento sin Rotura de APIs](#adr-003-organización-en-7-paquetes-mediante-fachadas-de-enrutamiento-sin-rotura-de-apis)
* [ADR-004: Aislamiento de Suite de Pruebas Automatizadas con Base de Datos Local Dedicada](#adr-004-aislamiento-de-suite-de-pruebas-automatizadas-con-base-de-datos-local-dedicada)
* [ADR-005: Bypass de Gobernanza y Auditoría para SuperAdministrador](#adr-005-bypass-de-gobernanza-y-auditoría-para-superadministrador)
* [ADR-006: Inclusión del Módulo SaaS (Planes y Suscripciones) en Paquete P1 durante Sprint 3](#adr-006-inclusión-del-módulo-saas-planes-y-suscripciones-en-paquete-p1-durante-sprint-3)
* [ADR-007: Motor Heurístico de Machine Learning Ligero Off-Chain para Sospecha de Fraude (CU-023)](#adr-007-motor-heurístico-de-machine-learning-ligero-off-chain-para-sospecha-de-fraude-cu-023)

---

### ADR-001: Estrategia de Aislamiento Multi-Tenant por Columna Discriminadora

* **Estado:** Aceptado
* **Fecha:** Sprint 0
* **Contexto:** La plataforma debe alojar múltiples empresas importadoras y distribuidoras en Bolivia de forma aislada. Se evaluaron tres enfoques: base de datos por tenant, esquema por tenant (PostgreSQL schemas) y base de datos compartida con discriminador `tenant_id`.
* **Decisión:** Implementar base de datos compartida con columna discriminadora `idtenant` / `tenant_id` en todas las tablas transaccionales, inyectada y validada obligatoriamente en cada endpoint de FastAPI mediante la dependencia `resolve_tenant_id`.
* **Consecuencias:**
  * *Positivas:* Menor costo de infraestructura, migraciones simples con Alembic y facilidad para consultas analíticas globales del SuperAdmin.
  * *Riesgos:* Toda consulta debe incluir `WHERE idtenant = :tenant_id`. Se mitiga forzando el filtrado a través de servicios y dependencias base.

---

### ADR-002: Modelo Híbrido de Trazabilidad: Notarización On-Chain vs. Persistencia Off-Chain

* **Estado:** Aceptado
* **Fecha:** Sprint 1 / Sprint 2
* **Contexto:** Registrar la totalidad de los datos (documentos, fotos, datos JSON de sensores) directamente en la red Ethereum generaría costos insostenibles de gas fees y problemas severos de escalabilidad y latencia.
* **Decisión:** Adoptar un modelo híbrido:
  1. **Off-Chain (PostgreSQL + Cloud Storage):** Almacena los registros operativos completos, archivos binarios (PDFs, facturas aduaneras) y metadatos de sensores.
  2. **On-Chain (Smart Contracts en Sepolia/Amoy):** Almacena únicamente el hash criptográfico SHA-256 de los datos, el identificador único del equipo (`unitId`), timestamp y la firma del operador.
* **Consecuencias:**
  * *Positivas:* Consumo mínimo de gas, transacciones instantáneas off-chain y garantía matemática de no alteración mediante verificación de hash.
  * *Trade-off:* Se requiere una tarea de sincronización/reconciliación entre la base relacional y la confirmación final de la transacción en la blockchain (estado "pendiente").

---

### ADR-003: Organización en 7 Paquetes mediante Fachadas de Enrutamiento sin Rotura de APIs

* **Estado:** Aceptado
* **Fecha:** Sprint 2 / Sprint 3
* **Contexto:** El backend creció con 26 carpetas individuales por Caso de Uso (`cu001` a `cu034`), generando más de 25 inclusiones de routers en `main.py`. Mover físicamente los archivos de inmediato rompería los tests unitarios y las rutas consumidas por Angular y Flutter.
* **Decisión:** Implementar un patrón de Módulos Profundos mediante empaquetado físico en `app/packages/` (P1 a P7) y fachadas `router.py`, manteniendo shims retrocompatibles en las rutas históricas de `app/controllers/`, `app/models/` y `app/views/`.
* **Consecuencias:**
  * *Positivas:* Rutas HTTP (`/api/v1/...`) 100% preservadas, cero roturas en los clientes frontend/móvil y preservación de la suite de pruebas.

---

### ADR-004: Aislamiento de Suite de Pruebas Automatizadas con Base de Datos Local Dedicada

* **Estado:** Aceptado
* **Fecha:** Sprint 2
* **Contexto:** Las pruebas de integración en pytest presentaban fallos aleatorios por colisión de IDs y mutación de estado compartido al ejecutarse sobre bases de datos en desarrollo.
* **Decisión:** Configurar un arnés de pruebas con una base de datos local dedicada PostgreSQL (`blacktest`), aislando los fixtures de sesión y ejecutando limpieza controlada tras cada suite.
* **Consecuencias:**
  * *Positivas:* 100% de reproducibilidad (167 tests pasando consecutivamente). Pruebas seguras sin riesgo de corromper datos de desarrollo.

---

### ADR-005: Bypass de Gobernanza y Auditoría para SuperAdministrador

* **Estado:** Aceptado
* **Fecha:** Sprint 2
* **Contexto:** El Super Administrador necesita supervisar, auditar e intervenir cualquier empresa sin requerir asignaciones manuales previas ni bloqueos por membresía rígida.
* **Decisión:** Otorgar bypass total de tenant en `require_roles` y `resolve_tenant_id` para el rol SuperAdministrador, registrando en `Bitacora` (CU-005) cada una de sus acciones de supervisión transversal.
* **Consecuencias:**
  * *Positivas:* Flexibilidad operativa total para el administrador global de la plataforma.
  * *Contramedida:* Trazabilidad obligatoria de auditoría en cada petición mediante el middleware HTTP.

---

### ADR-006: Inclusión del Módulo SaaS (Planes y Suscripciones) en Paquete P1 durante Sprint 3

* **Estado:** Aceptado
* **Fecha:** Sprint 3 (2026-11-01)
* **Contexto:** La plataforma requiere monetización multi-tenant y control de cuotas para las empresas clientes (límite de dispositivos trazados, almacenamiento, usuarios y días de prueba gratuita) según la guía rectora de CU-036 y CU-037.
* **Decisión:** Implementar `CU-036` (Planes de Suscripción) y `CU-037` (Suscripción de Empresa) dentro del Paquete P1 (Seguridad y Multi-Tenant) durante el Sprint 3, estableciendo un hook automático en `TenantController.create_tenant` que asigna inmediatamente un plan `trial` a toda empresa nueva. El control activo de límites duros se delega a Sprint 4 (`CU-040`).
* **Consecuencias:**
  * *Positivas:* Permite a las empresas clientes ver claramente sus cuotas de servicio y al SuperAdmin gestionar el catálogo SaaS sin alterar el alcance de ventas de Sprint 4.

---

### ADR-007: Motor Heurístico de Machine Learning Ligero Off-Chain para Sospecha de Fraude (CU-023)

* **Estado:** Aceptado
* **Fecha:** Sprint 3 (2026-11-01)
* **Contexto:** Las denuncias públicas de falsificación de dispositivos Apple requieren una evaluación objetiva preliminar para priorizar alertas y despachar verificaciones aduaneras o técnicas sin incurrir en costos de servicios externos de LLM ni latencia excesiva.
* **Decisión:** Implementar un servicio heurístico nativo de Machine Learning (`SuspicionMLService`) en Python, basado en TF-IDF simplificado, scoring ponderado de términos de fraude (`falso`, `clon`, `sellos rotos`, `caja china`) y normalización léxica en una escala de 0.0 a 1.0.
* **Consecuencias:**
  * *Positivas:* Sin dependencias pesadas de GPU ni llamadas a APIs de pago; tiempo de respuesta inferior a 5ms y persistencia del score en la tabla `reportesospecha`.
