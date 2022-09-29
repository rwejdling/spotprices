from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Float, Integer, BigInteger, String, DateTime, JSON
from sqlalchemy import MetaData, Table, ForeignKey, func

Base = declarative_base()

class SpotPrices(Base):
  __tablename__ = 'spotprices'
  uid = Column(BigInteger, primary_key=True)
  hour_utc = Column(DateTime, nullable=False, unique = True)
  hour_dk = Column(DateTime, nullable=False)
  price_area = Column(String, nullable=False)
  spotprice_eur = Column(Float, nullable=False)
  spotprice_dkk = Column(Float)
  last_updated = Column(DateTime, server_default=func.now())
