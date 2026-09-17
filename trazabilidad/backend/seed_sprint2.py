import sys
import os
import uuid
import hashlib
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu011_compras.purchase import Compra, CompraDetalle
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.models.cu021_eventos_transporte.shipment import (
    Envio,
    EnvioUnidad,
    EventoTrazabilidad,
    EventoUnidad,
    CondicionTransporte,
    Alerta
)


def seed_tenant_sprint2(db: Session, tenant: Tenant, variantes: list):
    print(f"\nProcesando tenant: {tenant.nombre} (ID: {tenant.idtenant})...")

    admin_user = db.execute(select(User).where(User.email == "admin@trazabilidad.com")).scalars().first()
    if not admin_user:
        admin_user = db.execute(select(User)).scalars().first()

    actores = db.execute(select(ActorCadena).where(ActorCadena.idtenant == tenant.idtenant)).scalars().all()
    if not actores:
        print(f"  Aviso: Tenant {tenant.idtenant} no tiene actores. Omitiendo.")
        return

    proveedor = next((a for a in actores if "PROVEEDOR" in str(a.tipoactor).upper()), actores[0])
    importador = next((a for a in actores if "IMPORTADOR" in str(a.tipoactor).upper()), actores[1] if len(actores) > 1 else proveedor)
    transportista = next((a for a in actores if "TRANSPORTISTA" in str(a.tipoactor).upper()), None)

    ubicacion = db.execute(select(Ubicacion).where(Ubicacion.idtenant == tenant.idtenant)).scalars().first()
    if not ubicacion:
        ubicacion = db.execute(select(Ubicacion)).scalars().first()

    unidades = db.execute(select(UnidadProducto).where(UnidadProducto.idtenant == tenant.idtenant)).scalars().all()

    # 1. CU-011: COMPRAS
    compras_existentes = db.execute(select(Compra).where(Compra.idtenant == tenant.idtenant)).scalars().all()
    for c in compras_existentes:
        detalles = db.execute(select(CompraDetalle).where(CompraDetalle.idcompra == c.idcompra)).scalars().all()
        if not detalles and variantes:
            db.add(CompraDetalle(
                idcompra=c.idcompra,
                idvariante=variantes[0].idvariante,
                cantidad=10,
                costounitariousd=Decimal("500.00"),
                subtotalusd=c.totalusd or Decimal("5000.00")
            ))

    if len(compras_existentes) < 2 and variantes:
        c1 = Compra(
            idtenant=tenant.idtenant,
            idproveedor=proveedor.idactor,
            numeroorden=f"PO-{tenant.idtenant}-APPLE-001",
            fechacompra=date.today() - timedelta(days=2),
            totalusd=Decimal("15000.00"),
            estado="pendiente"
        )
        c2 = Compra(
            idtenant=tenant.idtenant,
            idproveedor=proveedor.idactor,
            numeroorden=f"PO-{tenant.idtenant}-SAMSUNG-002",
            fechacompra=date.today() - timedelta(days=5),
            totalusd=Decimal("22000.00"),
            estado="enviada"
        )
        db.add_all([c1, c2])
        db.flush()

        v1 = variantes[0]
        v2 = variantes[1] if len(variantes) > 1 else v1
        db.add(CompraDetalle(idcompra=c1.idcompra, idvariante=v1.idvariante, cantidad=10, costounitariousd=Decimal("1500.00"), subtotalusd=Decimal("15000.00")))
        db.add(CompraDetalle(idcompra=c2.idcompra, idvariante=v2.idvariante, cantidad=20, costounitariousd=Decimal("1100.00"), subtotalusd=Decimal("22000.00")))
        print(f"  [CU-011] Compras creadas para tenant {tenant.idtenant}.")

    # 2. CU-016: CODIGOS QR
    if unidades:
        qrs_count = 0
        for u in unidades:
            qr_existente = db.execute(select(CodigoQR).where(CodigoQR.idunidad == u.idunidad)).scalars().first()
            if not qr_existente:
                token = str(uuid.uuid4())
                db.add(CodigoQR(
                    idunidad=u.idunidad,
                    tokenpublico=token,
                    url=f"http://localhost:4200/trace/{token}",
                    fechageneracion=datetime.now(timezone.utc).replace(tzinfo=None),
                    activo=True
                ))
                qrs_count += 1
        if qrs_count > 0:
            print(f"  [CU-016] {qrs_count} codigos QR generados para tenant {tenant.idtenant}.")

    # 3. CU-021: ENVIOS Y TRAZABILIDAD
    envios = db.execute(select(Envio).where(Envio.idtenant == tenant.idtenant)).scalars().all()
    if len(envios) == 0 and ubicacion and admin_user:
        e1 = Envio(
            idtenant=tenant.idtenant,
            idactororigen=proveedor.idactor,
            idactordestino=importador.idactor,
            idtransportista=transportista.idactor if transportista else None,
            codigoenvio=f"ENV-{tenant.idtenant}-001",
            fechasalida=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=3),
            fechaestimada=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=2),
            estado="en_transito",
            trackingexterno="DHL-TRACK-100"
        )
        e2 = Envio(
            idtenant=tenant.idtenant,
            idactororigen=proveedor.idactor,
            idactordestino=importador.idactor,
            idtransportista=transportista.idactor if transportista else None,
            codigoenvio=f"ENV-{tenant.idtenant}-002",
            fechasalida=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
            fechaestimada=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=4),
            estado="preparacion",
            trackingexterno="FEDEX-TRACK-200"
        )
        db.add_all([e1, e2])
        db.flush()

        if unidades:
            for idx, u in enumerate(unidades[:4]):
                db.add(EnvioUnidad(idenvio=e1.idenvio if idx < 2 else e2.idenvio, idunidad=u.idunidad))

        # Evento de trazabilidad
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        payload_str = f"{e1.idenvio}:transporte_aereo:{ubicacion.idubicacion}:{now.isoformat()}"
        p_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        ev = EventoTrazabilidad(
            idtenant=tenant.idtenant,
            tipoevento="transporte_aereo",
            fechahora=now,
            idactororigen=proveedor.idactor,
            idactordestino=importador.idactor,
            idubicacion=ubicacion.idubicacion,
            idusuarioresponsable=admin_user.idusuario,
            descripcion="Vuelo de carga internacional en ruta a destino",
            payloadhash=p_hash,
            estadoverificacion="verificado"
        )
        db.add(ev)
        db.flush()

        if unidades:
            db.add(EventoUnidad(idevento=ev.idevento, idunidad=unidades[0].idunidad))

        db.add(CondicionTransporte(
            idevento=ev.idevento,
            temperatura=Decimal("20.50"),
            humedad=Decimal("45.00"),
            presion=Decimal("1013.20"),
            nivelvibracion=Decimal("0.10"),
            fuentedatos="Sensor IoT BLE"
        ))

        db.add(Alerta(
            idtenant=tenant.idtenant,
            idunidad=unidades[0].idunidad if unidades else None,
            tipoalerta="temperatura",
            descripcion="Temperatura monitoreada dentro de limites optimos",
            gravedad="baja",
            fechadeteccion=now,
            estado="resuelta"
        ))

        print(f"  [CU-021] Envíos y trazabilidad creados para tenant {tenant.idtenant}.")

    db.commit()


def seed_sprint2():
    db: Session = SessionLocal()
    try:
        tenants = db.execute(select(Tenant).order_by(Tenant.idtenant)).scalars().all()
        variantes = db.execute(select(VarianteProducto)).scalars().all()
        print(f"Poblando datos de Sprint 2 para {len(tenants)} tenants...")

        for tenant in tenants:
            seed_tenant_sprint2(db, tenant, variantes)

        print("\n--- Todos los tenants quedaron poblados para CU-011, CU-016 y CU-021 ---")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sprint2()
