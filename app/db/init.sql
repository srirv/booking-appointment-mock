-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    "appointmentId" VARCHAR PRIMARY KEY,
    "patientId" VARCHAR NOT NULL,
    "name" VARCHAR NOT NULL,
    "date" DATE NOT NULL,
    "time" TIME NOT NULL,
    "department" VARCHAR NOT NULL,
    "doctorName" VARCHAR NOT NULL,
    "userPhoneNumber" VARCHAR NOT NULL,
    "isCancelled" BOOLEAN DEFAULT FALSE,
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_appointments_patientid ON appointments("patientId");
CREATE INDEX IF NOT EXISTS idx_appointments_userphone ON appointments("userPhoneNumber");
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments("date");

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE OR REPLACE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust according to your needs)
GRANT SELECT, INSERT, UPDATE, DELETE ON appointments TO neondb_owner; 