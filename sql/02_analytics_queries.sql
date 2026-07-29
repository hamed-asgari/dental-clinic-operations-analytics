-- Core analytics queries for the synthetic dental-clinic dataset.
-- Each query is linked to a defined operational or management question.

SET
NOCOUNT ON;


-- 1. Appointment status distribution
-- Management question:
-- What proportion of scheduled activity ends in completion,
-- cancellation, rescheduling, or no-show?

SELECT status,
       COUNT(*) AS appointment_count,
       CAST(
               100.0 * COUNT(*)
                   / SUM(COUNT(*)) OVER ()
           AS DECIMAL (6, 2)
       )        AS appointment_percentage
FROM dbo.Appointments
GROUP BY status
ORDER BY appointment_count DESC;


-- 2. No-show rate by reminder status
-- Management question:
-- Are reminders associated with a lower synthetic no-show rate?

SELECT CASE
           WHEN reminder_sent = 1
               THEN 'reminder_sent'
           ELSE 'no_reminder'
           END  AS reminder_group,
       COUNT(*) AS total_appointments,
       SUM(
               CASE
                   WHEN status = 'no_show'
                       THEN 1
                   ELSE 0
                   END
       )        AS no_show_count,
       CAST(
               100.0
                   * SUM(
                       CASE
                           WHEN status = 'no_show'
                               THEN 1
                           ELSE 0
                           END
                     )
                   / NULLIF(COUNT(*), 0)
           AS DECIMAL(6, 2)
       )        AS no_show_rate_percentage
FROM dbo.Appointments
GROUP BY reminder_sent
ORDER BY reminder_sent DESC;


-- 3. Monthly chair-time performance by dentist
-- Management question:
-- How much actual clinical chair time is delivered by each dentist,
-- and how do waiting time and schedule variance differ?

SELECT a.dentist_id,
       d.dentist_role,
       DATEFROMPARTS(
           YEAR(a.scheduled_start_at), MONTH(a.scheduled_start_at), 1
       )        AS month_start,
       COUNT(*) AS completed_appointments,
       SUM(
               DATEDIFF(
                   MINUTE, a.chair_start_at,
                           a.chair_end_at
               )
       )        AS actual_chair_minutes,
       CAST(
               AVG(
                       1.0 * DATEDIFF(
                           MINUTE, a.check_in_at,
                                   a.chair_start_at
                             )
               )
           AS DECIMAL(10, 2)
       )        AS average_waiting_minutes,
       CAST(
               AVG(
                       1.0 * (
                           DATEDIFF(
                               MINUTE, a.chair_start_at,
                                       a.chair_end_at
                           )
                               - a.planned_duration_min
                           )
               )
           AS DECIMAL(10, 2)
       )        AS average_schedule_variance_minutes
FROM dbo.Appointments AS a
         INNER JOIN dbo.Dentists AS d
                    ON d.dentist_id = a.dentist_id
WHERE a.status = 'completed'
GROUP BY a.dentist_id,
         d.dentist_role,
         DATEFROMPARTS(
             YEAR(a.scheduled_start_at), MONTH(a.scheduled_start_at), 1
         )
ORDER BY month_start,
         a.dentist_id;


-- 4. Revenue and direct margin by procedure group
-- Management question:
-- Which clinical service groups generate the highest revenue
-- and direct financial contribution?

SELECT pc.procedure_group,
       COUNT(*) AS procedure_count,
       SUM(ap.quantity) AS procedure_unit_count,
       COUNT(
               DISTINCT ap.appointment_id
       )        AS appointment_count,
       CAST(
               SUM(ap.fee_amount)
           AS DECIMAL(16, 2)
       )        AS gross_fee_amount,
       CAST(
               SUM(ap.discount_amount)
           AS DECIMAL(16, 2)
       )        AS discount_amount,
       CAST(
               SUM(
                       ap.fee_amount
                           - ap.discount_amount
               )
           AS DECIMAL(16, 2)
       )        AS net_procedure_revenue,
       CAST(
               SUM(ap.direct_cost)
           AS DECIMAL(16, 2)
       )        AS direct_cost,
       CAST(
               SUM(
                       ap.fee_amount
                           - ap.discount_amount
                           - ap.direct_cost
               )
           AS DECIMAL(16, 2)
       )        AS direct_margin,
       CAST(
               100.0
                   * SUM(
                       ap.fee_amount
                           - ap.discount_amount
                           - ap.direct_cost
                     )
                   / NULLIF(
                       SUM(
                               ap.fee_amount
                                   - ap.discount_amount
                       ),
                       0
                     )
           AS DECIMAL(6, 2)
       )        AS direct_margin_percentage
