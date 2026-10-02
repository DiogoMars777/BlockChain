from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EnvioUnidad(Base):
    __tablename__ = "enviounidad"

    idenviounidad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idenvio: Mapped[int] = mapped_column(Integer, ForeignKey("envio.idenvio"), nullable=False)
    idunidad: Mapped[int] = mapped_column(Integer, ForeignKey("unidadproducto.idunidad"), nullable=False)

    envio = relationship("Envio", back_populates="envio_unidades")
    unidad = relationship("UnidadProducto")
