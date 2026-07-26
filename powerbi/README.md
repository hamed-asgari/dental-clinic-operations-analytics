# Power BI dashboard plan

## Current status

The processed analytical datasets are complete and validated. The
Power BI semantic model and dashboard have not been built yet.

Rebuild the Power BI source files with:

```powershell
python src\build_processed_datasets.py
```

Import all nine CSV files from:

```text
data/processed/
```

The required grains, relationships, active and role-playing date
keys, measure ownership, and double-counting rules are documented in:

```text
docs/processed_data_model.md
```

## Modeling guardrails

- Use one-to-many, single-direction relationships from dimensions to
  facts.
- Do not create direct relationships between fact tables.
- Use the recommended active date relationship for each fact and keep
  other date roles inactive unless separate date dimensions are
  created.
- Calculate ratios from aggregated numerators and denominators.
- Use `fact_appointments` for full appointment chair time.
- Use `fact_procedures` for allocated procedure chair time and
  procedure revenue.
- Use `fact_payments` for cash and refunds.
- Use `fact_payment_allocations` for collection timing and
  allocation-level analysis.
- Do not call appointment non-completion true capacity utilization.
  The data contains typical weekly dentist hours, not a detailed chair
  availability schedule.

## Planned dashboard pages

Create three pages:

## 1. Executive overview
- Appointments
- Completed visits
- No-show rate
- Cancellation rate
- Net procedure revenue
- Net procedure revenue per actual chair hour

## 2. Scheduling and capacity
- Appointment status by month
- No-show by weekday and hour
- Planned versus actual duration
- Actual chair hours by dentist
- Scheduled-hours utilization estimate by dentist
- Lead time and no-show relationship

## 3. Treatment and finance
- Procedure mix
- Revenue and direct margin by procedure group
- Treatment-plan acceptance
- Payment collection rate based on allocated completed inflows
- Referral-source performance

Export dashboard screenshots to `images/` before publishing the repository.
