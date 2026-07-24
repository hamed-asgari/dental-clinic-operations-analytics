-- SQL Server schema for the synthetic dental-clinic dataset.
-- All records are artificial and contain no real patient information.

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;

-- Drop dependent tables first so the script can be rerun safely.
IF OBJECT_ID('dbo.PaymentAllocations', 'U') IS NOT NULL
    DROP TABLE dbo.PaymentAllocations;

IF OBJECT_ID('dbo.Payments', 'U') IS NOT NULL
    DROP TABLE dbo.Payments;

IF OBJECT_ID('dbo.AppointmentProcedures', 'U') IS NOT NULL
    DROP TABLE dbo.AppointmentProcedures;

IF OBJECT_ID('dbo.TreatmentPlanItems', 'U') IS NOT NULL
    DROP TABLE dbo.TreatmentPlanItems;

IF OBJECT_ID('dbo.TreatmentPlans', 'U') IS NOT NULL
    DROP TABLE dbo.TreatmentPlans;

IF OBJECT_ID('dbo.Appointments', 'U') IS NOT NULL
    DROP TABLE dbo.Appointments;

IF OBJECT_ID('dbo.ProcedureCatalog', 'U') IS NOT NULL
    DROP TABLE dbo.ProcedureCatalog;

IF OBJECT_ID('dbo.Dentists', 'U') IS NOT NULL
    DROP TABLE dbo.Dentists;

IF OBJECT_ID('dbo.Patients', 'U') IS NOT NULL
    DROP TABLE dbo.Patients;


CREATE TABLE dbo.Patients (
    patient_id INT NOT NULL,
    birth_year SMALLINT NOT NULL,
    sex VARCHAR(20) NOT NULL,
    city_area VARCHAR(30) NOT NULL,
    registered_at DATETIME2(0) NOT NULL,
    insurance_type VARCHAR(40) NOT NULL,
    referral_source VARCHAR(40) NOT NULL,
    preferred_contact_channel VARCHAR(40) NOT NULL,
    patient_status VARCHAR(20) NOT NULL,

    CONSTRAINT PK_Patients
        PRIMARY KEY (patient_id),

    CONSTRAINT CK_Patients_BirthYear
        CHECK (birth_year BETWEEN 1900 AND 2100),

    CONSTRAINT CK_Patients_Sex
        CHECK (
            sex IN (
                'female',
                'male',
                'other_unknown'
            )
        ),

    CONSTRAINT CK_Patients_Status
        CHECK (
            patient_status IN (
                'active',
                'inactive',
                'archived'
            )
        )
);


CREATE TABLE dbo.Dentists (
    dentist_id INT NOT NULL,
    dentist_role VARCHAR(40) NOT NULL,
    engagement_type VARCHAR(30) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    scheduled_hours_weekly DECIMAL(5,2) NOT NULL,
    active BIT NOT NULL,

    CONSTRAINT PK_Dentists
        PRIMARY KEY (dentist_id),

    CONSTRAINT CK_Dentists_EngagementType
        CHECK (
            engagement_type IN (
                'employee',
                'contractor',
                'visiting_specialist'
            )
        ),

    CONSTRAINT CK_Dentists_DateRange
        CHECK (
            end_date IS NULL
            OR end_date >= start_date
        ),

    CONSTRAINT CK_Dentists_ScheduledHours
        CHECK (
            scheduled_hours_weekly > 0
            AND scheduled_hours_weekly <= 168
        )
);


CREATE TABLE dbo.ProcedureCatalog (
    procedure_code VARCHAR(20) NOT NULL,
    procedure_name VARCHAR(120) NOT NULL,
    procedure_group VARCHAR(30) NOT NULL,
    default_planned_duration_min SMALLINT NOT NULL,
    standard_fee_amount DECIMAL(14,2) NOT NULL,
    standard_direct_cost DECIMAL(14,2) NOT NULL,
    active BIT NOT NULL,

    CONSTRAINT PK_ProcedureCatalog
        PRIMARY KEY (procedure_code),

    CONSTRAINT CK_ProcedureCatalog_Group
        CHECK (
            procedure_group IN (
                'diagnostic',
                'preventive',
                'restorative',
                'endodontic',
                'periodontal',
                'surgical',
                'prosthodontic',
                'orthodontic',
                'pediatric',
                'other'
            )
        ),

    CONSTRAINT CK_ProcedureCatalog_Duration
        CHECK (
            default_planned_duration_min > 0
        ),

    CONSTRAINT CK_ProcedureCatalog_Fee
        CHECK (
            standard_fee_amount > 0
        ),

    CONSTRAINT CK_ProcedureCatalog_Cost
        CHECK (
            standard_direct_cost >= 0
            AND standard_direct_cost
                <= standard_fee_amount
        )
);


