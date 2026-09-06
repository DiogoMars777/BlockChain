from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UsuarioTenantRol(Base):
    __tablename__ = "usuariotenantrol"

    idusuariotenantrol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idusuariotenant: Mapped[int] = mapped_column(Integer, ForeignKey("usuariotenant.idusuariotenant"), nullable=False)
    idrol: Mapped[int] = mapped_column(Integer, ForeignKey("rol.idrol"), nullable=False)

    role = relationship("Role", back_populates="usuario_tenant_roles")
