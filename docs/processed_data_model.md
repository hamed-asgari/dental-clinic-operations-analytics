# Processed Analytical Data Model

## Purpose

The processed layer is a reproducible Power BI-ready fact
constellation built entirely from the nine synthetic CSV files in
`data/raw/`.

Run:

```powershell
python src\build_processed_datasets.py
```

The script rebuilds every processed CSV, validates the analytical
grains and relationships, reconciles chair time and financial
measures, and reopens the written files to verify their structure.

## Model design

The model uses four conformed dimensions and five fact tables.

| Dataset | Grain | Primary key | Rows |
|---|---|---|---:|
| `dim_date.csv` | One row per calendar date | `date_key` | 1,185 |
| `dim_patients.csv` | One row per patient | `patient_id` | 2,000 |
| `dim_dentists.csv` | One row per dentist | `dentist_id` | 7 |
| `dim_procedures.csv` | One row per procedure code | `procedure_code` | 24 |
| `fact_appointments.csv` | One row per appointment | `appointment_id` | 8,000 |
| `fact_procedures.csv` | One row per performed procedure | `appointment_procedure_id` | 8,378 |
| `fact_treatment_plan_items.csv` | One row per treatment-plan item | `plan_item_id` | 3,596 |
| `fact_payments.csv` | One row per payment transaction | `payment_id` | 7,973 |
| `fact_payment_allocations.csv` | One row per payment allocation | `allocation_id` | 9,616 |

The dimensions filter the facts through one-to-many relationships.
Fact tables should not be connected directly to one another.

## Recommended Power BI relationships

Use single-direction filtering from each dimension to each fact.

### Date relationships

Recommended active relationships:

| Dimension column | Fact column |
|---|---|
| `dim_date[date_key]` | `fact_appointments[appointment_date_key]` |
| `dim_date[date_key]` | `fact_procedures[appointment_date_key]` |
| `dim_date[date_key]` | `fact_treatment_plan_items[proposed_date_key]` |
| `dim_date[date_key]` | `fact_payments[received_date_key]` |
| `dim_date[date_key]` | `fact_payment_allocations[service_date_key]` |

The remaining date keys are role-playing dates. Keep their
relationships inactive unless a dedicated copy of the date dimension
is added:

- `fact_appointments[booked_date_key]`
- `fact_appointments[status_updated_date_key]`
- `fact_treatment_plan_items[decision_date_key]`
- `fact_treatment_plan_items[valid_until_date_key]`
- `fact_treatment_plan_items[first_linked_procedure_date_key]`
- `fact_payment_allocations[payment_received_date_key]`

### Patient relationships

Connect `dim_patients[patient_id]` to:

- `fact_appointments[patient_id]`
- `fact_procedures[patient_id]`
- `fact_treatment_plan_items[patient_id]`
- `fact_payments[patient_id]`
- `fact_payment_allocations[patient_id]`

### Dentist relationships

Connect `dim_dentists[dentist_id]` to:

- `fact_appointments[dentist_id]`
- `fact_procedures[dentist_id]`
- `fact_treatment_plan_items[proposed_by_dentist_id]`
- `fact_payment_allocations[dentist_id]`

### Procedure relationships

Connect `dim_procedures[procedure_code]` to:

- `fact_procedures[procedure_code]`
- `fact_treatment_plan_items[procedure_code]`
- `fact_payment_allocations[procedure_code]`

## Dimension notes

### Date

`dim_date.csv` spans every date from the earliest to the latest
non-null date found across the raw datasets. It has no gaps.

Important columns:

- `date_key`: Integer key in `YYYYMMDD` format.
- `date`: ISO calendar date.
- `year`, `quarter_number`, and `quarter`.
- `month_number`, `month_name`, and `month_short_name`.
- `year_month` and `year_month_sort`.
- `week_of_year`.
- `day_of_month`, `weekday_number`, and `weekday_name`.

Use the numeric sort columns when sorting month, quarter, and weekday
labels in Power BI.

### Patients, dentists, and procedures

These dimensions retain the documented raw attributes without
duplicating analytical measures. Their field definitions are in
`docs/data_dictionary.md`.

## Fact notes

### Appointments

`fact_appointments.csv` supports appointment volume, status,
scheduling, waiting-time, chair-time, and patient-age analysis.

Important derived columns:

- `appointment_count`: Always 1.
- `completed_appointment_count`, `no_show_count`,
  `cancelled_count`, and `rescheduled_count`: Additive status
  counters.
- `non_completed_count`: 1 for every status other than completed.
- `booking_lead_minutes`: Scheduled start minus booking time.
- `patient_wait_minutes`: Chair start minus check-in.
- `actual_chair_minutes`: Chair end minus chair start.
- `checkout_delay_minutes`: Checkout minus chair end.
- `schedule_variance_minutes`: Actual chair time minus planned
  duration.
- `status_notice_minutes`: Scheduled start minus the status-update
  time for cancelled and rescheduled appointments.
- `approximate_age_at_appointment`: Scheduled year minus birth year.

Actual chair time is stored once per appointment. It must not be
copied to every procedure row.

### Procedures

`fact_procedures.csv` supports procedure mix, revenue, direct margin,
chair-time productivity, and service-level collection analysis.

Important derived columns:

- `procedure_count`: Always 1.
- Procedure-status counters for completed, partially completed, and
  discontinued procedures.
- `linked_to_plan_item_count`: 1 when the procedure is linked to an
  accepted treatment-plan item.
