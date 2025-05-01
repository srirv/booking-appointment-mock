-- Drop triggers first
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop indexes
DROP INDEX IF EXISTS idx_appointments_patientid;
DROP INDEX IF EXISTS idx_appointments_userphone;
DROP INDEX IF EXISTS idx_appointments_date;

-- Drop tables
DROP TABLE IF EXISTS appointments CASCADE; 