FROM dbo.AppointmentProcedures AS ap
         INNER JOIN dbo.ProcedureCatalog AS pc
                    ON pc.procedure_code = ap.procedure_code
GROUP BY pc.procedure_group
ORDER BY net_procedure_revenue DESC;


-- 5. Treatment-plan acceptance by plan status
-- Management question:
-- What share of decided treatment items is accepted,
-- and what share of total proposed value is accepted?

WITH PlanValues AS (
    SELECT
        tp.plan_id,
        tp.plan_status,
        COUNT(*) AS proposed_item_count,
        SUM(
            CASE
                WHEN tpi.decision_status IN ('accepted', 'declined', 'deferred')
                    THEN 1
                ELSE 0
            END
        ) AS decided_item_count,
        SUM(
            CASE
                WHEN tpi.decision_status = 'accepted'
                    THEN 1
                ELSE 0
            END
        ) AS accepted_item_count,
        SUM(
            tpi.proposed_fee_amount
                - tpi.proposed_discount_amount
        ) AS proposed_value,
        SUM(
            CASE
                WHEN tpi.decision_status = 'accepted'
                    THEN (
                        tpi.proposed_fee_amount
                            - tpi.proposed_discount_amount
                    )
                ELSE 0
            END
        ) AS accepted_value
    FROM dbo.TreatmentPlans AS tp
    INNER JOIN dbo.TreatmentPlanItems AS tpi
        ON tpi.plan_id = tp.plan_id
    GROUP BY
        tp.plan_id,
        tp.plan_status
)
SELECT
    plan_status,
    COUNT(*) AS plan_count,
    SUM(proposed_item_count) AS proposed_item_count,
    SUM(decided_item_count) AS decided_item_count,
    SUM(accepted_item_count) AS accepted_item_count,
    CAST(
        100.0 * SUM(accepted_item_count)
            / NULLIF(SUM(decided_item_count), 0)
        AS DECIMAL(6, 2)
    ) AS decided_item_acceptance_rate_percentage,
    CAST(
        SUM(proposed_value)
        AS DECIMAL(16, 2)
    ) AS proposed_value,
    CAST(
        SUM(accepted_value)
        AS DECIMAL(16, 2)
    ) AS accepted_value,
    CAST(
        100.0 * SUM(accepted_value)
            / NULLIF(SUM(proposed_value), 0)
        AS DECIMAL(6, 2)
    ) AS proposed_value_acceptance_rate_percentage
FROM PlanValues
GROUP BY plan_status
ORDER BY proposed_value DESC;


-- 6. Appointment non-completion by weekday
-- Management question:
-- Which weekdays have the highest rates of cancellation,
-- rescheduling, or no-show?

SET DATEFIRST 1;

SELECT
    DATENAME(WEEKDAY, scheduled_start_at) AS weekday_name,
    DATEPART(WEEKDAY, scheduled_start_at) AS weekday_number,
    COUNT(*) AS total_appointments,
    SUM(
        CASE
            WHEN status = 'completed'
                THEN 1
            ELSE 0
        END
    ) AS completed_count,
    SUM(
        CASE
            WHEN status IN ('cancelled', 'rescheduled', 'no_show')
                THEN 1
            ELSE 0
        END
    ) AS non_completed_count,
    CAST(
        100.0
            * SUM(
                CASE
                    WHEN status IN ('cancelled', 'rescheduled', 'no_show')
                        THEN 1
                    ELSE 0
                END
              )
            / NULLIF(COUNT(*), 0)
        AS DECIMAL(6, 2)
    ) AS non_completion_rate_percentage,
    SUM(
        CASE
            WHEN status = 'no_show'
                THEN 1
            ELSE 0
        END
    ) AS no_show_count,
    CAST(
        100.0
            * SUM(
                CASE
                    WHEN status = 'no_show'
                        THEN 1
                    ELSE 0
                END
              )
            / NULLIF(COUNT(*), 0)
        AS DECIMAL(6, 2)
    ) AS no_show_rate_percentage