- `duration_weight`: Catalogue default duration multiplied by
  quantity.
- `allocated_chair_minutes`: Appointment chair time allocated among
  its procedures in proportion to duration weight.
- `allocated_chair_hours`: Allocated chair minutes divided by 60.
- `net_revenue`: Fee amount minus discount amount.
- `direct_margin`: Net revenue minus direct cost.
- `standard_fee_total`: Catalogue standard fee multiplied by
  quantity.
- `fee_variance_from_standard`: Charged fee minus standard fee total.
- `allocated_amount_total`: Completed payment and deposit amounts
  allocated to the procedure.
- `outstanding_balance`: Net revenue minus allocated amount.

All procedure completion statuses remain in the financial facts
because each status can contain recorded fee, cost, and allocation
amounts.

Do not average or sum row-level ratios. Revenue per chair hour and
margin percentage should be defined as ratios of aggregated
numerators and denominators in Power BI.

### Treatment-plan items

`fact_treatment_plan_items.csv` supports item- and value-based
acceptance, decision timing, and accepted-item completion.

Important derived columns:

- `plan_item_count`: Always 1.
- Counters for accepted, declined, pending, deferred, and decided
  items.
- `net_proposed_value`: Proposed fee minus proposed discount.
- `accepted_proposed_value`: Net proposed value for accepted items.
- `decided_proposed_value`: Net proposed value for non-pending items.
- `decision_time_days`: Decision time minus proposal time.
- `linked_procedure_count`: Number of performed procedures linked to
  the item.
- `linked_net_revenue`: Net revenue recorded on linked procedures.
- `days_to_first_completed_procedure`: Time from the item decision to
  the first linked completed procedure.
- `accepted_item_completed_count`: 1 when an accepted item has a
  linked completed procedure.

Use a distinct count of `plan_id` for plan-level counts because plan
attributes repeat across their item rows.

### Payments

`fact_payments.csv` supports cash, refund, payment-method, payment
status, and unallocated-deposit analysis.

Important derived columns:

- `transaction_count`: Always 1.
- Counters for completed payments, deposits, and refunds.
- `completed_cash_inflow`: Completed payments and deposits.
- `completed_refund_amount`: Completed refunds as a positive source
  amount.
- `net_cash_amount`: Completed cash inflow minus completed refunds.
- `allocation_count`: Number of allocation rows for the transaction.
- `allocated_amount_total`: Total amount allocated by the
  transaction.
- `unallocated_inflow_amount`: Unallocated portion of completed
  payments and deposits.
- `has_unallocated_inflow_count`: 1 when a completed inflow has a
  remaining unallocated amount.

Pending, failed, cancelled, and reversed transactions retain their
source amount but contribute zero to net cash.

### Payment allocations

`fact_payment_allocations.csv` supports collection analysis across
service, patient, dentist, procedure, payment method, and payment
timing.

Important derived columns:

- `allocation_count`: Always 1.
- `allocated_amount`: The amount at the allocation grain.
- `days_from_procedure_completion_to_payment`: Payment receipt time
  minus procedure completion time.
- `payment_timing_group`: Before procedure completion, same day after
  completion, or after the service date.
- Additive counters for each payment-timing group.

Negative days-to-payment values represent deposits or other payments
received before the procedure was completed. They are valid and
should not be converted to missing values.

## Measure ownership and double-counting rules

- Appointment volume and full appointment chair time belong to
  `fact_appointments`.
- Procedure revenue, direct cost, direct margin, and allocated
  procedure chair time belong to `fact_procedures`.
- Proposed and accepted treatment value belong to
  `fact_treatment_plan_items`.
- Cash inflow, refunds, net cash, and unallocated inflow belong to
  `fact_payments`.
- Allocation timing and allocation-level slicing belong to
  `fact_payment_allocations`.

`allocated_amount_total` is carried in the procedure and payment facts
for convenient reconciliation. `allocated_amount` is also present at
the allocation grain. A visual or measure must use only one of these
sources at a time.

For service-date collection rate, use allocated amount from the
allocation fact divided by net revenue from the procedure fact under
compatible dimension filters.

## Validation benchmark

The default synthetic dataset currently reconciles to:

| Check | Value |
|---|---:|
| Completed appointments | 5,936 |
| Non-completed appointments | 2,064 |
| Actual and allocated chair minutes | 275,569.00 |
| Net procedure revenue | 776,623.23 |
| Allocated completed inflows | 706,056.86 |
| Procedure outstanding balance | 70,566.37 |
| Net cash | 704,745.93 |
| Unallocated completed inflow | 1,467.49 |
| Accepted treatment-plan items | 2,001 |
| Accepted items linked to completed procedures | 113 |
| Decided treatment-plan items | 2,961 |
| Treatment-plan acceptance rate | 67.58% |

The values are synthetic validation benchmarks, not real clinic
performance or market estimates.

## Validation rules

The build fails when any of the following occurs:

- A raw file or expected column is missing.
- A processed primary key is null or duplicated.
- A processed foreign key is orphaned.
- A fact row count differs from its raw grain.
- A required time or amount is non-positive or logically invalid.
- Allocated procedure chair time does not reconcile to appointment
  chair time.
- Net revenue, payment allocation, outstanding balance, or net cash
  does not reconcile.
- A non-accepted treatment-plan item is linked to a performed
  procedure.
- A payment allocation references an ineligible transaction or a
  different patient.
- Written CSV names, columns, or row counts differ from the validated
  in-memory datasets.
