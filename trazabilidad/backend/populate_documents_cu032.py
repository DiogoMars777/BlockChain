"""
=============================================================================
SCRIPT DE POBLADO DE DOCUMENTOS ADJUNTOS A UNIDADES (CU-032)
=============================================================================
Puebla de forma realista y multi-tenant la tabla `documentounidad` con
documentos técnicos y legales vinculados a unidades físicas reales de los 5 tenants:
  - Factura comercial de compra (Apple Store / Distribuidor USA)
  - Certificado de importación y póliza aduanera (Aduana Nacional de Bolivia)
  - Comprobante de garantía oficial Apple Care / Distribuidor
  - Certificado de autenticidad criptográfica
  - Informe técnico de recepción y control de calidad
Cada documento incluye:
  - Nombre representativo del documento oficial
  - URL de almacenamiento cloud simulada (ej. Cloud Storage / S3 / IPFS)
  - Hash criptográfico SHA-256 verificado del contenido del documento
  - Fecha de emisión y fecha de vencimiento según corresponda
  - Tipo de documento válido del Enum:
    ('factura_compra', 'certificado_importacion', 'comprobante_garantia',
     'certificado_autenticidad', 'informe_tecnico')
=============================================================================
"""

import hashlib
import random
from datetime import date, timedelta
from typing import List, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu032_documentos_unidad.documento_unidad import DocumentoUnidad

# Plantillas de documentos por tipo
DOC_TEMPLATES = [
    {
        "tipo": "factura_compra",
        "nombre_fmt": "Factura Comercial USA #{num}",
        "url_fmt": "https://storage.appletrace.bo/tenants/{tenant}/invoices/inv_{serial}_{num}.pdf",
        "raw_prefix": "INVOICE-APPLE-USA-RETAIL-STORE-",
        "vigencia_dias": None,
        "emision_offset": 60,
    },
    {
        "tipo": "certificado_importacion",
        "nombre_fmt": "Póliza de Importación DUI-ANB #{num}",
        "url_fmt": "https://storage.appletrace.bo/tenants/{tenant}/customs/dui_{serial}_{num}.pdf",
        "raw_prefix": "CUSTOMS-DECLARATION-BOLIVIA-ANB-",
        "vigencia_dias": 365 * 5,  # 5 años
        "emision_offset": 45,
    },
    {
        "tipo": "comprobante_garantia",
        "nombre_fmt": "Certificado de Garantía Apple Care #{num}",
        "url_fmt": "https://storage.appletrace.bo/tenants/{tenant}/warranty/garantia_{serial}.pdf",
        "raw_prefix": "APPLECARE-WARRANTY-AGREEMENT-GLOBAL-",
        "vigencia_dias": 365,  # 1 año
        "emision_offset": 30,
    },
    {
        "tipo": "certificado_autenticidad",
        "nombre_fmt": "Certificado Criptográfico de Autenticidad #{num}",
        "url_fmt": "https://storage.appletrace.bo/tenants/{tenant}/certificates/cert_autenticidad_{serial}.pdf",
        "raw_prefix": "CRYPTO-AUTHENTICITY-CERT-BOLIVIA-ORIGINAL-",
        "vigencia_dias": 365 * 3,  # 3 años
        "emision_offset": 20,
    },
    {
        "tipo": "informe_tecnico",
        "nombre_fmt": "Acta de Inspección Técnica Inicial #{num}",
        "url_fmt": "https://storage.appletrace.bo/tenants/{tenant}/reports/inspeccion_{serial}.pdf",
        "raw_prefix": "TECH-INSPECTION-CHECKLIST-PASSED-",
        "vigencia_dias": None,
        "emision_offset": 15,
    },
]


def generar_hash(contenido_texto: str) -> str:
    return hashlib.sha256(contenido_texto.encode("utf-8")).hexdigest()


def populate_documents():
    db: Session = SessionLocal()
    print("=" * 70)
    print("POBLANDO DOCUMENTOS ADJUNTOS A UNIDADES (CU-032)")
    print("=" * 70)

    try:
        tenants = db.execute(select(Tenant).order_by(Tenant.idtenant.asc())).scalars().all()
        if not tenants:
            print("❌ No se encontraron empresas (tenants). Ejecute seed.py primero.")
            return

        total_documentos_creados = 0
        hoy = date.today()

        for t in tenants:
            # Obtener unidades para este tenant
            unidades = db.execute(
                select(UnidadProducto)
                .where(UnidadProducto.idtenant == t.idtenant)
                .order_by(UnidadProducto.idunidad.asc())
            ).scalars().all()

            if not unidades:
                print(f"  [Tenant #{t.idtenant} - {t.nombre}] Sin unidades registradas. Saltando.")
                continue

            print(f"\n🏢 Tenant #{t.idtenant}: {t.nombre} ({len(unidades)} unidades encontradas)")

            # Poblar documentos para un subconjunto representativo de unidades (ej. primeras 15 por tenant)
            # o seleccionar unidades variadas
            unidades_a_poblar = unidades[:15]
            docs_tenant = 0

            for idx, u in enumerate(unidades_a_poblar):
                # Verificar si la unidad ya tiene documentos asignados
                docs_existentes = db.execute(
                    select(DocumentoUnidad).where(DocumentoUnidad.idunidad == u.idunidad)
                ).scalars().all()

                if docs_existentes:
                    continue

                # Cada unidad tendrá entre 2 y 4 documentos variados
                # Para la primera mitad, asignamos los 4 principales (factura, importación, garantía, autenticidad)
                if idx % 2 == 0:
                    templates_asignadas = DOC_TEMPLATES[:4]
                else:
                    templates_asignadas = [DOC_TEMPLATES[0], DOC_TEMPLATES[1], DOC_TEMPLATES[4]]

                for tmpl in templates_asignadas:
                    num_rand = random.randint(10000, 99999)
                    serial = u.numeroserie
                    nombre_doc = tmpl["nombre_fmt"].format(num=num_rand)
                    url_doc = tmpl["url_fmt"].format(tenant=t.idtenant, serial=serial, num=num_rand)

                    contenido_simulado = f"{tmpl['raw_prefix']}{serial}-{num_rand}-{t.idtenant}"
                    hash_sha256 = generar_hash(contenido_simulado)

                    fecha_emision = hoy - timedelta(days=tmpl["emision_offset"] + random.randint(0, 10))
                    fecha_vencimiento = None
                    if tmpl["vigencia_dias"]:
                        fecha_vencimiento = fecha_emision + timedelta(days=tmpl["vigencia_dias"])

                    doc = DocumentoUnidad(
                        idunidad=u.idunidad,
                        nombre=nombre_doc,
                        urlarchivo=url_doc,
                        hasharchivo=hash_sha256,
                        fechaemision=fecha_emision,
                        fechavencimiento=fecha_vencimiento,
                        tipodocumento=tmpl["tipo"],
                    )
                    db.add(doc)
                    docs_tenant += 1
                    total_documentos_creados += 1

            db.commit()
            print(f"  ✓ {docs_tenant} documentos creados para {len(unidades_a_poblar)} unidades.")

        total_en_db = db.query(DocumentoUnidad).count()
        print("\n" + "=" * 70)
        print(f"✅ POBLADO COMPLETADO EXITOSAMENTE:")
        print(f"   - Nuevos documentos insertados: {total_documentos_creados}")
        print(f"   - Total de documentos en la base de datos: {total_en_db}")
        print("=" * 70)

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante el poblado de documentos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_documents()