FROM dbo.Appointments
GROUP BY
    DATENAME(WEEKDAY, scheduled_start_at),
    DATEPART(WEEKDAY, scheduled_start_at)
ORDER BY
    weekday_number;


-- 7. No-show rate by booking lead-time band
-- Management question:
-- How does the time between booking and the scheduled appointment
-- correspond to the synthetic no-show rate?

WITH AppointmentLeadTime AS (
    SELECT
        appointment_id,
        status,
        CAST(
            DATEDIFF(
                MINUTE,
                booked_at,
                scheduled_start_at
            ) / 1440.0
            AS DECIMAL(10, 2)
        ) AS booking_lead_time_days
    FROM dbo.Appointments
),
LeadTimeBands AS (
    SELECT
        appointment_id,
        status,
        booking_lead_time_days,
        CASE
            WHEN booking_lead_time_days < 1
                THEN 'Same day'
            WHEN booking_lead_time_days < 4
                THEN '1-3 days'
            WHEN booking_lead_time_days < 8
                THEN '4-7 days'
            WHEN booking_lead_time_days < 15
                THEN '8-14 days'
            WHEN booking_lead_time_days < 31
                THEN '15-30 days'
            ELSE '31+ days'
        END AS booking_lead_time_band,
        CASE
            WHEN booking_lead_time_days < 1 THEN 1
            WHEN booking_lead_time_days < 4 THEN 2
            WHEN booking_lead_time_days < 8 THEN 3
            WHEN booking_lead_time_days < 15 THEN 4
            WHEN booking_lead_time_days < 31 THEN 5
            ELSE 6
        END AS booking_lead_time_sort
    FROM AppointmentLeadTime
)
SELECT
    booking_lead_time_band,
    booking_lead_time_sort,
    COUNT(*) AS total_appointments,
    CAST(
        AVG(booking_lead_time_days)
        AS DECIMAL(10, 2)
    ) AS average_booking_lead_time_days,
    SUM(
        CASE
            WHEN status = 'no_show'
                THEN 1
            ELSE 0
        END
    ) AS no_show_count,
    CAST(
        100.0
            * SUM(
                CASE
                    WHEN status = 'no_show'
                        THEN 1
                    ELSE 0
                END
              )
            / NULLIF(COUNT(*), 0)
        AS DECIMAL(6, 2)
    ) AS no_show_rate_percentage
FROM LeadTimeBands
GROUP BY
    booking_lead_time_band,
    booking_lead_time_sort
ORDER BY
    booking_lead_time_sort;


-- 8. Revenue efficiency by procedure group
-- Management question:
-- Which procedure groups generate the highest net revenue
-- and direct margin per allocated clinical chair hour?

