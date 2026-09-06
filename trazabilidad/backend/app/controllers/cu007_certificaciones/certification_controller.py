from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.cu007_certificaciones.certification import Certificacion, ProductoCertificacion
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu002_usuarios.user import User
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.views.cu007_certificaciones.certification_views import (
    CertificationCreate,
    CertificationUpdate,
    CertificationResponse,
    ProductCertificationAssign,
    ProductCertificationResponse
)

router = APIRouter(tags=["Gestionar Certificaciones Técnicas (CU-007)"])


class CertificationController:
    @staticmethod
    def list_certifications(db: Session) -> List[CertificationResponse]:
        stmt = select(Certificacion).order_by(Certificacion.idcertificacion.asc())
        certs = db.execute(stmt).scalars().all()
        return [CertificationResponse.model_validate(c) for c in certs]

    @staticmethod
    def create_certification(db: Session, data: CertificationCreate) -> CertificationResponse:
        cert = Certificacion(
            nombre=data.nombre,
            entidademisora=data.entidademisora,
            descripcion=data.descripcion,
            logourl=data.logourl
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return CertificationResponse.model_validate(cert)

    @staticmethod
    def update_certification(db: Session, idcertificacion: int, data: CertificationUpdate) -> CertificationResponse:
        stmt = select(Certificacion).where(Certificacion.idcertificacion == idcertificacion)
        cert = db.execute(stmt).scalar_one_or_none()
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificación con ID {idcertificacion} no encontrada."
            )

        if data.nombre is not None:
            cert.nombre = data.nombre
        if data.entidademisora is not None:
            cert.entidademisora = data.entidademisora
        if data.descripcion is not None:
            cert.descripcion = data.descripcion
        if data.logourl is not None:
            cert.logourl = data.logourl

        db.commit()
        db.refresh(cert)
        return CertificationResponse.model_validate(cert)

    @staticmethod
    def delete_certification(db: Session, idcertificacion: int):
        stmt = select(Certificacion).where(Certificacion.idcertificacion == idcertificacion)
        cert = db.execute(stmt).scalar_one_or_none()
        if not cert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Certificación con ID {idcertificacion} no encontrada."
            )

        db.delete(cert)
        db.commit()
        return {"detail": f"Certificación {idcertificacion} eliminada exitosamente."}

    # Product Certification Assignments
    @staticmethod
    def list_product_certifications(db: Session, idproducto: int) -> List[ProductCertificationResponse]:
        stmt = select(ProductoCertificacion).where(ProductoCertificacion.idproducto == idproducto)
        links = db.execute(stmt).scalars().all()
        return [ProductCertificationResponse.model_validate(l) for l in links]

    @staticmethod
    def assign_product_certification(db: Session, idproducto: int, data: ProductCertificationAssign) -> ProductCertificationResponse:
        # Check product
        stmt_p = select(Producto).where(Producto.idproducto == idproducto)
        if not db.execute(stmt_p).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

        # Check certification
        stmt_c = select(Certificacion).where(Certificacion.idcertificacion == data.idcertificacion)
        if not db.execute(stmt_c).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificación no encontrada.")

        # Check existing
        stmt_e = select(ProductoCertificacion).where(
            ProductoCertificacion.idproducto == idproducto,
            ProductoCertificacion.idcertificacion == data.idcertificacion
        )
        if db.execute(stmt_e).scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta certificación ya está asignada al producto.")

        link = ProductoCertificacion(
            idproducto=idproducto,
            idcertificacion=data.idcertificacion,
            fechaobtencion=data.fechaobtencion
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        return ProductCertificationResponse.model_validate(link)

    @staticmethod
    def remove_product_certification(db: Session, idproducto: int, idcertificacion: int):
        stmt = select(ProductoCertificacion).where(
            ProductoCertificacion.idproducto == idproducto,
            ProductoCertificacion.idcertificacion == idcertificacion
        )
        link = db.execute(stmt).scalar_one_or_none()
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asignación no encontrada.")

        db.delete(link)
        db.commit()
        return {"detail": "Certificación removida del producto."}


# Endpoints
@router.get("/certifications", response_model=List[CertificationResponse])
def get_certifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar certificaciones técnicas (CU-007)."""
    return CertificationController.list_certifications(db)


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def create_certification(
    data: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear una nueva certificación técnica (CU-007)."""
    return CertificationController.create_certification(db, data)


@router.put("/certifications/{idcertificacion}", response_model=CertificationResponse)
def update_certification(
    idcertificacion: int,
    data: CertificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Editar una certificación técnica (CU-007)."""
    return CertificationController.update_certification(db, idcertificacion, data)


@router.delete("/certifications/{idcertificacion}")
def delete_certification(
    idcertificacion: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar una certificación técnica (CU-007)."""
    return CertificationController.delete_certification(db, idcertificacion)


# Product Certification Links
@router.get("/products/{idproducto}/certifications", response_model=List[ProductCertificationResponse])
def get_product_certifications(
    idproducto: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar certificaciones asignadas a un producto (CU-007)."""
    return CertificationController.list_product_certifications(db, idproducto)


@router.post("/products/{idproducto}/certifications", response_model=ProductCertificationResponse, status_code=201)
def assign_product_certification(
    idproducto: int,
    data: ProductCertificationAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Asignar certificación a un producto (CU-007)."""
    return CertificationController.assign_product_certification(db, idproducto, data)


@router.delete("/products/{idproducto}/certifications/{idcertificacion}")
def remove_product_certification(
    idproducto: int,
    idcertificacion: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remover certificación de un producto (CU-007)."""
    return CertificationController.remove_product_certification(db, idproducto, idcertificacion)
