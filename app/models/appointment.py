from sqlalchemy import Column, String, DateTime, Date, Time
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    appointmentId = Column(String, primary_key=True, index=True)
    patientId = Column(String, index=True)
    name = Column(String)
    date = Column(Date)
    time = Column(Time)
    department = Column(String)
    doctorName = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @staticmethod
    def generate_id():
        return str(uuid.uuid4()) 