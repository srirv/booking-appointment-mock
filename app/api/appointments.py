from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.models.appointment import Appointment as AppointmentModel
from app.schemas.appointment import (
    Appointment, 
    AppointmentCreateRequest, 
    AppointmentUpdateRequest, 
    AppointmentPatchRequest
)
from app.db.base import get_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@router.get("/", response_model=List[Appointment])
def get_all_appointments(db: Session = Depends(get_db)):
    appointments = db.query(AppointmentModel).all()
    return appointments

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreateRequest, db: Session = Depends(get_db)):
    # Delete any existing appointments for this patient
    existing_appointments = db.query(AppointmentModel).filter(
        AppointmentModel.patientId == appointment.patientId
    ).all()
    
    if existing_appointments:
        for existing_appointment in existing_appointments:
            db.delete(existing_appointment)
        db.commit()
    
    # Create new appointment
    db_appointment = AppointmentModel(
        appointmentId=AppointmentModel.generate_id(),
        patientId=appointment.patientId,
        name=appointment.name,
        date=appointment.date,
        time=appointment.time,
        department=appointment.department,
        doctorName=appointment.doctorName
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/{appointmentId}", response_model=Appointment)
def get_appointment_by_id(appointmentId: str, db: Session = Depends(get_db)):
    appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointmentId}", response_model=Appointment)
def update_appointment(appointmentId: str, appointment: AppointmentUpdateRequest, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update all fields
    update_data = appointment.dict()
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.patch("/{appointmentId}", response_model=Appointment)
def patch_appointment(appointmentId: str, appointment: AppointmentPatchRequest, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update only provided fields
    update_data = appointment.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment 