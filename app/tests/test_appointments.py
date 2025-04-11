import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, date, time
import json

from app.main import app

client = TestClient(app)

@pytest.fixture
def appointment_data():
    # Use tomorrow's date and a fixed time for testing
    tomorrow = date.today() + timedelta(days=1)
    test_time = time(10, 30, 0)  # 10:30 AM
    
    return {
        "patientId": "PAT-12345",
        "name": "Test Patient",
        "date": tomorrow.isoformat(),
        "time": test_time.isoformat(),
        "department": "Cardiology",
        "doctorName": "Dr. Test Doctor"
    }

def test_create_appointment(appointment_data):
    response = client.post("/v1/appointments/", json=appointment_data)
    assert response.status_code == 201
    data = response.json()
    assert data["patientId"] == appointment_data["patientId"]
    assert data["name"] == appointment_data["name"]
    assert data["date"] == appointment_data["date"]
    assert data["time"] == appointment_data["time"]
    assert data["department"] == appointment_data["department"]
    assert data["doctorName"] == appointment_data["doctorName"]
    assert "appointmentId" in data
    return data

def test_get_all_appointments():
    response = client.get("/v1/appointments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_appointment_by_id(appointment_data):
    # First create an appointment
    created = test_create_appointment(appointment_data)
    
    # Then retrieve it
    response = client.get(f"/v1/appointments/{created['appointmentId']}")
    assert response.status_code == 200
    assert response.json()["appointmentId"] == created["appointmentId"]

def test_update_appointment(appointment_data):
    # First create an appointment
    created = test_create_appointment(appointment_data)
    
    # Update data
    updated_data = appointment_data.copy()
    updated_data["name"] = "Updated Patient Name"
    updated_data["department"] = "Neurology"
    
    # Then update it
    response = client.put(f"/v1/appointments/{created['appointmentId']}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Patient Name"
    assert data["department"] == "Neurology"

def test_patch_appointment(appointment_data):
    # First create an appointment
    created = test_create_appointment(appointment_data)
    
    # Patch data (only update name and time)
    new_time = time(14, 0, 0)  # 2:00 PM
    patch_data = {
        "name": "Partially Updated Name",
        "time": new_time.isoformat()
    }
    
    # Then patch it
    response = client.patch(f"/v1/appointments/{created['appointmentId']}", json=patch_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Partially Updated Name"
    assert data["time"] == new_time.isoformat()
    # Other fields should remain unchanged
    assert data["date"] == appointment_data["date"]
    assert data["department"] == appointment_data["department"]
    assert data["doctorName"] == appointment_data["doctorName"]

def test_deletes_old_appointments_for_same_patient(appointment_data):
    # Create first appointment
    first_appointment = test_create_appointment(appointment_data)
    first_id = first_appointment["appointmentId"]
    
    # Get all appointments to verify it exists
    response = client.get("/v1/appointments/")
    appointments_before = response.json()
    assert any(a["appointmentId"] == first_id for a in appointments_before)
    
    # Create second appointment for same patient
    second_appointment_data = appointment_data.copy()
    second_appointment_data["department"] = "Neurology"  # Change some data
    next_day = (date.fromisoformat(appointment_data["date"]) + timedelta(days=1)).isoformat()
    second_appointment_data["date"] = next_day  # Change date
    second_appointment = client.post("/v1/appointments/", json=second_appointment_data).json()
    second_id = second_appointment["appointmentId"]
    
    # Get all appointments again
    response = client.get("/v1/appointments/")
    appointments_after = response.json()
    
    # Verify first appointment is gone and only second exists
    assert not any(a["appointmentId"] == first_id for a in appointments_after)
    assert any(a["appointmentId"] == second_id for a in appointments_after)
    
    # Verify count of appointments for this patient is 1
    patient_appointments = [a for a in appointments_after if a["patientId"] == appointment_data["patientId"]]
    assert len(patient_appointments) == 1 