WITH ProcedureWeights AS (
    SELECT
        ap.appointment_procedure_id,
        ap.appointment_id,
        ap.procedure_code,
        ap.quantity,
        ap.fee_amount,
        ap.discount_amount,
        ap.direct_cost,
        pc.procedure_group,
        pc.default_planned_duration_min * ap.quantity
            AS procedure_duration_weight,
        SUM(
            pc.default_planned_duration_min * ap.quantity
        ) OVER (
            PARTITION BY ap.appointment_id
        ) AS appointment_duration_weight,
        DATEDIFF(
            MINUTE,
            a.chair_start_at,
            a.chair_end_at
        ) AS appointment_actual_chair_minutes
    FROM dbo.AppointmentProcedures AS ap
    INNER JOIN dbo.ProcedureCatalog AS pc
        ON pc.procedure_code = ap.procedure_code
    INNER JOIN dbo.Appointments AS a
        ON a.appointment_id = ap.appointment_id
    WHERE
        a.status = 'completed'
        AND a.chair_start_at IS NOT NULL
        AND a.chair_end_at IS NOT NULL
),
AllocatedProcedures AS (
    SELECT
        appointment_procedure_id,
        procedure_group,
        fee_amount - discount_amount AS net_procedure_revenue,
        fee_amount - discount_amount - direct_cost AS direct_margin,
        appointment_actual_chair_minutes
            * 1.0 * procedure_duration_weight
            / NULLIF(appointment_duration_weight, 0)
            AS allocated_chair_minutes
    FROM ProcedureWeights
)
SELECT
    procedure_group,
    COUNT(*) AS procedure_count,
    CAST(
        SUM(allocated_chair_minutes) / 60.0
        AS DECIMAL(12, 2)
    ) AS allocated_chair_hours,
    CAST(
        SUM(net_procedure_revenue)
        AS DECIMAL(16, 2)
    ) AS net_procedure_revenue,
    CAST(
        SUM(direct_margin)
        AS DECIMAL(16, 2)
    ) AS direct_margin,
    CAST(
        SUM(net_procedure_revenue)
            / NULLIF(SUM(allocated_chair_minutes) / 60.0, 0)
        AS DECIMAL(16, 2)
    ) AS revenue_per_allocated_chair_hour,
    CAST(
        SUM(direct_margin)
            / NULLIF(SUM(allocated_chair_minutes) / 60.0, 0)
        AS DECIMAL(16, 2)
    ) AS direct_margin_per_allocated_chair_hour
FROM AllocatedProcedures
GROUP BY procedure_group
ORDER BY revenue_per_allocated_chair_hour DESC;


-- 9. Treatment-plan acceptance by patient insurance type
-- Management question:
-- How does treatment-plan item acceptance vary across
-- synthetic patient insurance groups?

WITH InsuranceAcceptance AS (
    SELECT
        p.insurance_type,
        COUNT(DISTINCT tp.plan_id) AS plan_count,
        COUNT(*) AS proposed_item_count,
        SUM(
            CASE
                WHEN tpi.decision_status IN (
                    'accepted',
                    'declined',
                    'deferred'
                )
                    THEN 1
                ELSE 0
            END
        ) AS decided_item_count,
        SUM(
            CASE
                WHEN tpi.decision_status = 'accepted'
                    THEN 1
                ELSE 0
            END
        ) AS accepted_item_count,
        SUM(
            tpi.proposed_fee_amount
                - tpi.proposed_discount_amount
        ) AS proposed_value,
        SUM(
            CASE
                WHEN tpi.decision_status = 'accepted'
                    THEN (
                        tpi.proposed_fee_amount
                            - tpi.proposed_discount_amount
                    )
                ELSE 0
            END
        ) AS accepted_value
    FROM dbo.TreatmentPlans AS tp
    INNER JOIN dbo.TreatmentPlanItems AS tpi
        ON tpi.plan_id = tp.plan_id
    INNER JOIN dbo.Patients AS p
        ON p.patient_id = tp.patient_id
    GROUP BY
        p.insurance_type
)
SELECT
    insurance_type,
    plan_count,
    proposed_item_count,
    decided_item_count,
    accepted_item_count,
    CAST(
        100.0 * accepted_item_count
            / NULLIF(decided_item_count, 0)
        AS DECIMAL(6, 2)
    ) AS decided_item_acceptance_rate_percentage,
    CAST(
        proposed_value
        AS DECIMAL(16, 2)
    ) AS proposed_value,
    CAST(
        accepted_value
        AS DECIMAL(16, 2)
    ) AS accepted_value,
    CAST(
        100.0 * accepted_value
            / NULLIF(proposed_value, 0)
        AS DECIMAL(6, 2)
    ) AS proposed_value_acceptance_rate_percentage
FROM InsuranceAcceptance
ORDER BY
    decided_item_acceptance_rate_percentage DESC,
    insurance_type;


-- 10. Operational and financial performance by referral source
-- Management question:
-- Which synthetic referral sources correspond to stronger appointment,
-- financial, and treatment-plan outcomes?

