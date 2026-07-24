-- Draft analytics queries. Add interpretation for every result.

-- 1. Appointment status distribution
SELECT status, COUNT(*) AS appointment_count,
       CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS percentage
FROM dbo.Appointments
GROUP BY status
ORDER BY appointment_count DESC;

-- 2. No-show rate by reminder status
SELECT reminder_sent,
       COUNT(*) AS total_appointments,
       SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) AS no_shows,
       CAST(100.0 * SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) / COUNT(*) AS DECIMAL(5,2)) AS no_show_rate
FROM dbo.Appointments
GROUP BY reminder_sent;

-- 3. Completed chair minutes by dentist and month
SELECT dentist_id,
       DATEFROMPARTS(YEAR(appointment_datetime), MONTH(appointment_datetime), 1) AS month_start,
       SUM(CASE WHEN status = 'completed' THEN planned_duration_min ELSE 0 END) AS completed_chair_minutes
FROM dbo.Appointments
GROUP BY dentist_id, DATEFROMPARTS(YEAR(appointment_datetime), MONTH(appointment_datetime), 1)
ORDER BY month_start, dentist_id;

-- 4. Revenue and direct margin by procedure group
SELECT procedure_group,
       SUM(fee_amount) AS gross_revenue,
       SUM(direct_cost) AS direct_cost,
       SUM(fee_amount - direct_cost) AS direct_margin
FROM dbo.Procedures
GROUP BY procedure_group
ORDER BY gross_revenue DESC;

-- 5. Treatment-plan acceptance
SELECT plan_status,
       COUNT(*) AS plan_count,
       SUM(total_value) AS proposed_value,
       SUM(accepted_value) AS accepted_value
FROM dbo.TreatmentPlans
GROUP BY plan_status;

-- TODO: Add at least five more queries and explain the management decision each query supports.