CREATE TABLE dbo.Appointments (
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    dentist_id INT NOT NULL,
    booked_at DATETIME2(0) NOT NULL,
    scheduled_start_at DATETIME2(0) NOT NULL,
    planned_duration_min SMALLINT NOT NULL,
    visit_type VARCHAR(40) NOT NULL,
    booking_channel VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    status_updated_at DATETIME2(0) NULL,
    reminder_sent BIT NOT NULL,
    check_in_at DATETIME2(0) NULL,
    chair_start_at DATETIME2(0) NULL,
    chair_end_at DATETIME2(0) NULL,
    checkout_at DATETIME2(0) NULL,
    status_change_reason VARCHAR(40) NULL,
    rescheduled_from_appointment_id INT NULL,

    CONSTRAINT PK_Appointments
        PRIMARY KEY (appointment_id),

    CONSTRAINT FK_Appointments_Patients
        FOREIGN KEY (patient_id)
        REFERENCES dbo.Patients(patient_id),

    CONSTRAINT FK_Appointments_Dentists
        FOREIGN KEY (dentist_id)
        REFERENCES dbo.Dentists(dentist_id),

    CONSTRAINT FK_Appointments_RescheduledFrom
        FOREIGN KEY (rescheduled_from_appointment_id)
        REFERENCES dbo.Appointments(appointment_id),

    CONSTRAINT CK_Appointments_BookingTime
        CHECK (
            booked_at < scheduled_start_at
        ),

    CONSTRAINT CK_Appointments_Duration
        CHECK (
            planned_duration_min > 0
        ),

    CONSTRAINT CK_Appointments_VisitType
        CHECK (
            visit_type IN (
                'new_patient_examination',
                'recall_examination',
                'consultation',
                'treatment',
                'emergency',
                'follow_up'
            )
        ),

    CONSTRAINT CK_Appointments_BookingChannel
        CHECK (
            booking_channel IN (
                'phone',
                'in_person',
                'online',
                'referral',
                'other'
            )
        ),

    CONSTRAINT CK_Appointments_Status
        CHECK (
            status IN (
                'scheduled',
                'completed',
                'cancelled',
                'no_show',
                'rescheduled'
            )
        ),

    CONSTRAINT CK_Appointments_ChairTimes
        CHECK (
            chair_start_at IS NULL
            OR chair_end_at IS NULL
            OR chair_end_at > chair_start_at
        ),

    CONSTRAINT CK_Appointments_CheckoutTime
        CHECK (
            chair_end_at IS NULL
            OR checkout_at IS NULL
            OR checkout_at >= chair_end_at
        )
);


CREATE TABLE dbo.TreatmentPlans (
    plan_id INT NOT NULL,
    patient_id INT NOT NULL,
    proposed_by_dentist_id INT NOT NULL,
    source_appointment_id INT NULL,
    proposed_at DATETIME2(0) NOT NULL,
    plan_status VARCHAR(30) NOT NULL,
    valid_until DATE NULL,

    CONSTRAINT PK_TreatmentPlans
        PRIMARY KEY (plan_id),

    CONSTRAINT FK_TreatmentPlans_Patients
        FOREIGN KEY (patient_id)
        REFERENCES dbo.Patients(patient_id),

    CONSTRAINT FK_TreatmentPlans_Dentists
        FOREIGN KEY (proposed_by_dentist_id)
        REFERENCES dbo.Dentists(dentist_id),

    CONSTRAINT FK_TreatmentPlans_Appointments
        FOREIGN KEY (source_appointment_id)
        REFERENCES dbo.Appointments(appointment_id),

    CONSTRAINT CK_TreatmentPlans_Status
        CHECK (
            plan_status IN (
                'draft',
                'presented',
                'partially_accepted',
                'fully_accepted',
                'declined',
                'expired',
                'closed'
            )
        )
);


