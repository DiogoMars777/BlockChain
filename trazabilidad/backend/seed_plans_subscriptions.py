"""
Script de seed para poblar planes y suscripciones de prueba (CU-036 y CU-037).
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.db.session import SessionLocal
from app.packages.p1_seguridad.models.cu036_planes.subscription_models import Plan, Suscripcion
from app.models.cu001_tenants.tenant import Tenant

def seed_plans_and_subscriptions():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        planes_data = [
            {
                "codigo": "trial",
                "nombre": "Prueba Gratuita (Trial)",
                "descripcion": "Acceso inicial de 14 días para evaluación con cuotas controladas.",
                "preciomensual": Decimal("0.00"),
                "precioanual": Decimal("0.00"),
                "moneda": "USD",
                "limiteusuarios": 3,
                "limiteunidades": 20,
                "limitereportesmes": 50,
                "limitealmacenamientomb": 100,
                "diastrial": 14,
                "activo": True,
            },
            {
                "codigo": "basico",
                "nombre": "Plan Básico Starter",
                "descripcion": "Ideal para pequeños importadores y tiendas boutique de Apple.",
                "preciomensual": Decimal("49.00"),
                "precioanual": Decimal("490.00"),
                "moneda": "USD",
                "limiteusuarios": 5,
                "limiteunidades": 100,
                "limitereportesmes": 200,
                "limitealmacenamientomb": 500,
                "diastrial": 0,
                "activo": True,
            },
            {
                "codigo": "pro",
                "nombre": "Plan Profesional Business",
                "descripcion": "Para distribuidores mayoristas con múltiples sucursales en Bolivia.",
                "preciomensual": Decimal("149.00"),
                "precioanual": Decimal("1490.00"),
                "moneda": "USD",
                "limiteusuarios": 20,
                "limiteunidades": 1000,
                "limitereportesmes": 1000,
                "limitealmacenamientomb": 2048,
                "diastrial": 0,
                "activo": True,
            },
            {
                "codigo": "enterprise",
                "nombre": "Plan Enterprise Corporativo",
                "descripcion": "Volumen ilimitado, soporte 24/7 y anclaje prioritario en blockchain.",
                "preciomensual": Decimal("399.00"),
                "precioanual": Decimal("3990.00"),
                "moneda": "USD",
                "limiteusuarios": None,
                "limiteunidades": None,
                "limitereportesmes": None,
                "limitealmacenamientomb": 10240,
                "diastrial": 0,
                "activo": True,
            },
        ]

        planes_creados = {}
        for p in planes_data:
            existente = db.query(Plan).filter(Plan.codigo == p["codigo"]).first()
            if not existente:
                nuevo = Plan(
                    codigo=p["codigo"],
                    nombre=p["nombre"],
                    descripcion=p["descripcion"],
                    preciomensual=p["preciomensual"],
                    precioanual=p["precioanual"],
                    moneda=p["moneda"],
                    limiteusuarios=p["limiteusuarios"],
                    limiteunidades=p["limiteunidades"],
                    limitereportesmes=p["limitereportesmes"],
                    limitealmacenamientomb=p["limitealmacenamientomb"],
                    diastrial=p["diastrial"],
                    activo=p["activo"],
                    creadoen=now,
                    actualizadoen=now,
                )
                db.add(nuevo)
                db.flush()
                planes_creados[p["codigo"]] = nuevo
            else:
                planes_creados[p["codigo"]] = existente

        # Backfill para tenants existentes 1..5
        tenants = db.query(Tenant).all()
        subs_creadas = 0
        for idx, t in enumerate(tenants):
            tiene_sub = db.query(Suscripcion).filter(Suscripcion.idtenant == t.idtenant).first()
            if not tiene_sub:
                # Tenant 1 y 2 tienen Pro, Tenant 3 tiene Básico, Tenant 4 y 5 tienen Trial
                if t.idtenant in (1, 2):
                    plan_asignar = planes_creados.get("pro")
                    estado = "activa"
                    dias = 365
                elif t.idtenant == 3:
                    plan_asignar = planes_creados.get("basico")
                    estado = "activa"
                    dias = 180
                else:
                    plan_asignar = planes_creados.get("trial")
                    estado = "trial"
                    dias = 14

                sub = Suscripcion(
                    idtenant=t.idtenant,
                    idplan=plan_asignar.idplan,
                    estado=estado,
                    fechainicio=now,
                    fechafin=now + timedelta(days=dias),
                    renovacionautomatica=(estado == "activa"),
                    creadoen=now,
                    actualizadoen=now,
                )
                db.add(sub)
                subs_creadas += 1

        db.commit()
        print(f"Planes verificados. Suscripciones creadas para {subs_creadas} empresas.")
    except Exception as e:
        db.rollback()
        print(f"Error en seed de planes/suscripciones: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_plans_and_subscriptions()

