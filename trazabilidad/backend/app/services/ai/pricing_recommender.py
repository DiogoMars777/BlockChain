from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu008_catalogo_empresa.tenant_catalog import CatalogoTenant
from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu012_recepciones.reception import RecepcionCompra, RecepcionDetalle

# Bolivia es UTC-4
BOLIVIA_TZ = timezone(timedelta(hours=-4))


def get_now_bolivia_str() -> str:
    now_bo = datetime.now(BOLIVIA_TZ)
    return now_bo.strftime("%d/%m/%Y %H:%M:%S")


def _to_float(v: Optional[Any]) -> float:
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def _as_bolivia_aware(value: Optional[datetime]) -> Optional[datetime]:
    """Las columnas DateTime se guardan naive; se les asigna la zona de Bolivia."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=BOLIVIA_TZ)
    return value.astimezone(BOLIVIA_TZ)


def _aplicar_delta(precio: float, delta_pct: float) -> float:
    """Aplica un porcentaje de cambio al precio y redondea a dos decimales."""
    return float(
        (Decimal(str(precio)) * (Decimal(1) + Decimal(str(delta_pct)) / Decimal(100))).quantize(
            Decimal("0.01")
        )
    )


def build_pricing_recommendations(
    db: Session,
    tenant_id: int,
    top_n: int = 8,
) -> Dict[str, Any]:
    # Ventas por variante (estado vendido)
    ventas_q = (
        select(
            UnidadProducto.idvariante,
            func.count(UnidadProducto.idunidad).label("vendidas"),
            func.min(UnidadProducto.fechaventa).label("primera_venta"),
            func.max(UnidadProducto.fechaventa).label("ultima_venta"),
        )
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.estado == "vendido",
        )
        .group_by(UnidadProducto.idvariante)
    )
    ventas_map: Dict[int, Dict[str, Any]] = {
        row.idvariante: {
            "vendidas": int(row.vendidas or 0),
            "primera_venta": row.primera_venta,
            "ultima_venta": row.ultima_venta,
        }
        for row in db.execute(ventas_q).all()
    }

    # Disponibles
    disp_q = (
        select(
            UnidadProducto.idvariante,
            func.count(UnidadProducto.idunidad).label("disponibles"),
        )
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.estado == "disponible",
        )
        .group_by(UnidadProducto.idvariante)
    )
    disp_map: Dict[int, Dict[str, Any]] = {
        row.idvariante: {"disponibles": int(row.disponibles or 0)}
        for row in db.execute(disp_q).all()
    }

    # Devueltos
    dev_q = (
        select(
            UnidadProducto.idvariante,
            func.count(UnidadProducto.idunidad).label("devueltas"),
        )
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.estado == "devuelto",
        )
        .group_by(UnidadProducto.idvariante)
    )
    dev_map: Dict[int, Dict[str, Any]] = {
        row.idvariante: {"devueltas": int(row.devueltas or 0)}
        for row in db.execute(dev_q).all()
    }

    # Demanda pedida (CompraDetalle)
    ped_q = (
        select(
            CompraDetalle.idvariante,
            func.sum(CompraDetalle.cantidad).label("cant_pedida"),
        )
        .join(Compra, Compra.idcompra == CompraDetalle.idcompra)
        .where(Compra.idtenant == tenant_id)
        .group_by(CompraDetalle.idvariante)
    )
    ped_map: Dict[int, Dict[str, Any]] = {
        row.idvariante: {"cant_pedida": int(row.cant_pedida or 0)}
        for row in db.execute(ped_q).all()
    }

    # Recibido
    rec_q = (
        select(
            RecepcionDetalle.idvariante,
            func.sum(RecepcionDetalle.cantidadrecibida).label("cant_recibida"),
        )
        .join(RecepcionCompra, RecepcionCompra.idrecepcion == RecepcionDetalle.idrecepcion)
        .join(Compra, Compra.idcompra == RecepcionCompra.idcompra)
        .where(Compra.idtenant == tenant_id)
        .group_by(RecepcionDetalle.idvariante)
    )
    rec_map: Dict[int, Dict[str, Any]] = {
        row.idvariante: {"cant_recibida": int(row.cant_recibida or 0)}
        for row in db.execute(rec_q).all()
    }

    # Catálogo
    cat_rows = (
        db.execute(
            select(
                CatalogoTenant,
                VarianteProducto,
                Producto,
            )
            .select_from(CatalogoTenant)
            .join(VarianteProducto, VarianteProducto.idvariante == CatalogoTenant.idvariante)
            .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
            .where(
                CatalogoTenant.idtenant == tenant_id,
                CatalogoTenant.activo == True,
            )
        )
        .all()
    )

    now = datetime.now(BOLIVIA_TZ)
    items: List[Dict[str, Any]] = []
    for cat, var, prod in cat_rows:
        vid = var.idvariante
        v = ventas_map.get(vid, {})
        d = disp_map.get(vid, {})
        dv = dev_map.get(vid, {})
        p = ped_map.get(vid, {})
        r = rec_map.get(vid, {})

        vendidas = int(v.get("vendidas", 0))
        disponibles = int(d.get("disponibles", 0))
        devueltas = int(dv.get("devueltas", 0))
        pedidas = int(p.get("cant_pedida", 0))
        recibidas = int(r.get("cant_recibida", 0))

        cost = _to_float(cat.costopromedio or 0)
        price = _to_float(cat.precioventa or 0)
        margen_pct = ((price - cost) / price * 100.0) if price > 0 else 0.0
        margen_abs_usd = price - cost

        # Rotación simple
        ultima = _as_bolivia_aware(v.get("ultima_venta"))
        dias_activos = 90.0
        if ultima:
            delta = (now - ultima).days
            dias_activos = max(30.0, float(delta)) if delta >= 1 else 90.0
        rotacion_mensual = (vendidas / dias_activos * 30.0) if dias_activos > 0 else 0.0

        brecha_demanda = pedidas - vendidas
        devolucion_pct = (devueltas / vendidas * 100.0) if vendidas > 0 else 0.0

        rec_list = []

        if price < cost + 0.01 and price > 0:
            tipo = "MARGEN_NEGATIVO"
            prioridad = "critica"
            accion = f"Corregir precio de venta. Costo ${cost:,.2f} USD vs precio ${price:,.2f} USD."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Margen negativo en {prod.nombre} {var.capacidad}",
                "justificacion": "Precio de venta por debajo del costo promedio. Genera pérdida en cada unidad vendida.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "disponibles": disponibles,
                    "devueltas": devueltas,
                    "pedidas": pedidas,
                    "recibidas": recibidas,
                    "precioventa": round(price, 2),
                    "costopromedio": round(cost, 2),
                    "margen_pct": round(margen_pct, 2),
                    "margen_abs_usd": round(margen_abs_usd, 2),
                    "rotacion_mensual": round(rotacion_mensual, 2),
                    "devolucion_pct": round(devolucion_pct, 2),
                    "brecha_demanda": brecha_demanda,
                },
                "evidencia": [f"SKU: {var.sku}", f"Stock disponible: {disponibles}", f"Vendidas: {vendidas}"],
            })

        if rotacion_mensual >= 0.6 and margen_pct < 15.0 and price >= cost:
            tipo = "SUBIR_PRECIO"
            prioridad = "alta"
            delta_pct = 8.0
            nuevo_precio = _aplicar_delta(price, delta_pct)
            accion = f"Subir precio ~{delta_pct}% → ${nuevo_precio:,.2f} USD."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Rotación alta, margen bajo: {prod.nombre}",
                "justificacion": "Se vende con frecuencia pero el margen bruto está por debajo de 15%. Hay espacio para subir precio sin frenar la demanda.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "disponibles": disponibles,
                    "precioventa": round(price, 2),
                    "costopromedio": round(cost, 2),
                    "margen_pct": round(margen_pct, 2),
                    "rotacion_mensual": round(rotacion_mensual, 2),
                    "precio_sugerido_usd": nuevo_precio,
                },
                "evidencia": [f"Rotación mensual estimada: {rotacion_mensual:.2f} und/mes", f"Margen: {margen_pct:.1f}%"],
            })

        if margen_pct > 45.0 and vendidas == 0 and disponibles > 0:
            tipo = "BAJAR_PRECIO"
            prioridad = "media"
            delta_pct = -10.0
            nuevo_precio = _aplicar_delta(price, delta_pct)
            accion = f"Bajar precio ~{abs(delta_pct)}% → ${nuevo_precio:,.2f} USD para activar rotación."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Margen alto sin ventas: {prod.nombre}",
                "justificacion": "Margen superior a 45% con 0 ventas y stock disponible. Probable precio fuera del mercado.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "disponibles": disponibles,
                    "precioventa": round(price, 2),
                    "costopromedio": round(cost, 2),
                    "margen_pct": round(margen_pct, 2),
                    "precio_sugerido_usd": nuevo_precio,
                },
                "evidencia": [f"Stock disponible: {disponibles}", f"Vendidas últimos 90 días: {vendidas}"],
            })

        if disponibles > vendidas * 3 and vendidas == 0 and disponibles >= 2:
            tipo = "SOBRESTOCK"
            prioridad = "media"
            accion = "Ejecutar promoción para liquidar stock o ajustar precio para acelerar rotación."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Sobrestock sin rotación: {prod.nombre}",
                "justificacion": "Stock disponible alto vs. ventas nulas en los últimos 90 días. Capital inmovilizado.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "disponibles": disponibles,
                    "precioventa": round(price, 2),
                    "costopromedio": round(cost, 2),
                    "margen_pct": round(margen_pct, 2),
                },
                "evidencia": [f"Ratio disp/vendidas: {disponibles}/{vendidas or 0}"],
            })

        if rotacion_mensual >= 0.8 and disponibles <= 2:
            tipo = "REPOSICION_URGENTE"
            prioridad = "alta"
            accion = "Generar orden de compra para reponer este SKU con mayor urgencia."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Reponer stock urgente: {prod.nombre}",
                "justificacion": "Rotación elevada con stock disponible crítico. Riesgo de pérdida de ventas.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "disponibles": disponibles,
                    "rotacion_mensual": round(rotacion_mensual, 2),
                    "pedidas": pedidas,
                    "recibidas": recibidas,
                },
                "evidencia": [f"Disponibles: {disponibles}", f"Pedidas vs recibidas: {pedidas}/{recibidas}"],
            })

        if vendidas > 0 and devolucion_pct >= 20.0:
            tipo = "RIESGO_DEVOLUCION"
            prioridad = "alta"
            accion = "Revisar origen de devoluciones y calidad antes de reabastecer."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Alto % de devoluciones: {prod.nombre}",
                "justificacion": f"{devolucion_pct:.1f}% de las unidades vendidas fueron devueltas. Señal de alerta operativa o comercial.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "devueltas": devueltas,
                    "devolucion_pct": round(devolucion_pct, 2),
                    "disponibles": disponibles,
                },
                "evidencia": [f"Devueltas: {devueltas}", f"% devoluciones: {devolucion_pct:.1f}%"],
            })

        if brecha_demanda > 0 and vendidas > 0 and rotacion_mensual < 1.0:
            tipo = "BRECHA_DEMANDA"
            prioridad = "media"
            accion = "Analizar capacidad de recepción vs. lo pedido para ajustar compras futuras."
            rec_list.append({
                "idvariante": vid,
                "sku": var.sku,
                "producto": prod.nombre,
                "capacidad": var.capacidad,
                "color": var.color,
                "tipo": tipo,
                "prioridad": prioridad,
                "titulo": f"Brecha entre pedido y ventas: {prod.nombre}",
                "justificacion": "Cantidad pedida supera las ventas registradas. Puede indicar sobrecompra o retraso en recepción.",
                "accion_sugerida": accion,
                "metricas": {
                    "vendidas": vendidas,
                    "pedidas": pedidas,
                    "recibidas": recibidas,
                    "brecha_demanda": brecha_demanda,
                },
                "evidencia": [f"Pedidas: {pedidas}", f"Vendidas: {vendidas}", f"Recibidas: {recibidas}"],
            })

        items.extend(rec_list)

    # Ordenar: crítica, alta, media, baja
    prio_order = {"critica": 0, "alta": 1, "media": 2, "baja": 3}
    items.sort(key=lambda x: (prio_order.get(x["prioridad"], 9), -float(x["metricas"].get("vendidas", 0))))

    return {
        "tenant_id": tenant_id,
        "generated_at": get_now_bolivia_str(),
        "total_recomendaciones": len(items),
        "recomendaciones": items[:top_n],
    }