WITH ReferralSources AS (
    SELECT
        referral_source,
        COUNT(*) AS patient_count
    FROM dbo.Patients
    GROUP BY referral_source
),
AppointmentPerformance AS (
    SELECT
        p.referral_source,
        COUNT(*) AS appointment_count,
        SUM(
            CASE
                WHEN a.status = 'completed'
                    THEN 1
                ELSE 0
            END
        ) AS completed_appointment_count,
        SUM(
            CASE
                WHEN a.status = 'no_show'
                    THEN 1
                ELSE 0
            END
        ) AS no_show_count,
        SUM(
            CASE
                WHEN a.status = 'cancelled'
                    THEN 1
                ELSE 0
            END
        ) AS cancelled_count
    FROM dbo.Appointments AS a
    INNER JOIN dbo.Patients AS p
        ON p.patient_id = a.patient_id
    GROUP BY p.referral_source
),
ProcedurePerformance AS (
    SELECT
        p.referral_source,
        COUNT(*) AS procedure_count,
        SUM(
            ap.fee_amount
                - ap.discount_amount
        ) AS net_procedure_revenue,
        SUM(
            ap.fee_amount
                - ap.discount_amount
                - ap.direct_cost
        ) AS direct_margin
    FROM dbo.AppointmentProcedures AS ap
    INNER JOIN dbo.Appointments AS a
        ON a.appointment_id = ap.appointment_id
    INNER JOIN dbo.Patients AS p
        ON p.patient_id = a.patient_id
    GROUP BY p.referral_source
),
TreatmentPlanPerformance AS (
    SELECT
        p.referral_source,
        SUM(
            CASE
                WHEN tpi.decision_status IN (
                    'accepted',
                    'declined',
                    'deferred'
                )
                    THEN 1
                ELSE 0
            END
        ) AS decided_item_count,
        SUM(
            CASE
                WHEN tpi.decision_status = 'accepted'
                    THEN 1
                ELSE 0
            END
        ) AS accepted_item_count
    FROM dbo.TreatmentPlans AS tp
    INNER JOIN dbo.TreatmentPlanItems AS tpi
        ON tpi.plan_id = tp.plan_id
    INNER JOIN dbo.Patients AS p
        ON p.patient_id = tp.patient_id
    GROUP BY p.referral_source
)
SELECT
    rs.referral_source,
    rs.patient_count,
    COALESCE(a.appointment_count, 0) AS appointment_count,
    COALESCE(a.completed_appointment_count, 0)
        AS completed_appointment_count,
    COALESCE(a.no_show_count, 0) AS no_show_count,
    CAST(
        100.0 * COALESCE(a.no_show_count, 0)
            / NULLIF(a.appointment_count, 0)
        AS DECIMAL(6, 2)
    ) AS no_show_rate_percentage,
    COALESCE(a.cancelled_count, 0) AS cancelled_count,
    CAST(
        100.0 * COALESCE(a.cancelled_count, 0)
            / NULLIF(a.appointment_count, 0)
        AS DECIMAL(6, 2)
    ) AS cancellation_rate_percentage,
    COALESCE(pr.procedure_count, 0) AS procedure_count,
    CAST(
        COALESCE(pr.net_procedure_revenue, 0)
        AS DECIMAL(16, 2)
    ) AS net_procedure_revenue,
    CAST(
        COALESCE(pr.direct_margin, 0)
        AS DECIMAL(16, 2)
    ) AS direct_margin,
    CAST(
        COALESCE(pr.net_procedure_revenue, 0)
            / NULLIF(rs.patient_count, 0)
        AS DECIMAL(16, 2)
    ) AS revenue_per_registered_patient,
    COALESCE(tp.decided_item_count, 0) AS decided_item_count,
    COALESCE(tp.accepted_item_count, 0) AS accepted_item_count,
    CAST(
        100.0 * COALESCE(tp.accepted_item_count, 0)
            / NULLIF(tp.decided_item_count, 0)
        AS DECIMAL(6, 2)
    ) AS treatment_plan_acceptance_rate_percentage
FROM ReferralSources AS rs
LEFT JOIN AppointmentPerformance AS a
    ON a.referral_source = rs.referral_source
LEFT JOIN ProcedurePerformance AS pr
    ON pr.referral_source = rs.referral_source
LEFT JOIN TreatmentPlanPerformance AS tp
    ON tp.referral_source = rs.referral_source
ORDER BY
    net_procedure_revenue DESC,
    rs.referral_source;