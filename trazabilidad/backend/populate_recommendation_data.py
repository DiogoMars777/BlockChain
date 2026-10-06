"""
Script para poblar datos de prueba de Recomendaciones de IA (CU-008 + IA).
Crea escenarios realistas que activan todas las reglas de pricing e inventario:
1. MARGEN_NEGATIVO (crítica): Precio de venta inferior al costo promedio.
2. SUBIR_PRECIO (alta): Alta rotación mensual (>0.6) con margen bruto bajo (<15%).
3. REPOSICION_URGENTE (alta): Rotación alta (>0.8) con stock disponible crítico (<=2).
4. RIESGO_DEVOLUCION (alta): Alto porcentaje de unidades devueltas (>=20%).
5. BAJAR_PRECIO (media): Margen excesivo (>45%) sin ventas en 90 días y stock disponible.
6. SOBRESTOCK (media): Stock alto (>=2) sin rotación en 90 días.
7. BRECHA_DEMANDA (media): Pedidos en orden de compra superan ventas con rotación baja.
"""

import os
import sys
import uuid
import hashlib
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Bolivia UTC-4
BOLIVIA_TZ = timezone(timedelta(hours=-4))

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu008_catalogo_empresa.tenant_catalog import CatalogoTenant
from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu012_recepciones.reception import RecepcionCompra, RecepcionDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.services.ai.pricing_recommender import build_pricing_recommendations


def get_now_bolivia() -> datetime:
    return datetime.now(BOLIVIA_TZ).replace(tzinfo=None)


