from pydantic import BaseModel, Field
from datetime import datetime, date, time
from typing import Optional

class AppointmentBase(BaseModel):
    patientId: str
    name: str
    date: date
    time: time
    department: str
    doctorName: str
    userPhoneNumber: str

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
    userPhoneNumber: Optional[str] = None

class Appointment(AppointmentBase):
    appointmentId: str
    isCancelled: Optional[bool] = False
    
    @property
    def appointmentNumber(self) -> str:
        return self.appointmentId
    
    class Config:
        orm_mode = True

# New schemas based on OpenAPI spec
class AppointmentAvailabilityResponse(BaseModel):
    slotAvailable: bool
    appointmentTime: Optional[time] = None
    nextAvailableSlot: Optional[datetime] = None
    doctorName: str

class BookingDetailsResponse(BaseModel):
    appointmentDate: date
    appointmentNumber: str
    appointmentTime: time
    userPhoneNumber: str
    userName: str

class AppointmentUserDetailsResponse(BaseModel):
    appointmentAvailable: bool
    appointmentNumber: Optional[str] = None
    userName: Optional[str] = None
    appointmentDate: Optional[date] = None
    appointmentTime: Optional[time] = None

class OtpRequest(BaseModel):
    userPhoneNumber: str

class OtpResponse(BaseModel):
    sentOtp: str = Field(..., regex=r'^\d{6}$')

class RescheduleDetailsResponse(BaseModel):
    rescheduleAvailable: bool

class CancellationDetailsResponse(BaseModel):
    appointmentCancelled: bool

class SmsBookingRequest(BaseModel):
    appointmentDate: date
    appointmentTime: time
    userPhoneNumber: str
    userName: str
    doctorName: str
    userAddress: str

class SmsCancellationRequest(BaseModel):
    appointmentDate: date
    appointmentTime: time
    userPhoneNumber: str
    userName: str

class SmsRescheduleRequest(BaseModel):
    appointmentDate: date
    appointmentTime: time
    userPhoneNumber: str
    userName: str

class SmsResponse(BaseModel):
    smsSent: bool 