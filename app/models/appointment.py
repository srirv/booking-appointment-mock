from sqlalchemy import Column, String, DateTime, Date, Time, Boolean
from sqlalchemy.sql import func
import uuid
import random
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
    userPhoneNumber = Column(String, index=True)
    isCancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    @staticmethod
    def generate_id():
        """Generate a 6-digit appointment number"""
        return ''.join(random.choices('0123456789', k=6))
    
    @property
    def appointment_number(self):
        """Use appointmentId as the appointment number"""
        return self.appointmentId 