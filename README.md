# Dental Clinic Operations Analytics

A portfolio project demonstrating how SQL Server, Python, pandas, and Power BI can support operational and financial decision-making in a dental clinic.

The project uses only reproducible synthetic data and contains no real patient information.

## Project status

Version 0.5 - normalized source model, reproducible synthetic data,
SQL Server workflow, exploratory analysis, validated processed datasets,
and a validated Power BI semantic model completed.

## Business problem

Dental clinics often store appointment, treatment, procedure, and payment information across disconnected systems.

This fragmentation makes it difficult to answer operational questions such as:

- How frequently do patients cancel or miss appointments?
- Are appointment reminders associated with lower no-show rates?
- How much clinical chair time does each dentist deliver?
- Which procedure groups generate the highest revenue and direct margin?
- What proportion of proposed treatment is accepted?
- How effectively are payments allocated to completed procedures?

This project creates an integrated analytical dataset for investigating these questions.

## Current capabilities

The repository currently supports:

- A normalized nine-table relational data model
- Reproducible synthetic data generation
- Automated data-quality and relationship validation
- SQL Server table and constraint creation
- Transactional loading of CSV data into SQL Server
- Row-count validation after database loading
- Core operational and financial SQL queries
- Treatment-plan-to-procedure linkage
- Payment-to-procedure allocation analysis
- A reproducible processed-data build for Power BI
- Four conformed dimensions and five analytical fact tables
- Chair-time, revenue, payment, and treatment-plan reconciliation
- Post-write validation of processed CSV names, columns, and row counts

## Data model

The database contains nine primary tables:

1. `Patients`
2. `Dentists`
3. `Appointments`
4. `ProcedureCatalog`
5. `AppointmentProcedures`
6. `TreatmentPlans`
7. `TreatmentPlanItems`
8. `Payments`
9. `PaymentAllocations`

Detailed field definitions and relationships are documented in:

```text
docs/data_dictionary.md
```

The processed analytical model, Power BI relationships, grains,
derived measures, and double-counting rules are documented in:

```text
docs/processed_data_model.md
```

## Default synthetic dataset

The default generator currently produces:

| Dataset | Rows |
|---|---:|
| Patients | 2,000 |
| Dentists | 7 |
| Appointments | 8,000 |
| Procedure catalog | 24 |
| Appointment procedures | 8,378 |
| Treatment plans | 1,775 |
| Treatment plan items | 3,596 |
| Payments | 7,973 |
| Payment allocations | 9,616 |

Because the random seed is fixed, rerunning the generator produces the same datasets.

## Core analytical questions

The current SQL queries examine:

- Appointment status distribution
- No-show rate by reminder status
- Monthly chair-time performance by dentist
- Revenue and direct margin by procedure group
- Treatment-plan acceptance by item count and proposed value

Additional analysis will cover patient retention, payment collection, utilization, procedure mix, and revenue per clinical hour.

## Technology stack

- Python 3.12
- pandas
- NumPy
- pyodbc
- Microsoft SQL Server
- SQL Server ODBC Driver 17
- Power BI
- Jupyter Notebook
- Git and GitHub

## Repository structure

```text
.
|-- data/
|   |-- raw/
|   `-- processed/
|-- docs/
|   |-- data_dictionary.md
|   |-- processed_data_model.md
|   `-- project_charter.md
|-- images/
|-- notebooks/
|   `-- 01_eda.ipynb
|-- powerbi/
|   `-- README.md
|-- sql/
|   |-- 01_schema.sql
|   `-- 02_analytics_queries.sql
|-- src/
|   |-- build_processed_datasets.py
|   |-- generate_synthetic_data.py
|   `-- load_csv_to_sql_server.py
|-- .gitignore
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Quick start

### 1. Create and activate the Python environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Generate the synthetic datasets

```powershell
python src\generate_synthetic_data.py
```

The generated CSV files are written to:

```text
data/raw/
```

### 3. Build the processed analytical datasets

```powershell
python src\build_processed_datasets.py
```

The build creates four conformed dimensions and five analytical fact
tables for direct import into Power BI. It validates keys, row counts,
relationships, appointment and procedure chair time, procedure
revenue, payment allocations, treatment-plan linkage, net cash, and
the written CSV structure.

The processed files are written to:

```text
data/processed/
```

### 4. Create the SQL Server test database

The following commands use Windows integrated authentication:

```powershell
sqlcmd -S localhost -E -Q "IF DB_ID('DentalClinicAnalytics_Test') IS NULL CREATE DATABASE DentalClinicAnalytics_Test;"
```

### 5. Create the database schema

```powershell
sqlcmd -S localhost -E -d DentalClinicAnalytics_Test -b -i sql\01_schema.sql
```

The schema script creates all tables, primary keys, foreign keys, validation constraints, and indexes.

### 6. Load the CSV data into SQL Server

```powershell
python src\load_csv_to_sql_server.py
```

The loader:

- Reads all nine CSV files
- Converts values to database-compatible types
- Loads tables in dependency order
- Uses a single database transaction
- Rolls back changes if loading fails
- Verifies database row counts before committing

A different server, database, driver, or data directory can be supplied through command-line arguments:

```powershell
python src\load_csv_to_sql_server.py --help
```

### 7. Run the analytical SQL queries

```powershell
sqlcmd -S localhost -E -d DentalClinicAnalytics_Test -b -i sql\02_analytics_queries.sql
```

## Data integrity

The project validates several important relationships, including:

- Every appointment belongs to an existing patient and dentist
- Every performed procedure uses a valid procedure code
- Treatment-plan items belong to valid treatment plans
- Performed procedures can be linked to accepted treatment-plan items
- Payments belong to valid patients
- Payment allocations link valid payments to performed procedures
- Duplicate non-null payment reference codes are prohibited

## Ethics and limitations

- All records in this repository are synthetic.
- No real patient, dentist, or clinic data are included.
- The project is intended for education and portfolio demonstration.
- It must not be used to support clinical decisions.
- Results generated from synthetic data cannot be generalized to real dental clinics.
- Relationships in the synthetic data represent designed scenarios rather than causal evidence.

## Roadmap

- [x] Define the project scope and business questions
- [x] Design the normalized relational data model
- [x] Document the data dictionary
- [x] Generate reproducible synthetic datasets
- [x] Validate referential integrity
- [x] Create the SQL Server schema
- [x] Build the SQL Server data-loading workflow
- [x] Implement the first core analytical queries
- [ ] Expand the analytical SQL query library
- [x] Complete exploratory data analysis with Python
- [x] Create processed analytical datasets
- [x] Build the Power BI data model
- [ ] Develop the first Power BI dashboard
- [ ] Document findings and management recommendations
