-- SQL Server schema for synthetic dental-clinic data.
-- Adjust data types after inspecting generated CSV files.

CREATE TABLE dbo.Patients (
    patient_id INT PRIMARY KEY,
    birth_year SMALLINT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    city VARCHAR(50) NOT NULL,
    registration_date DATE NOT NULL,
    insurance_type VARCHAR(30) NOT NULL,
    referral_source VARCHAR(30) NOT NULL
);

CREATE TABLE dbo.Dentists (
    dentist_id INT PRIMARY KEY,
    dentist_role VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    scheduled_hours_weekly DECIMAL(5,2) NOT NULL
);

CREATE TABLE dbo.Appointments (
    appointment_id INT PRIMARY KEY,
    patient_id INT NOT NULL,
    dentist_id INT NOT NULL,
    appointment_datetime DATETIME2 NOT NULL,
    booked_date DATE NOT NULL,
    appointment_type VARCHAR(30) NOT NULL,
    planned_duration_min SMALLINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    reminder_sent BIT NOT NULL,
    wait_time_min SMALLINT NULL,
    CONSTRAINT FK_Appointments_Patients FOREIGN KEY (patient_id) REFERENCES dbo.Patients(patient_id),
    CONSTRAINT FK_Appointments_Dentists FOREIGN KEY (dentist_id) REFERENCES dbo.Dentists(dentist_id)
);

CREATE TABLE dbo.Procedures (
    procedure_id INT PRIMARY KEY,
    appointment_id INT NOT NULL,
    procedure_code VARCHAR(20) NOT NULL,
    procedure_group VARCHAR(30) NOT NULL,
    actual_duration_min SMALLINT NOT NULL,
    fee_amount DECIMAL(12,2) NOT NULL,
    direct_cost DECIMAL(12,2) NOT NULL,
    CONSTRAINT FK_Procedures_Appointments FOREIGN KEY (appointment_id) REFERENCES dbo.Appointments(appointment_id)
);

CREATE TABLE dbo.TreatmentPlans (
    plan_id INT PRIMARY KEY,
    patient_id INT NOT NULL,
    proposed_date DATE NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    accepted_value DECIMAL(12,2) NOT NULL,
    plan_status VARCHAR(30) NOT NULL,
    CONSTRAINT FK_TreatmentPlans_Patients FOREIGN KEY (patient_id) REFERENCES dbo.Patients(patient_id)
);

CREATE TABLE dbo.Payments (
    payment_id INT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    CONSTRAINT FK_Payments_Patients FOREIGN KEY (patient_id) REFERENCES dbo.Patients(patient_id),
    CONSTRAINT FK_Payments_Appointments FOREIGN KEY (appointment_id) REFERENCES dbo.Appointments(appointment_id)
);
