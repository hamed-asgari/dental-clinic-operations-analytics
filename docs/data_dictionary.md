# Data Dictionary - Draft 0.1

Review every field before generating the final dataset. Add clinical or operational fields only when they answer a defined question.

## patients.csv
| Column | Type | Description |
|---|---|---|
| patient_id | integer | Synthetic unique patient identifier |
| birth_year | integer | Synthetic year of birth |
| sex | category | Synthetic sex category |
| city | category | Synthetic city/area |
| registration_date | date | First registration date |
| insurance_type | category | Self-pay, basic, supplementary |
| referral_source | category | Search, referral, social media, walk-in, other |

## dentists.csv
| Column | Type | Description |
|---|---|---|
| dentist_id | integer | Dentist identifier |
| dentist_role | category | General dentist or defined clinical role |
| start_date | date | Start date in the clinic |
| scheduled_hours_weekly | numeric | Scheduled clinical hours per week |

## appointments.csv
| Column | Type | Description |
|---|---|---|
| appointment_id | integer | Appointment identifier |
| patient_id | integer | Foreign key to patients |
| dentist_id | integer | Foreign key to dentists |
| appointment_datetime | datetime | Scheduled date and time |
| booked_date | date | Date appointment was created |
| appointment_type | category | Examination, restorative, endodontic, surgery, hygiene, other |
| planned_duration_min | integer | Planned chair time |
| status | category | Completed, cancelled, no-show, rescheduled |
| reminder_sent | boolean | Whether a reminder was sent |
| wait_time_min | integer | Waiting time for completed visits |

## procedures.csv
| Column | Type | Description |
|---|---|---|
| procedure_id | integer | Procedure record identifier |
| appointment_id | integer | Foreign key to appointments |
| procedure_code | category | Synthetic procedure code |
| procedure_group | category | Diagnostic, preventive, restorative, endodontic, surgical, prosthetic |
| actual_duration_min | integer | Actual clinical duration |
| fee_amount | numeric | Synthetic fee amount |
| direct_cost | numeric | Synthetic direct cost |

## treatment_plans.csv
| Column | Type | Description |
|---|---|---|
| plan_id | integer | Treatment-plan identifier |
| patient_id | integer | Foreign key to patients |
| proposed_date | date | Plan proposal date |
| total_value | numeric | Synthetic total treatment value |
| accepted_value | numeric | Accepted portion of plan |
| plan_status | category | Fully accepted, partially accepted, declined, pending |

## payments.csv
| Column | Type | Description |
|---|---|---|
| payment_id | integer | Payment identifier |
| patient_id | integer | Foreign key to patients |
| appointment_id | integer | Optional foreign key to appointment |
| payment_date | date | Payment date |
| amount | numeric | Synthetic payment amount |
| payment_method | category | Cash, card, transfer, installment |