def populate_ai_recommendations(db: Session, target_tenant_ids=None):
    if target_tenant_ids is None:
        tenants = db.query(Tenant).all()
    else:
        tenants = db.query(Tenant).filter(Tenant.idtenant.in_(target_tenant_ids)).all()

    print(f"Poblando datos de recomendaciones IA para {len(tenants)} empresas...")

    FACTORY_PREFIXES = ["F17", "DNP", "G6T", "C39", "F2L", "DX3", "H02", "J8K", "M03", "K4L"]
    APPLE_TACS = ["35294111", "35849210", "35981208", "35401923", "35182944"]

    # Mapa de variantes Apple oficiales
    # 398: IP16PM-256-DES, 402: IP16P-256-NAT, 403: IP16P-128-NEG, 404: IP16-128-AZU,
    # 410: IP15P-256-BLA, 413: IP15-128-NEG, 414: APP2-USBC-BLA, 415: AP20W-USB-BLA
    SKU_SCENARIOS = {
        "IP16PM-256-DES": {
            "regla": "MARGEN_NEGATIVO",
            "costo": Decimal("1299.00"),
            "precio": Decimal("1199.00"),  # Pérdida directa (-8.34%)
            "vendidas": 3,
            "dias_venta_atras": 10,
            "disponibles": 2,
            "devueltas": 0,
            "pedidas": 5,
            "recibidas": 5,
        },
        "IP15-128-NEG": {
            "regla": "SUBIR_PRECIO",
            "costo": Decimal("799.00"),
            "precio": Decimal("869.00"),  # Margen 8.05% (< 15%)
            "vendidas": 8,
            "dias_venta_atras": 5,
            "disponibles": 4,  # > 2 para no chocar con reposición urgente
            "devueltas": 0,
            "pedidas": 12,
            "recibidas": 12,
        },
        "APP2-USBC-BLA": {
            "regla": "REPOSICION_URGENTE",
            "costo": Decimal("199.00"),
            "precio": Decimal("249.00"),  # Margen 20.08%
            "vendidas": 9,
            "dias_venta_atras": 3,
            "disponibles": 1,  # Stock crítico <= 2
            "devueltas": 0,
            "pedidas": 10,
            "recibidas": 10,
        },
        "IP16-128-AZU": {
            "regla": "RIESGO_DEVOLUCION",
            "costo": Decimal("749.00"),
            "precio": Decimal("899.00"),  # Margen 16.68%
            "vendidas": 5,
            "dias_venta_atras": 45,
            "disponibles": 3,
            "devueltas": 2,  # 40% devueltas (>= 20%)
            "pedidas": 10,
            "recibidas": 10,
        },
        "IP15P-256-BLA": {
            "regla": "BAJAR_PRECIO",
            "costo": Decimal("750.00"),
            "precio": Decimal("1499.00"),  # Margen 49.97% (> 45%)
            "vendidas": 0,
            "dias_venta_atras": None,
            "disponibles": 1,  # 1 disponible (> 0 y < 2 para aislar de sobrestock)
            "devueltas": 0,
            "pedidas": 1,
            "recibidas": 1,
        },
        "AP20W-USB-BLA": {
            "regla": "SOBRESTOCK",
            "costo": Decimal("22.00"),
            "precio": Decimal("29.00"),  # Margen normal 24.14% (< 45%)
            "vendidas": 0,
            "dias_venta_atras": None,
            "disponibles": 7,  # Stock inmovilizado >= 2
            "devueltas": 0,
            "pedidas": 7,
            "recibidas": 7,
        },
        "IP16P-128-NEG": {
            "regla": "BRECHA_DEMANDA",
            "costo": Decimal("920.00"),
            "precio": Decimal("1120.00"),  # Margen normal 17.86%
            "vendidas": 2,
            "dias_venta_atras": 75,  # rotación 2 / 75 * 30 = 0.8 < 1.0
            "disponibles": 5,
            "devueltas": 0,
            "pedidas": 15,  # brecha = 15 - 2 = 13 > 0
            "recibidas": 15,
        },
        "IP16P-256-NAT": {
            "regla": "SUBIR_PRECIO + REPOSICION",
            "costo": Decimal("990.00"),
            "precio": Decimal("1099.00"),  # Margen 9.92% (< 15%)
            "vendidas": 11,
            "dias_venta_atras": 4,  # rotación alta 11.0 >= 0.8
            "disponibles": 1,  # stock crítico <= 2
            "devueltas": 0,
            "pedidas": 12,
            "recibidas": 12,
        },
    }

    now_base = get_now_bolivia()

    for tenant in tenants:
        tid = tenant.idtenant
        print(f"\n--- Procesando Tenant {tid}: {tenant.nombre} ---")

        # Actores y ubicaciones del tenant
        proveedor = db.query(ActorCadena).filter(
            ActorCadena.idtenant == tid,
            ActorCadena.tipoactor.in_(["PROVEEDOR_EEUU", "DISTRIBUIDOR"])
        ).first()
        importador = db.query(ActorCadena).filter(
            ActorCadena.idtenant == tid,
            ActorCadena.tipoactor == "IMPORTADOR"
        ).first()
        tienda_actor = db.query(ActorCadena).filter(
            ActorCadena.idtenant == tid,
            ActorCadena.tipoactor == "TIENDA"
        ).first() or importador

        almacen_loc = db.query(Ubicacion).filter(
            Ubicacion.idtenant == tid,
            Ubicacion.tipo.in_(["centro_distribucion", "almacen"])
        ).first()
        tienda_loc = db.query(Ubicacion).filter(
            Ubicacion.idtenant == tid,
            Ubicacion.tipo == "punto_venta"
        ).first() or almacen_loc

        # Buscar o crear Orden de Compra oficial de abastecimiento
        num_orden = f"OC-2026-SCZ-{tid:02d}"
        compra = db.query(Compra).filter(
            Compra.idtenant == tid,
            Compra.numeroorden == num_orden
        ).first()
        if not compra:
            compra = Compra(
                idtenant=tid,
                idproveedor=proveedor.idactor if proveedor else 1,
                numeroorden=num_orden,
                fechacompra=now_base.date() - timedelta(days=20),
                totalusd=Decimal("50000.00"),
                estado="recibida_total"
            )
            db.add(compra)
            db.flush()

        # Buscar o crear Recepción física correspondiente
        num_rec = f"REC-2026-SCZ-{tid:02d}"
        recepcion = db.query(RecepcionCompra).filter(
            RecepcionCompra.idcompra == compra.idcompra
        ).first()
        if not recepcion:
            recepcion = RecepcionCompra(
                idcompra=compra.idcompra,
                idubicacion=almacen_loc.idubicacion if almacen_loc else 1,
                fecharecepcion=now_base - timedelta(days=15),
                numerodocumento=num_rec,
                estado="completa"
            )
            db.add(recepcion)
            db.flush()

        # Configurar cada escenario
        for sku, config in SKU_SCENARIOS.items():
            variante = db.query(VarianteProducto).filter(VarianteProducto.sku == sku).first()
            if not variante:
                print(f"  [AVISO] Variante {sku} no encontrada, omitiendo...")
                continue

            vid = variante.idvariante

            # 1. Actualizar o crear CatalogoTenant
            cat_item = db.query(CatalogoTenant).filter(
                CatalogoTenant.idtenant == tid,
                CatalogoTenant.idvariante == vid
            ).first()
            if not cat_item:
                cat_item = CatalogoTenant(
                    idtenant=tid,
                    idvariante=vid,
                    skuinterno=f"{tenant.nit[:4]}-{sku}",
                    costopromedio=config["costo"],
                    precioventa=config["precio"],
                    activo=True
                )
                db.add(cat_item)
            else:
                cat_item.costopromedio = config["costo"]
                cat_item.precioventa = config["precio"]
                cat_item.activo = True
            db.flush()

            # 2. Actualizar o crear CompraDetalle
            cd = db.query(CompraDetalle).filter(
                CompraDetalle.idcompra == compra.idcompra,
                CompraDetalle.idvariante == vid
            ).first()
            if not cd:
                cd = CompraDetalle(
                    idcompra=compra.idcompra,
                    idvariante=vid,
                    cantidad=config["pedidas"],
                    costounitariousd=config["costo"],
                    subtotalusd=(config["costo"] * config["pedidas"]).quantize(Decimal("0.01"))
                )
                db.add(cd)
            else:
                cd.cantidad = config["pedidas"]
                cd.costounitariousd = config["costo"]
                cd.subtotalusd = (config["costo"] * config["pedidas"]).quantize(Decimal("0.01"))
            db.flush()

            # 3. Actualizar o crear RecepcionDetalle
            rd = db.query(RecepcionDetalle).filter(
                RecepcionDetalle.idrecepcion == recepcion.idrecepcion,
                RecepcionDetalle.idvariante == vid
            ).first()
            if not rd:
                rd = RecepcionDetalle(
                    idrecepcion=recepcion.idrecepcion,
                    idvariante=vid,
                    cantidadesperada=config["pedidas"],
                    cantidadrecibida=config["recibidas"]
                )
                db.add(rd)
            else:
                rd.cantidadesperada = config["pedidas"]
                rd.cantidadrecibida = config["recibidas"]
            db.flush()

            # 4. Sincronizar Unidades de este SKU
            # Limpiar unidades de prueba previas específicas de este SKU para este tenant que no estén en envíos
            unidades_actuales = db.query(UnidadProducto).filter(
                UnidadProducto.idtenant == tid,
                UnidadProducto.idvariante == vid
            ).all()

            # Contar estados requeridos
            vendidas_req = config["vendidas"]
            disponibles_req = config["disponibles"]
            devueltas_req = config["devueltas"]

            # Si ya hay unidades, ajustar las existentes o crear adicionales
            u_vendidas = [u for u in unidades_actuales if u.estado == "vendido"]
            u_disponibles = [u for u in unidades_actuales if u.estado == "disponible"]
            u_devueltas = [u for u in unidades_actuales if u.estado == "devuelto"]

            # Unidades vendidas requeridas
            for i in range(vendidas_req):
                dias_atras = config["dias_venta_atras"] or 10
                fechaventa = now_base - timedelta(days=dias_atras, hours=i * 2)
                fechaingreso = fechaventa - timedelta(days=15)
                if i < len(u_vendidas):
                    unit = u_vendidas[i]
                    unit.fechaventa = fechaventa
                    unit.fechaingreso = fechaingreso
                else:
                    prefix = random.choice(FACTORY_PREFIXES)
                    rand_alnum = "".join(random.choices("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ", k=7))
                    serie = f"{prefix}{tid}V{vid % 100:02d}{rand_alnum}"
                    tac = random.choice(APPLE_TACS)
                    rand_num = "".join(random.choices("0123456789", k=6))
                    imei1 = f"{tac}{rand_num}{i % 10}"
                    imei2 = f"35{tac[2:]}{rand_num}{(i + 1) % 10}"
                    eid = f"89049032{tid:02d}" + "".join(random.choices("0123456789ABCDEF", k=22))

                    unit = UnidadProducto(
                        idtenant=tid,
                        idvariante=vid,
                        idrecepciondetalle=rd.idrecepciondetalle,
                        numeroserie=serie,
                        imei1=imei1,
                        imei2=imei2,
                        eid=eid,
                        uuidpublico=str(uuid.uuid4()),
                        idcustodioactual=tienda_actor.idactor if tienda_actor else None,
                        idubicacionactual=tienda_loc.idubicacion if tienda_loc else None,
                        estado="vendido",
                        fechaingreso=fechaingreso,
                        fechaventa=fechaventa
                    )
                    db.add(unit)
                    db.flush()

                    token_qr = hashlib.sha256(f"{unit.numeroserie}-{unit.uuidpublico}".encode()).hexdigest()[:32]
                    url_qr = f"https://blockchain-production-8de2.up.railway.app/trace/{unit.uuidpublico}"
                    db.add(CodigoQR(
                        idunidad=unit.idunidad,
                        tokenpublico=token_qr,
                        url=url_qr,
                        fechageneracion=fechaingreso,
                        activo=True
                    ))

            # Unidades devueltas requeridas
            for i in range(devueltas_req):
                dias_atras = (config["dias_venta_atras"] or 30) - 5
                fechaventa = now_base - timedelta(days=dias_atras, hours=i * 2)
                fechaingreso = fechaventa - timedelta(days=15)
                if i < len(u_devueltas):
                    unit = u_devueltas[i]
                    unit.fechaventa = fechaventa
                    unit.fechaingreso = fechaingreso
                else:
                    prefix = random.choice(FACTORY_PREFIXES)
                    rand_alnum = "".join(random.choices("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ", k=7))
                    serie = f"{prefix}{tid}D{vid % 100:02d}{rand_alnum}"
                    tac = random.choice(APPLE_TACS)
                    rand_num = "".join(random.choices("0123456789", k=6))
                    imei1 = f"{tac}{rand_num}{i % 10}"
                    imei2 = f"35{tac[2:]}{rand_num}{(i + 1) % 10}"
                    eid = f"89049032{tid:02d}" + "".join(random.choices("0123456789ABCDEF", k=22))

                    unit = UnidadProducto(
                        idtenant=tid,
                        idvariante=vid,
                        idrecepciondetalle=rd.idrecepciondetalle,
                        numeroserie=serie,
                        imei1=imei1,
                        imei2=imei2,
                        eid=eid,
                        uuidpublico=str(uuid.uuid4()),
                        idcustodioactual=tienda_actor.idactor if tienda_actor else None,
                        idubicacionactual=tienda_loc.idubicacion if tienda_loc else None,
                        estado="devuelto",
                        fechaingreso=fechaingreso,
                        fechaventa=fechaventa
                    )
                    db.add(unit)
                    db.flush()

                    token_qr = hashlib.sha256(f"{unit.numeroserie}-{unit.uuidpublico}".encode()).hexdigest()[:32]
                    url_qr = f"https://blockchain-production-8de2.up.railway.app/trace/{unit.uuidpublico}"
                    db.add(CodigoQR(
                        idunidad=unit.idunidad,
                        tokenpublico=token_qr,
                        url=url_qr,
                        fechageneracion=fechaingreso,
                        activo=True
                    ))

            # Unidades disponibles requeridas
            for i in range(disponibles_req):
                fechaingreso = now_base - timedelta(days=random.randint(15, 30))
                if i < len(u_disponibles):
                    unit = u_disponibles[i]
                    unit.fechaventa = None
                    unit.fechaingreso = fechaingreso
                else:
                    prefix = random.choice(FACTORY_PREFIXES)
                    rand_alnum = "".join(random.choices("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ", k=7))
                    serie = f"{prefix}{tid}S{vid % 100:02d}{rand_alnum}"
                    tac = random.choice(APPLE_TACS)
                    rand_num = "".join(random.choices("0123456789", k=6))
                    imei1 = f"{tac}{rand_num}{i % 10}"
                    imei2 = f"35{tac[2:]}{rand_num}{(i + 1) % 10}"
                    eid = f"89049032{tid:02d}" + "".join(random.choices("0123456789ABCDEF", k=22))

                    unit = UnidadProducto(
                        idtenant=tid,
                        idvariante=vid,
                        idrecepciondetalle=rd.idrecepciondetalle,
                        numeroserie=serie,
                        imei1=imei1,
                        imei2=imei2,
                        eid=eid,
                        uuidpublico=str(uuid.uuid4()),
                        idcustodioactual=importador.idactor if importador else None,
                        idubicacionactual=almacen_loc.idubicacion if almacen_loc else None,
                        estado="disponible",
                        fechaingreso=fechaingreso,
                        fechaventa=None
                    )
                    db.add(unit)
                    db.flush()

                    token_qr = hashlib.sha256(f"{unit.numeroserie}-{unit.uuidpublico}".encode()).hexdigest()[:32]
                    url_qr = f"https://blockchain-production-8de2.up.railway.app/trace/{unit.uuidpublico}"
                    db.add(CodigoQR(
                        idunidad=unit.idunidad,
                        tokenpublico=token_qr,
                        url=url_qr,
                        fechageneracion=fechaingreso,
                        activo=True
                    ))

            print(f"  ✓ {sku} ({config['regla']}): "
                  f"Vendidas={vendidas_req}, Disp={disponibles_req}, Dev={devueltas_req}, "
                  f"Costo=${config['costo']}, Precio=${config['precio']}")

        db.commit()

        # Resincronizar secuencias
        for tabla, col_pk in [("unidadproducto", "idunidad"), ("codigoqr", "idcodigoqr"), ("recepciondetalle", "idrecepciondetalle"), ("compradetalle", "idcompradetalle")]:
            try:
                db.execute(text(f"""
                    SELECT setval(
                        pg_get_serial_sequence('{tabla}', '{col_pk}'),
                        coalesce((SELECT MAX({col_pk}) FROM {tabla}), 1)
                    );
                """))
            except Exception:
                pass
        db.commit()

        # Validar recomendaciones para este tenant
        resultado = build_pricing_recommendations(db, tenant_id=tid, top_n=20)
        recs = resultado["recomendaciones"]
        print(f"\n[RESULTADO IA TENANT {tid}]: {resultado['total_recomendaciones']} recomendaciones encontradas:")
        for r in recs:
            print(f"   [{r['prioridad'].upper():<7}] {r['tipo']:<20} | {r['titulo']}")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        populate_ai_recommendations(db)
        print("\n¡Poblado de recomendaciones IA finalizado exitosamente!")
    except Exception as e:
        db.rollback()
        print(f"Error en script de recomendaciones: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
