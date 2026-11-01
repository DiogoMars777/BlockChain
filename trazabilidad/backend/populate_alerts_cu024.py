"""
Script para poblar datos enriquecidos y realistas de Alertas e Incidencias (CU-024)
para la plataforma Web y Móvil respetando el aislamiento multi-tenant.
"""
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.cu021_eventos_transporte.transport_event import Alerta
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu002_usuarios.user import User

def populate_alerts():
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Diccionario de alertas realistas para dispositivos Apple importados
        alerts_data = [
            # --- TENANT 1 (iStore Bolivia - Santa Cruz / La Paz) ---
            {
                "idtenant": 1,
                "unit_index": 0,
                "tipoalerta": "temperatura",
                "gravedad": "critica",
                "estado": "pendiente",
                "descripcion": "Sensor IoT #TR-402 detectó temperatura crítica de 39.4°C (máx tolerado 32.0°C) durante tramo Tambo Quemado - El Alto. Riesgo de degradación térmica de batería de iones de litio.",
                "days_ago": 1,
                "hours_ago": 4,
                "resolved": False,
            },
            {
                "idtenant": 1,
                "unit_index": 1,
                "tipoalerta": "humedad",
                "gravedad": "alta",
                "estado": "en_proceso",
                "descripcion": "Humedad relativa sostenida del 88% en contenedor logístico marítimo C-09 durante cruce aduanero. Riesgo de condensación interna en empaque original sellado.",
                "days_ago": 3,
                "hours_ago": 8,
                "resolved": False,
            },
            {
                "idtenant": 1,
                "unit_index": 2,
                "tipoalerta": "vibracion",
                "gravedad": "media",
                "estado": "resuelta",
                "descripcion": "Pico de impacto y aceleración anormal (4.8G) durante maniobra de estiba y descarga en depósito aduanero interior Santa Cruz.",
                "days_ago": 7,
                "hours_ago": 12,
                "resolved": True,
            },
            {
                "idtenant": 1,
                "unit_index": 3,
                "tipoalerta": "retraso_aduanero",
                "gravedad": "alta",
                "estado": "en_proceso",
                "descripcion": "Despacho arancelario y validación de póliza DIM demorada más de 96 horas en Aduana Nacional Interior Santa Cruz por inspección física diferida.",
                "days_ago": 2,
                "hours_ago": 6,
                "resolved": False,
            },
            {
                "idtenant": 1,
                "unit_index": 4,
                "tipoalerta": "fraude_autenticidad",
                "gravedad": "critica",
                "estado": "pendiente",
                "descripcion": "Intento de escaneo de QR público desde geolocalización incongruente fuera del corredor logístico habilitado antes de la recepción formal en sucursal.",
                "days_ago": 0,
                "hours_ago": 3,
                "resolved": False,
            },
            {
                "idtenant": 1,
                "unit_index": None,
                "tipoalerta": "inconsistencia_cadena",
                "gravedad": "alta",
                "estado": "pendiente",
                "descripcion": "Discrepancia de inventario físico vs manifiesto electrónico: el envío reporta 25 cajas máster pero se verificaron 24 en zona de recepción.",
                "days_ago": 1,
                "hours_ago": 10,
                "resolved": False,
            },
            {
                "idtenant": 1,
                "unit_index": 0,
                "tipoalerta": "vencimiento_garantia",
                "gravedad": "baja",
                "estado": "resuelta",
                "descripcion": "Alerta preventiva: Cobertura de garantía de fabricante Apple Care restante menor a 30 días respecto al lote de importación inicial.",
                "days_ago": 15,
                "hours_ago": 2,
                "resolved": True,
            },

            # --- TENANT 2 (TechImport SCZ) ---
            {
                "idtenant": 2,
                "unit_index": 0,
                "tipoalerta": "temperatura",
                "gravedad": "alta",
                "estado": "pendiente",
                "descripcion": "Exceso térmico persistente de 35.8°C registrado por sensor Bluetooth en transporte terrestre tramo Arica - La Paz.",
                "days_ago": 2,
                "hours_ago": 5,
                "resolved": False,
            },
            {
                "idtenant": 2,
                "unit_index": 1,
                "tipoalerta": "retraso_aduanero",
                "gravedad": "alta",
                "estado": "en_proceso",
                "descripcion": "Contenedor en canal rojo de aforo en Aduana Fronteriza Pisiga por discrepancia de partida arancelaria de accesorios y cables USB-C.",
                "days_ago": 4,
                "hours_ago": 9,
                "resolved": False,
            },
            {
                "idtenant": 2,
                "unit_index": 2,
                "tipoalerta": "vibracion",
                "gravedad": "critica",
                "estado": "pendiente",
                "descripcion": "Sensor de choque triaxial activado con aceleración de 6.2G por frenada intempestiva en carretera Oruro - Cochabamba.",
                "days_ago": 1,
                "hours_ago": 14,
                "resolved": False,
            },
            {
                "idtenant": 2,
                "unit_index": 3,
                "tipoalerta": "fraude_autenticidad",
                "gravedad": "alta",
                "estado": "resuelta",
                "descripcion": "Reporte de código QR con lectura ilegible o manipulada. Verificado por peritaje técnico y reetiquetado oficial con token firmado.",
                "days_ago": 8,
                "hours_ago": 16,
                "resolved": True,
            },
            {
                "idtenant": 2,
                "unit_index": None,
                "tipoalerta": "inconsistencia_cadena",
                "gravedad": "media",
                "estado": "en_proceso",
                "descripcion": "Falta de confirmación de recepción digital por transportista contratado tras entrega en Almacén Parque Industrial.",
                "days_ago": 3,
                "hours_ago": 1,
                "resolved": False,
            },

            # --- TENANT 3 (Andina Digital - La Paz / El Alto) ---
            {
                "idtenant": 3,
                "unit_index": 0,
                "tipoalerta": "temperatura",
                "gravedad": "media",
                "estado": "resuelta",
                "descripcion": "Temperatura mínima descendió a -2.1°C durante pernocte en zona altiplánica Patacamaya. Protocolo térmico aplicado.",
                "days_ago": 10,
                "hours_ago": 6,
                "resolved": True,
            },
            {
                "idtenant": 3,
                "unit_index": 1,
                "tipoalerta": "humedad",
                "gravedad": "baja",
                "estado": "resuelta",
                "descripcion": "Humedad ambiente en 76% controlada mediante gel desecante y empaque al vacío en furgón sellado.",
                "days_ago": 12,
                "hours_ago": 8,
                "resolved": True,
            },
            {
                "idtenant": 3,
                "unit_index": 2,
                "tipoalerta": "retraso_aduanero",
                "gravedad": "critica",
                "estado": "pendiente",
                "descripcion": "Retención en recinto aduanero por observación en el certificado de homologación ATT para frecuencias 5G de terminales iPhone 16 Pro.",
                "days_ago": 2,
                "hours_ago": 18,
                "resolved": False,
            },
            {
                "idtenant": 3,
                "unit_index": 3,
                "tipoalerta": "fraude_autenticidad",
                "gravedad": "critica",
                "estado": "en_proceso",
                "descripcion": "Alerta de duplicidad de número de serie: intento de registro paralelo en sistema externo con IMEI coincidente.",
                "days_ago": 1,
                "hours_ago": 7,
                "resolved": False,
            },
            {
                "idtenant": 3,
                "unit_index": 4,
                "tipoalerta": "inconsistencia_cadena",
                "gravedad": "alta",
                "estado": "pendiente",
                "descripcion": "Desvío de ruta GPS no autorizado detectado en vehículo de carga durante traslado entre Depósito Franco y Tienda Sopocachi.",
                "days_ago": 0,
                "hours_ago": 5,
                "resolved": False,
            },

            # --- TENANT 4 (ElectroSur Trading) ---
            {
                "idtenant": 4,
                "unit_index": 0,
                "tipoalerta": "vibracion",
                "gravedad": "alta",
                "estado": "pendiente",
                "descripcion": "Múltiples eventos de trepidación continua en camino de ripio hacia frontera sur Villazón. Inspección visual obligatoria.",
                "days_ago": 2,
                "hours_ago": 11,
                "resolved": False,
            },
            {
                "idtenant": 4,
                "unit_index": 1,
                "tipoalerta": "retraso_aduanero",
                "gravedad": "media",
                "estado": "resuelta",
                "descripcion": "Demora de 48h por mantenimiento de servidores del sistema aduanero SUMA. Flujo normalizado.",
                "days_ago": 9,
                "hours_ago": 4,
                "resolved": True,
            },
            {
                "idtenant": 4,
                "unit_index": 2,
                "tipoalerta": "temperatura",
                "gravedad": "critica",
                "estado": "en_proceso",
                "descripcion": "Cámara frigorífica / isotérmica de transporte apagada accidentalmente durante parada logística en Yacuiba (38.1°C).",
                "days_ago": 1,
                "hours_ago": 15,
                "resolved": False,
            },
            {
                "idtenant": 4,
                "unit_index": 3,
                "tipoalerta": "vencimiento_garantia",
                "gravedad": "media",
                "estado": "pendiente",
                "descripcion": "Dispositivo con activación de fábrica registrada hace más de 60 días antes del ingreso comercial al país.",
                "days_ago": 3,
                "hours_ago": 8,
                "resolved": False,
            },

            # --- TENANT 5 (Cochabamba Wireless) ---
            {
                "idtenant": 5,
                "unit_index": 0,
                "tipoalerta": "temperatura",
                "gravedad": "alta",
                "estado": "pendiente",
                "descripcion": "Sensor termográfico reporta 36.5°C constante en zona de carga durante trayecto por El Chapare.",
                "days_ago": 1,
                "hours_ago": 8,
                "resolved": False,
            },
            {
                "idtenant": 5,
                "unit_index": 1,
                "tipoalerta": "vibracion",
                "gravedad": "media",
                "estado": "en_proceso",
                "descripcion": "Vibración acumulada por bacheo en carretera nueva Cochabamba - Santa Cruz. Empaque secundario intacto.",
                "days_ago": 3,
                "hours_ago": 13,
                "resolved": False,
            },
            {
                "idtenant": 5,
                "unit_index": 2,
                "tipoalerta": "fraude_autenticidad",
                "gravedad": "critica",
                "estado": "pendiente",
                "descripcion": "Etiqueta física con signos de vulneración en precinto holográfico detectada en control de calidad interno.",
                "days_ago": 0,
                "hours_ago": 2,
                "resolved": False,
            },
            {
                "idtenant": 5,
                "unit_index": 3,
                "tipoalerta": "retraso_aduanero",
                "gravedad": "alta",
                "estado": "resuelta",
                "descripcion": "Retraso logístico superado tras aclaración de número de factura comercial electrónica con proveedor en Miami.",
                "days_ago": 6,
                "hours_ago": 10,
                "resolved": True,
            },
            {
                "idtenant": 5,
                "unit_index": None,
                "tipoalerta": "inconsistencia_cadena",
                "gravedad": "alta",
                "estado": "en_proceso",
                "descripcion": "Código de lote no coincide con el orden cronológico del manifiesto de carga aérea.",
                "days_ago": 2,
                "hours_ago": 19,
                "resolved": False,
            },
        ]

        # Obtener un usuario de referencia para resoluciones
        admin_user = db.query(User).filter(User.idusuario == 1).first()
        admin_id = admin_user.idusuario if admin_user else None

        # Obtener unidades para cada tenant
        units_by_tenant = {}
        for t in range(1, 6):
            units = db.query(UnidadProducto).filter(UnidadProducto.idtenant == t).all()
            units_by_tenant[t] = units

        nuevas_creadas = 0
        for item in alerts_data:
            t = item["idtenant"]
            units = units_by_tenant.get(t, [])
            idunidad = None
            if item["unit_index"] is not None and len(units) > item["unit_index"]:
                idunidad = units[item["unit_index"]].idunidad

            # Verificar si ya existe una alerta con descripción idéntica para evitar duplicados
            existe = db.query(Alerta).filter(
                Alerta.idtenant == t,
                Alerta.descripcion == item["descripcion"]
            ).first()

            if existe:
                continue

            detection_time = now - timedelta(days=item["days_ago"], hours=item["hours_ago"])
            resolution_time = (detection_time + timedelta(hours=14)) if item["resolved"] else None
            resolutor_id = admin_id if item["resolved"] else None

            nueva_alerta = Alerta(
                idtenant=t,
                idunidad=idunidad,
                idevento=None,
                tipoalerta=item["tipoalerta"],
                descripcion=item["descripcion"],
                gravedad=item["gravedad"],
                fechadeteccion=detection_time,
                fecharesolucion=resolution_time,
                estado=item["estado"],
                idusuarioresolutor=resolutor_id
            )
            db.add(nueva_alerta)
            nuevas_creadas += 1

        db.commit()
        print(f"Éxito: Se crearon {nuevas_creadas} nuevas alertas e incidencias para los tenants 1 a 5.")
        print(f"Total alertas en base de datos: {db.query(Alerta).count()}")
    except Exception as e:
        db.rollback()
        print(f"Error poblando alertas: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_alerts()

