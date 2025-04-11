from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional

class AppointmentBase(BaseModel):
    patientId: str
    name: str
    date: date
    time: time
    department: str
    doctorName: str

class AppointmentCreateRequest(AppointmentBase):
    pass

class AppointmentUpdateRequest(AppointmentBase):
    pass

class AppointmentPatchRequest(BaseModel):
    patientId: Optional[str] = None
    name: Optional[str] = None
    date: Optional[date] = None
    time: Optional[time] = None
    department: Optional[str] = None
    doctorName: Optional[str] = None

class Appointment(AppointmentBase):
    appointmentId: str
    
    class Config:
        orm_mode = True 