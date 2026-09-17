import sys
import os
import uuid
import hashlib
from datetime import date, datetime, timedelta
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


def seed_sprint2():
    db: Session = SessionLocal()
    try:
        print("--- Poblador de datos para CU-011, CU-016 y CU-021 ---")

        # 1. Obtener tenant principal y actores
        tenant = db.execute(select(Tenant).order_by(Tenant.idtenant)).scalars().first()
        if not tenant:
            print("Error: No se encontro ningun tenant.")
            return

        print(f"Tenant activo: {tenant.nombre} (ID: {tenant.idtenant})")

        admin_user = db.execute(select(User).where(User.email == "admin@trazabilidad.com")).scalars().first()
        if not admin_user:
            admin_user = db.execute(select(User)).scalars().first()

        actores = db.execute(select(ActorCadena).where(ActorCadena.idtenant == tenant.idtenant)).scalars().all()
        proveedor = next((a for a in actores if "PROVEEDOR" in str(a.tipoactor).upper()), actores[0] if actores else None)
        importador = next((a for a in actores if "IMPORTADOR" in str(a.tipoactor).upper()), actores[1] if len(actores) > 1 else proveedor)
        transportista = next((a for a in actores if "TRANSPORTISTA" in str(a.tipoactor).upper()), None)

        ubicacion = db.execute(select(Ubicacion).where(Ubicacion.idtenant == tenant.idtenant)).scalars().first()
        variantes = db.execute(select(VarianteProducto)).scalars().all()
        unidades = db.execute(select(UnidadProducto).where(UnidadProducto.idtenant == tenant.idtenant)).scalars().all()

        # ==========================================
        # CU-011: COMPRAS Y DETALLES
        # ==========================================
        print("\n[CU-011] Verificando compras...")
        compras_existentes = db.execute(select(Compra).where(Compra.idtenant == tenant.idtenant)).scalars().all()

        # Si existe compra sin detalles, agregamos detalles
        for c in compras_existentes:
            detalles_existentes = db.execute(
                select(CompraDetalle).where(CompraDetalle.idcompra == c.idcompra)
            ).scalars().all()
            if not detalles_existentes and variantes:
                v = variantes[0]
                db.add(CompraDetalle(
                    idcompra=c.idcompra,
                    idvariante=v.idvariante,
                    cantidad=25,
                    costounitariousd=Decimal("1000.00"),
                    subtotalusd=c.totalusd or Decimal("25000.00")
                ))
                print(f"  Detalle agregado a compra existente ID {c.idcompra}.")

        # Crear compras con estado 'pendiente' y 'enviada' para probar aprobación/rechazo
        if len(compras_existentes) < 3 and proveedor and variantes:
            if not any(c.numeroorden == "PO-2026-APPLE-002" for c in compras_existentes):
                c_pendiente = Compra(
                    idtenant=tenant.idtenant,
                    idproveedor=proveedor.idactor,
                    numeroorden="PO-2026-APPLE-002",
                    fechacompra=date.today() - timedelta(days=2),
                    totalusd=Decimal("18990.00"),
                    estado="pendiente"
                )
                db.add(c_pendiente)
                db.flush()

                v1 = variantes[0]
                v2 = variantes[1] if len(variantes) > 1 else v1
                db.add(CompraDetalle(
                    idcompra=c_pendiente.idcompra,
                    idvariante=v1.idvariante,
                    cantidad=10,
                    costounitariousd=Decimal("1099.00"),
                    subtotalusd=Decimal("10990.00")
                ))
                db.add(CompraDetalle(
                    idcompra=c_pendiente.idcompra,
                    idvariante=v2.idvariante,
                    cantidad=10,
                    costounitariousd=Decimal("800.00"),
                    subtotalusd=Decimal("8000.00")
                ))
                print("  Compra 'PO-2026-APPLE-002' (Pendiente) creada.")

            if not any(c.numeroorden == "PO-2026-SAMSUNG-003" for c in compras_existentes):
                c_enviada = Compra(
                    idtenant=tenant.idtenant,
                    idproveedor=proveedor.idactor,
                    numeroorden="PO-2026-SAMSUNG-003",
                    fechacompra=date.today() - timedelta(days=5),
                    totalusd=Decimal("12500.00"),
                    estado="enviada"
                )
                db.add(c_enviada)
                db.flush()

                v_last = variantes[-1]
                db.add(CompraDetalle(
                    idcompra=c_enviada.idcompra,
                    idvariante=v_last.idvariante,
                    cantidad=15,
                    costounitariousd=Decimal("833.33"),
                    subtotalusd=Decimal("12500.00")
                ))
                print("  Compra 'PO-2026-SAMSUNG-003' (Enviada) creada.")

        db.commit()

        # ==========================================
        # CU-016: CÓDIGOS QR
        # ==========================================
        print("\n[CU-016] Verificando códigos QR...")
        qrs_existentes = db.execute(select(CodigoQR)).scalars().all()
        if len(qrs_existentes) == 0 and unidades:
            for u in unidades[:10]:
                token = str(uuid.uuid4())
                trace_url = f"http://localhost:4200/trace/{token}"
                qr = CodigoQR(
                    idunidad=u.idunidad,
                    tokenpublico=token,
                    url=trace_url,
                    fechageneracion=datetime.utcnow() - timedelta(days=3),
                    activo=True
                )
                db.add(qr)
            db.commit()
            print(f"  {min(len(unidades), 10)} codigos QR generados y asociados a unidades.")
        else:
            print(f"  Ya existen {len(qrs_existentes)} codigos QR.")

        # ==========================================
        # CU-021: ENVÍOS, EVENTOS Y CONDICIONES
        # ==========================================
        print("\n[CU-021] Verificando envios y trazabilidad...")
        envios_existentes = db.execute(select(Envio).where(Envio.idtenant == tenant.idtenant)).scalars().all()
        if len(envios_existentes) == 0 and proveedor and importador and ubicacion and admin_user:
            # Envio 1: En transito
            envio1 = Envio(
                idtenant=tenant.idtenant,
                idactororigen=proveedor.idactor,
                idactordestino=importador.idactor,
                idtransportista=transportista.idactor if transportista else None,
                codigoenvio="ENV-BO-2026-001",
                fechasalida=datetime.utcnow() - timedelta(days=4),
                fechaestimada=datetime.utcnow() + timedelta(days=2),
                estado="en_transito",
                trackingexterno="DHL-BO-992233"
            )
            # Envio 2: En preparacion
            envio2 = Envio(
                idtenant=tenant.idtenant,
                idactororigen=proveedor.idactor,
                idactordestino=importador.idactor,
                idtransportista=transportista.idactor if transportista else None,
                codigoenvio="ENV-BO-2026-002",
                fechasalida=datetime.utcnow() - timedelta(days=1),
                fechaestimada=datetime.utcnow() + timedelta(days=5),
                estado="preparacion",
                trackingexterno="FEDEX-BO-441100"
            )
            # Envio 3: Entregado
            envio3 = Envio(
                idtenant=tenant.idtenant,
                idactororigen=proveedor.idactor,
                idactordestino=importador.idactor,
                idtransportista=transportista.idactor if transportista else None,
                codigoenvio="ENV-BO-2026-003",
                fechasalida=datetime.utcnow() - timedelta(days=10),
                fechaestimada=datetime.utcnow() - timedelta(days=2),
                fechaentrega=datetime.utcnow() - timedelta(days=2),
                estado="entregado",
                trackingexterno="DHL-BO-771199"
            )
            db.add_all([envio1, envio2, envio3])
            db.flush()

            # Vincular unidades a los envios
            if unidades:
                for idx, u in enumerate(unidades[:6]):
                    e = envio1 if idx < 3 else envio2
                    db.add(EnvioUnidad(idenvio=e.idenvio, idunidad=u.idunidad))

            # Crear Eventos de trazabilidad para envio1
            now = datetime.utcnow()
            eventos_data = [
                ("exportacion", now - timedelta(days=4), "Carga despachada desde origen"),
                ("transporte_aereo", now - timedelta(days=3), "Vuelo de carga internacional en ruta"),
                ("llegada_puerto", now - timedelta(days=2), "Arribo al aeropuerto internacional Viru Viru"),
                ("despacho_aduanero", now - timedelta(days=1), "Inspeccion y desaduanizacion en proceso")
            ]

            for tipo, f_hora, desc in eventos_data:
                payload_str = f"{envio1.idenvio}:{tipo}:{ubicacion.idubicacion}:{f_hora.isoformat()}"
                p_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

                ev = EventoTrazabilidad(
                    idtenant=tenant.idtenant,
                    tipoevento=tipo,
                    fechahora=f_hora,
                    idactororigen=proveedor.idactor,
                    idactordestino=importador.idactor,
                    idubicacion=ubicacion.idubicacion,
                    idusuarioresponsable=admin_user.idusuario,
                    descripcion=desc,
                    payloadhash=p_hash,
                    estadoverificacion="verificado"
                )
                db.add(ev)
                db.flush()

                # Vincular unidad al evento
                if unidades:
                    db.add(EventoUnidad(idevento=ev.idevento, idunidad=unidades[0].idunidad))

                # Condición de transporte IoT
                db.add(CondicionTransporte(
                    idevento=ev.idevento,
                    temperatura=Decimal("21.50"),
                    humedad=Decimal("48.00"),
                    presion=Decimal("1013.25"),
                    nivelvibracion=Decimal("0.15"),
                    fuentedatos="Sensor IoT BLE-300"
                ))

            # Crear una alerta preventiva
            db.add(Alerta(
                idtenant=tenant.idtenant,
                idunidad=unidades[0].idunidad if unidades else None,
                tipoalerta="humedad",
                descripcion="Humedad relativa en bodega alcanzo 62% (limite recomendado: 60%)",
                gravedad="media",
                fechadeteccion=now - timedelta(hours=12),
                estado="pendiente"
            ))

            db.commit()
            print("  Envios ENV-BO-2026-001, ENV-BO-2026-002, ENV-BO-2026-003 y trazabilidad creados.")
        else:
            print(f"  Ya existen {len(envios_existentes)} envios registrados.")

        print("\n--- Poblacion de CU-011, CU-016 y CU-021 completada con exito ---")

    except Exception as err:
        db.rollback()
        print(f"Error al poblar: {err}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_sprint2()
