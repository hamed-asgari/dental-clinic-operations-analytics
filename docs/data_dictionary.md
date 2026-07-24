# Data Dictionary - Draft 0.2

Review every field before generating the final dataset. Add clinical or operational fields only when they answer a defined question.

## Design principles

- All records in this project are fully synthetic and do not represent real patients, dentists, clinics, treatments, or financial transactions.
- The model represents one medium-sized outpatient dental clinic with multiple dentists and visiting specialists.
- One appointment may contain multiple completed procedures.
- Procedure codes must be reusable and must refer to a separate procedure catalogue.
- A treatment plan may contain multiple treatment-plan items.
- Treatment-plan acceptance must be measurable both at the total-plan level and at the individual-item level.
- A payment may be allocated across one or more completed procedures, while deposits and advance payments may remain temporarily unallocated.
- Operational metrics such as waiting time and actual appointment duration should be calculated from timestamps whenever possible.
- Only fields that support a defined analytical or managerial question should be included.

## patients.csv

| Column | Type | Description |
|---|---|---|
| patient_id | integer | Unique synthetic patient identifier |
| birth_year | integer | Synthetic year of birth used to derive approximate age |
| sex | category | Female, male, or other/unknown synthetic category |
| city_area | category | Synthetic city or service area |
| registered_at | datetime | Date and time when the patient was first registered |
| insurance_type | category | Self-pay, basic insurance, supplementary insurance, or mixed |
| referral_source | category | Existing-patient referral, dentist referral, online search, social media, walk-in, advertising, or other |
| preferred_contact_channel | category | Phone call, SMS, messaging application, email, or other |
| patient_status | category | Active, inactive, or archived |

### Derived patient metrics

The following variables should be calculated during analysis:

- Approximate age at appointment
- Time from registration to first completed appointment
- Number of completed appointments per patient
- Patient retention indicator
- Repeat-visit rate
- No-show rate per patient
- Cancellation rate per patient
- Lifetime net procedure revenue
- Outstanding balance per patient
- Treatment-plan acceptance rate per patient
- Patient distribution by referral source
- Patient distribution by city area

## dentists.csv

| Column | Type | Description |
|---|---|---|
| dentist_id | integer | Unique dentist identifier |
| dentist_role | category | General dentist, endodontist, periodontist, oral surgeon, orthodontist, pediatric dentist, prosthodontist, or other |
| engagement_type | category | Employee, contractor, or visiting specialist |
| start_date | date | Date when the dentist started working at the clinic |
| end_date | date, nullable | Date when the dentist stopped working at the clinic |
| scheduled_hours_weekly | numeric | Typical scheduled clinical hours per week |
| active | boolean | Whether the dentist currently works at the clinic |

### Derived dentist metrics

The following variables should be calculated during analysis:

- Completed appointments per dentist
- Actual chair hours per dentist
- Scheduled-hours utilization
- Net procedure revenue per dentist
- Gross margin per dentist
- Revenue per actual chair hour
- Procedure mix per dentist
- No-show rate per dentist
- Cancellation rate per dentist
- Average patient waiting time per dentist
- Average schedule variance per dentist
- Treatment-plan acceptance rate per dentist
- Treatment-plan completion rate per dentist

## appointments.csv

| Column | Type | Description |
|---|---|---|
| appointment_id | integer | Unique appointment identifier |
| patient_id | integer | Foreign key to patients |
| dentist_id | integer | Foreign key to dentists |
| booked_at | datetime | Date and time when the appointment was created |
| scheduled_start_at | datetime | Scheduled appointment start date and time |
| planned_duration_min | integer | Planned chair time in minutes |
| visit_type | category | New-patient examination, recall examination, consultation, treatment, emergency, or follow-up |
| booking_channel | category | Phone, in-person, online, referral, or other |
| status | category | Scheduled, completed, cancelled, no-show, or rescheduled |
| status_updated_at | datetime, nullable | Date and time when the appointment status was last changed |
| reminder_sent | boolean | Whether at least one appointment reminder was sent |
| check_in_at | datetime, nullable | Time the patient arrived and checked in |
| chair_start_at | datetime, nullable | Time the patient was seated and clinical care began |
| chair_end_at | datetime, nullable | Time the clinical visit ended |
| checkout_at | datetime, nullable | Time the patient completed checkout |
| status_change_reason | category, nullable | Reason recorded for a cancelled or rescheduled appointment |
| rescheduled_from_appointment_id | integer, nullable | Self-referencing identifier of the original appointment when this appointment is a replacement |

### Derived appointment metrics

The following variables should be calculated during analysis rather than stored directly in the raw appointment table:

- Booking lead time = scheduled start time minus booking time
- Patient waiting time = chair start time minus check-in time
- Actual chair time = chair end time minus chair start time
- Checkout delay = checkout time minus chair end time
- Schedule variance = actual chair time minus planned duration
- No-show indicator derived from appointment status
- Cancellation indicator derived from appointment status
- Cancellation or rescheduling notice time = scheduled start time minus status update time

## procedure_catalog.csv

| Column | Type | Description |
|---|---|---|
| procedure_code | string | Unique reusable procedure code |
| procedure_name | string | Standard name of the dental procedure |
| procedure_group | category | Diagnostic, preventive, restorative, endodontic, periodontal, surgical, prosthodontic, orthodontic, pediatric, or other |
| default_planned_duration_min | integer | Default planned chair time for the procedure |
| standard_fee_amount | numeric | Synthetic standard fee before appointment-specific adjustments |
| standard_direct_cost | numeric | Synthetic standard direct material or laboratory cost |
| active | boolean | Whether the procedure is currently available in the clinic |