CREATE TABLE dbo.TreatmentPlanItems (
    plan_item_id INT NOT NULL,
    plan_id INT NOT NULL,
    procedure_code VARCHAR(20) NOT NULL,
    tooth_code VARCHAR(10) NULL,
    sequence_order SMALLINT NOT NULL,
    priority_level VARCHAR(20) NOT NULL,
    proposed_quantity SMALLINT NOT NULL,
    proposed_fee_amount DECIMAL(14,2) NOT NULL,
    proposed_discount_amount DECIMAL(14,2) NOT NULL,
    decision_status VARCHAR(20) NOT NULL,
    decision_at DATETIME2(0) NULL,

    CONSTRAINT PK_TreatmentPlanItems
        PRIMARY KEY (plan_item_id),

    CONSTRAINT FK_TreatmentPlanItems_Plans
        FOREIGN KEY (plan_id)
        REFERENCES dbo.TreatmentPlans(plan_id),

    CONSTRAINT FK_TreatmentPlanItems_ProcedureCatalog
        FOREIGN KEY (procedure_code)
        REFERENCES dbo.ProcedureCatalog(procedure_code),

    CONSTRAINT CK_TreatmentPlanItems_Sequence
        CHECK (
            sequence_order > 0
        ),

    CONSTRAINT CK_TreatmentPlanItems_Priority
        CHECK (
            priority_level IN (
                'urgent',
                'short_term',
                'elective',
                'maintenance'
            )
        ),

    CONSTRAINT CK_TreatmentPlanItems_Quantity
        CHECK (
            proposed_quantity > 0
        ),

    CONSTRAINT CK_TreatmentPlanItems_Fee
        CHECK (
            proposed_fee_amount > 0
        ),

    CONSTRAINT CK_TreatmentPlanItems_Discount
        CHECK (
            proposed_discount_amount >= 0
            AND proposed_discount_amount
                <= proposed_fee_amount
        ),

    CONSTRAINT CK_TreatmentPlanItems_DecisionStatus
        CHECK (
            decision_status IN (
                'pending',
                'accepted',
                'declined',
                'deferred'
            )
        )
);


CREATE TABLE dbo.AppointmentProcedures (
    appointment_procedure_id INT NOT NULL,
    appointment_id INT NOT NULL,
    plan_item_id INT NULL,
    procedure_code VARCHAR(20) NOT NULL,
    tooth_code VARCHAR(10) NULL,
    quantity SMALLINT NOT NULL,
    completion_status VARCHAR(30) NOT NULL,
    fee_amount DECIMAL(14,2) NOT NULL,
    discount_amount DECIMAL(14,2) NOT NULL,
    direct_cost DECIMAL(14,2) NOT NULL,

    CONSTRAINT PK_AppointmentProcedures
        PRIMARY KEY (appointment_procedure_id),

    CONSTRAINT FK_AppointmentProcedures_Appointments
        FOREIGN KEY (appointment_id)
        REFERENCES dbo.Appointments(appointment_id),

    CONSTRAINT FK_AppointmentProcedures_TreatmentPlanItems
        FOREIGN KEY (plan_item_id)
        REFERENCES dbo.TreatmentPlanItems(plan_item_id),

    CONSTRAINT FK_AppointmentProcedures_ProcedureCatalog
        FOREIGN KEY (procedure_code)
        REFERENCES dbo.ProcedureCatalog(procedure_code),

    CONSTRAINT CK_AppointmentProcedures_Quantity
        CHECK (
            quantity > 0
        ),

    CONSTRAINT CK_AppointmentProcedures_Status
        CHECK (
            completion_status IN (
                'completed',
                'partially_completed',
                'discontinued'
            )
        ),

    CONSTRAINT CK_AppointmentProcedures_Fee
        CHECK (
            fee_amount > 0
        ),

    CONSTRAINT CK_AppointmentProcedures_Discount
        CHECK (
            discount_amount >= 0
            AND discount_amount <= fee_amount
        ),

    CONSTRAINT CK_AppointmentProcedures_Cost
        CHECK (
            direct_cost >= 0
        )
);


