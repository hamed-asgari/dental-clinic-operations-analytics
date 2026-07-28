# Power BI report

## Current status

The processed analytical datasets, Power BI semantic model, and
three-page Power BI operations report are complete and validated.

The report includes synchronized reporting-period slicers across all
pages and uses Executive Overview as the default landing page.

Rebuild the Power BI source files with:

```powershell
python src\build_processed_datasets.py
```

The semantic model reads all nine processed CSV files from:

```text
data/processed/
```

The required grains, relationships, active and role-playing date
keys, measure ownership, and double-counting rules are documented in:

```text
docs/processed_data_model.md
```

## Open the Power BI project

Open:

```text
powerbi/DentalClinicOperationsAnalytics.pbip
```

Before refreshing the model on another computer, update the
`ProcessedDataPath` Power Query parameter so that it points to the
local `data/processed/` directory.

The semantic model contains:

- Four conformed dimensions
- Five analytical fact tables
- One dedicated measures table
- Twenty-three validated relationships
- Twenty-five validated DAX measures
- A marked date table with configured sort columns

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

## Report pages

Each report page uses a consistent 16:9 layout with a page title,
subtitle, synchronized reporting-period slicer, six KPI cards, and four
analytical charts.

### 1. Executive Overview

- Appointments and completed visits
- No-show and cancellation rates
- Net procedure revenue
- Revenue per actual chair hour
- Appointment and net-revenue trends
- No-show and cancellation trends
- Top procedure groups by net revenue

### 2. Scheduling & Capacity

- Appointments and completed visits
- No-show and cancellation rates
- Planned and actual chair hours
- Appointment volume trend
- Planned versus actual chair-hour trend
- No-show and cancellation trends
- Appointment volume by weekday

### 3. Treatment & Finance

- Procedure volume
- Treatment-plan acceptance rate
- Payment collection rate
- Direct margin and net procedure revenue
- Revenue per allocated procedure chair hour
- Procedure-volume and net-revenue trends
- Procedure-group revenue and chair-hour efficiency comparisons

## Cross-page behavior

- The reporting-period slicer is synchronized across all three pages.
- Filter selections remain active while navigating between pages.
- Executive Overview is configured as the default landing page.
- All pages use a consistent visual design system and report layout.

## Modeling notes

- Appointment-level chair hours are used for clinic-wide operational
  efficiency.
- Allocated procedure chair hours are used for procedure-group revenue
  efficiency.
- Payment collection is calculated from allocated completed inflows.
- Scheduled-hours utilization remains an estimate because the source
  data does not contain a detailed chair-availability schedule.

Report screenshots should be exported to `../images/` before the final
portfolio release.
