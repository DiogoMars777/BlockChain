from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RolPermiso(Base):
    __tablename__ = "rolpermiso"

    idrolpermiso: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idrol: Mapped[int] = mapped_column(Integer, ForeignKey("rol.idrol"), nullable=False)
    idpermiso: Mapped[int] = mapped_column(Integer, ForeignKey("permiso.idpermiso"), nullable=False)

    role = relationship("Role", back_populates="role_permissions")
    permiso = relationship("Permiso", back_populates="role_permissions")