CREATE TABLE dbo.Payments (
    payment_id INT NOT NULL,
    patient_id INT NOT NULL,
    received_at DATETIME2(0) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    payment_arrangement VARCHAR(30) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    reference_code VARCHAR(30) NULL,
    notes VARCHAR(255) NULL,

    CONSTRAINT PK_Payments
        PRIMARY KEY (payment_id),

    CONSTRAINT FK_Payments_Patients
        FOREIGN KEY (patient_id)
        REFERENCES dbo.Patients(patient_id),

    CONSTRAINT CK_Payments_TransactionType
        CHECK (
            transaction_type IN (
                'payment',
                'deposit',
                'refund'
            )
        ),

    CONSTRAINT CK_Payments_Arrangement
        CHECK (
            payment_arrangement IN (
                'full_payment',
                'partial_payment',
                'installment',
                'not_applicable'
            )
        ),

    CONSTRAINT CK_Payments_Method
        CHECK (
            payment_method IN (
                'cash',
                'card',
                'bank_transfer',
                'online_payment',
                'other'
            )
        ),

    CONSTRAINT CK_Payments_Amount
        CHECK (
            amount > 0
        ),

    CONSTRAINT CK_Payments_Status
        CHECK (
            payment_status IN (
                'completed',
                'pending',
                'failed',
                'cancelled',
                'reversed'
            )
        )
);


CREATE TABLE dbo.PaymentAllocations (
    allocation_id INT NOT NULL,
    payment_id INT NOT NULL,
    appointment_procedure_id INT NOT NULL,
    allocated_amount DECIMAL(14,2) NOT NULL,

    CONSTRAINT PK_PaymentAllocations
        PRIMARY KEY (allocation_id),

    CONSTRAINT FK_PaymentAllocations_Payments
        FOREIGN KEY (payment_id)
        REFERENCES dbo.Payments(payment_id),

    CONSTRAINT FK_PaymentAllocations_AppointmentProcedures
        FOREIGN KEY (appointment_procedure_id)
        REFERENCES dbo.AppointmentProcedures(
            appointment_procedure_id
        ),

    CONSTRAINT UQ_PaymentAllocations_PaymentProcedure
        UNIQUE (
            payment_id,
            appointment_procedure_id
        ),

    CONSTRAINT CK_PaymentAllocations_Amount
        CHECK (
            allocated_amount > 0
        )
);


-- Indexes for common analytical joins and filters.

CREATE INDEX IX_Appointments_PatientDate
    ON dbo.Appointments (
        patient_id,
        scheduled_start_at
    );

CREATE INDEX IX_Appointments_DentistDate
    ON dbo.Appointments (
        dentist_id,
        scheduled_start_at
    );

CREATE INDEX IX_Appointments_StatusDate
    ON dbo.Appointments (
        status,
        scheduled_start_at
    );

CREATE INDEX IX_AppointmentProcedures_Appointment
    ON dbo.AppointmentProcedures (
        appointment_id
    );

CREATE INDEX IX_AppointmentProcedures_ProcedureCode
    ON dbo.AppointmentProcedures (
        procedure_code
    );

CREATE INDEX IX_AppointmentProcedures_PlanItem
    ON dbo.AppointmentProcedures (
        plan_item_id
    )
    WHERE plan_item_id IS NOT NULL;

CREATE INDEX IX_TreatmentPlans_PatientDate
    ON dbo.TreatmentPlans (
        patient_id,
        proposed_at
    );

CREATE INDEX IX_TreatmentPlanItems_Plan
    ON dbo.TreatmentPlanItems (
        plan_id
    );

CREATE INDEX IX_TreatmentPlanItems_Decision
    ON dbo.TreatmentPlanItems (
        decision_status
    );

CREATE INDEX IX_Payments_PatientDate
    ON dbo.Payments (
        patient_id,
        received_at
    );

CREATE INDEX IX_Payments_StatusType
    ON dbo.Payments (
        payment_status,
        transaction_type
    );

CREATE INDEX IX_PaymentAllocations_Procedure
    ON dbo.PaymentAllocations (
        appointment_procedure_id
    );

CREATE UNIQUE INDEX UX_Payments_ReferenceCode
    ON dbo.Payments (
        reference_code
    )
    WHERE reference_code IS NOT NULL;