## appointment_procedures.csv

| Column | Type | Description |
|---|---|---|
| appointment_procedure_id | integer | Unique identifier for a procedure performed during an appointment |
| appointment_id | integer | Foreign key to appointments |
| plan_item_id | integer, nullable | Foreign key to the originating treatment-plan item when applicable |
| procedure_code | string | Foreign key to the procedure catalogue |
| tooth_code | string, nullable | Synthetic tooth identifier using FDI notation when applicable |
| quantity | integer | Number of units of the procedure performed |
| completion_status | category | Completed, partially completed, or discontinued |
| fee_amount | numeric | Synthetic amount charged for this procedure |
| discount_amount | numeric | Synthetic discount applied to this procedure |
| direct_cost | numeric | Synthetic direct material or laboratory cost |

### Derived procedure metrics

The following variables should be calculated during analysis:

- Net procedure revenue = fee amount minus discount amount
- Gross margin = net procedure revenue minus direct cost
- Total procedure revenue per appointment
- Total direct cost per appointment
- Revenue per actual chair minute
- Procedure volume by procedure group
- Procedure mix by dentist
- Difference between the charged fee and the catalogue standard fee

## treatment_plans.csv

| Column | Type | Description |
|---|---|---|
| plan_id | integer | Unique treatment-plan identifier |
| patient_id | integer | Foreign key to patients |
| proposed_by_dentist_id | integer | Foreign key to the dentist who proposed the treatment plan |
| source_appointment_id | integer, nullable | Foreign key to the appointment during which the plan was proposed |
| proposed_at | datetime | Date and time when the treatment plan was presented |
| plan_status | category | Draft, presented, partially accepted, fully accepted, declined, expired, or closed |
| valid_until | date, nullable | Optional date until which the proposed prices or conditions remain valid |

## treatment_plan_items.csv

| Column | Type | Description |
|---|---|---|
| plan_item_id | integer | Unique treatment-plan item identifier |
| plan_id | integer | Foreign key to treatment plans |
| procedure_code | string | Foreign key to the procedure catalogue |
| tooth_code | string, nullable | Synthetic tooth identifier using FDI notation when applicable |
| sequence_order | integer | Suggested order of the item within the treatment plan |
| priority_level | category | Urgent, short-term, elective, or maintenance |
| proposed_quantity | integer | Number of proposed units |
| proposed_fee_amount | numeric | Synthetic proposed fee before discount |
| proposed_discount_amount | numeric | Synthetic discount proposed for the item |
| decision_status | category | Pending, accepted, declined, or deferred |
| decision_at | datetime, nullable | Date and time when the patient decision was recorded |

### Derived treatment-plan metrics

The following variables should be calculated during analysis:

- Net proposed item value = proposed fee amount minus proposed discount amount
- Total proposed plan value = sum of net proposed values for all plan items
- Accepted plan value = sum of net proposed values for accepted items
- Plan acceptance rate by value = accepted plan value divided by total proposed plan value
- Plan acceptance rate by item count
- Time to patient decision = decision time minus proposal time
- Time from acceptance to first completed procedure
- Accepted-item completion rate
- Proposed versus completed value
- Acceptance rate by procedure group
- Acceptance rate by dentist
- Acceptance rate by patient referral source

## payments.csv

| Column | Type | Description |
|---|---|---|
| payment_id | integer | Unique payment transaction identifier |
| patient_id | integer | Foreign key to patients |
| received_at | datetime | Date and time when the transaction was recorded |
| transaction_type | category | Payment, deposit, or refund |
| payment_arrangement | category | Full payment, partial payment, installment, or not applicable |
| payment_method | category | Cash, card, bank transfer, online payment, or other |
| amount | numeric | Positive synthetic transaction amount |
| payment_status | category | Completed, pending, failed, cancelled, or reversed |
| reference_code | string, nullable | Synthetic transaction or receipt reference |
| notes | string, nullable | Optional non-clinical explanation of the transaction |

## payment_allocations.csv

| Column | Type | Description |
|---|---|---|
| allocation_id | integer | Unique payment-allocation identifier |
| payment_id | integer | Foreign key to payments |
| appointment_procedure_id | integer | Foreign key to the completed appointment procedure |
| allocated_amount | numeric | Portion of the payment allocated to the procedure |

### Derived payment metrics

The following variables should be calculated during analysis:

- Total payments received
- Total refunds
- Net cash received = completed payments minus completed refunds
- Unallocated payment amount
- Amount paid per completed procedure
- Outstanding balance per completed procedure
- Outstanding balance per patient
- Collection rate = allocated completed payments divided by net procedure revenue
- Average time from procedure completion to payment
- Payment-method distribution
- Installment-payment share

## Data integrity and validation rules

- Every appointment must reference an existing patient and dentist.
- The scheduled appointment time must not precede the booking time.
- Check-in, chair-start, chair-end, and checkout timestamps must follow a logical chronological order.
- Cancelled and rescheduled appointments should have a status-update timestamp.
- Only completed appointments may contain completed appointment procedures.
- Every appointment procedure must reference an active or historically valid procedure code.
- A treatment-plan item decision time must not precede the treatment-plan proposal time.
- A completed procedure linked to a treatment-plan item must match the procedure code of that item.
- Payment, deposit, and refund amounts must be positive; their financial direction is determined by transaction type.
- The sum of allocations for a payment must not exceed the completed transaction amount.
- An allocation must reference a completed appointment procedure.
- All personally identifiable information is excluded because the dataset is fully synthetic.