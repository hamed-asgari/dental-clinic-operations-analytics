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
-- What share of proposed treatment value and treatment items
-- is accepted by patients?

WITH PlanValues AS (SELECT tp.plan_id,
                           tp.plan_status,
                           COUNT(*) AS proposed_item_count,
                           SUM(
                                   CASE
                                       WHEN tpi.decision_status = 'accepted'
                                           THEN 1
                                       ELSE 0
                                       END
                           )        AS accepted_item_count,
                           SUM(
                                   tpi.proposed_fee_amount
                                       - tpi.proposed_discount_amount
                           )        AS proposed_value,
                           SUM(
                                   CASE
                                       WHEN tpi.decision_status = 'accepted'
                                           THEN (
                                           tpi.proposed_fee_amount
                                               - tpi.proposed_discount_amount
                                           )
                                       ELSE 0
                                       END
                           )        AS accepted_value
                    FROM dbo.TreatmentPlans AS tp
                             INNER JOIN dbo.TreatmentPlanItems AS tpi
                                        ON tpi.plan_id = tp.plan_id
                    GROUP BY tp.plan_id,
                             tp.plan_status)
SELECT plan_status,
       COUNT(*)                 AS plan_count,
       SUM(proposed_item_count) AS proposed_item_count,
       SUM(accepted_item_count) AS accepted_item_count,
       CAST(
               100.0
                   * SUM(accepted_item_count)
                   / NULLIF(
                       SUM(proposed_item_count),
                       0
                     )
           AS DECIMAL(6, 2)
       )                        AS item_acceptance_rate_percentage,
       CAST(
               SUM(proposed_value)
           AS DECIMAL(16, 2)
       )                        AS proposed_value,
       CAST(
               SUM(accepted_value)
           AS DECIMAL(16, 2)
       )                        AS accepted_value,
       CAST(
               100.0
                   * SUM(accepted_value)
                   / NULLIF(
                       SUM(proposed_value),
                       0
                     )
           AS DECIMAL(6, 2)
       )                        AS value_acceptance_rate_percentage
FROM PlanValues
GROUP BY plan_status
ORDER BY proposed_value DESC;