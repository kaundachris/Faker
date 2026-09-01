# Kaunda Ltd — Dummy MSME Lending Database

A practice project: a synthetic dataset for a fictional Kenyan MSME
lender, built to practice SQL schema design and Excel/Power Query
dashboarding ahead of a Strategy Finance Specialist role that requires
both.

## Problem / motivation

The target role requires building automatic Excel dashboards and
PowerPoint investor reports from data housed in Lightdash, which
typically sits on top of a Postgres/BigQuery/Snowflake-style warehouse.
This project simulates that environment end to end:

1. A free-tier Postgres database (Supabase), reachable from Excel via
   Power Query — the same "pull data by a link" workflow the role needs.
2. A six-table relational schema modeling an MSME lender's core
   operations: staff, customers, loan products, loans, and repayments.
3. A Python generator producing realistic, internally-consistent dummy
   data across all six tables.

## Schema

Six tables: `departments`, `employees`, `customers`, `products`,
`loans`, `payments`. Full `CREATE TABLE` statements, in the order they
must be run, are in [`schema.sql`](./schema.sql).

**departments** — `sales`, `customer_service`, `human_resources`,
`finance_and_accounting`, `c_suite`, `collections`, `underwriters`.
`department_head_id` points at the highest-position employee in that
department (or the CEO, for `c_suite`).

**employees** (50 total) — three-tier structure per department (1 head,
2-3 specialists, remaining as associates), plus a separate `c_suite`
department with distinct CEO/CFO/COO roles. Salaries follow a single
consistent rule: each tier is 1.5× the one below it (associate 70,000 →
specialist 105,000 → head 157,500 → CFO/COO 236,250 → CEO 354,375).

**customers** (1,000) — one of six business types (retail, wholesale,
agriculture, hospitality, health, transport), with `monthly_cashflow`
and `asset_value` drawn from a triangular distribution to avoid an
unrealistic uniform spread.

**products** — three loan products, one per risk tier (high/medium/low),
each with its own interest rate. Rates loosely follow real Kenyan
asset-backed MSME lending ranges (roughly 4-6% low risk, 7-10% medium,
11-15% high, per digital/asset-backed lenders like Okolea).

**loans** (10,000) — the core derivation logic: a random `principal` is
generated *independently* of the customer, then compared against that
customer's cashflow/assets to determine risk tier (and therefore
`product_id` and `interest_rate`):

- Cashflow or assets ≥ loan amount → **low** risk
- Cashflow or assets ≥ 50% of loan amount → **medium** risk
- Otherwise → **high** risk

`interest_rate` on a loan is a deliberate *snapshot* of the product's
rate at disbursement time — not a live reference — since a real
borrower's agreed rate shouldn't change if the product's rate changes
later. `employee_id` links to the **collections** employee responsible
for recovering the loan (not the salesperson who originated it).
`status` is weighted 45% active / 30% paid off / 10% defaulted / 5%
pending, rather than an unrealistic even split.

**payments** — deliberately has **no `customer_id` column**: it's
derivable via `loan_id → loans.customer_id`, so storing it again would
risk the two values silently contradicting each other. One payment is
generated per month of a loan's duration, for loans that are `paid_off`
or `active`.

### Key design decisions worth knowing

- **No stored, derivable values.** Loan balance, department headcount,
  and customer risk tier are all intentionally *not* columns — they're
  calculated via queries, not stored and risked going stale.
- **The departments ↔ employees circular dependency** (`employees.department_id`
  references `departments`, `departments.department_head_id` references
  `employees`) is resolved by creating `departments` first with
  `department_head_id` nullable and unconstrained, creating `employees`
  second, then adding the foreign key back with `ALTER TABLE` and
  backfilling head ids with `UPDATE`.

## Important precondition

**This must be run against a freshly created, empty database**, with
the tables created and CSVs imported in the exact order in
`schema.sql`, and with no failed or retried inserts along the way.

Why this matters: Postgres's `SERIAL` id counter advances on every
insert *attempt* — successful or not — and never reuses a number. The
data generator (`company.py`) assumes ids start at 1 with no gaps (e.g.
customer ids 1-1000, matching CSV row order exactly). If your database's
actual ids don't start cleanly at 1 — check with
`SELECT MIN(id) FROM <table>;` — every foreign key the generator writes
will point at the wrong row.

## Setup

1. Run `company.py` to generate the four CSVs (`kaunda_ltd_employees.csv`,
   `kaunda_ltd_customers.csv`, `kaunda_ltd_loans.csv`,
   `kaunda_ltd_payments.csv`). Requires the `faker` package
   (`pip install faker`).
2. Create a free Postgres database (e.g. via [Supabase](https://supabase.com)).
3. Run `schema.sql` section by section, importing each CSV via your
   database's import tool (e.g. Supabase's Table Editor → Insert →
   Import data from CSV) at the point marked in the file.
4. Connect Excel via **Data → Get Data → From Database → From
   PostgreSQL Database** (Power Query), using your database's
   connection details. Requires the free Npgsql driver installed once.
   If your network is IPv4-only, use the Session Pooler connection
   string rather than Direct Connection.

## Known limitations

These are deliberate simplifications, made to prioritize reaching the
Excel/dashboarding stage over further data realism:

- Cashflow and asset value ranges are **not** tied to business type —
  a wholesale trader and a salon draw from the same distribution.
- `paid_off` and `active` loans can have payment schedules that extend
  into the future relative to "today" in the dataset's timeline.
- `active` loans get a full payment history identical in shape to
  `paid_off` loans — nothing in the payments data itself distinguishes
  "fully repaid" from "still ongoing."
- `defaulted` and `pending` loans have zero payment records.
- Phone numbers and addresses use Faker's default US-style formatting
  (no full Kenyan locale exists in Faker for these providers).
- `product_category()` hardcodes product ids 1/2/3 assuming products
  were inserted high → medium → low risk, per `schema.sql`.
- No random seed is set — each generation run produces different data.

## What's next

- Validate the Power Query connection and build a first pivot
  table/chart against live data.
- Build out Excel dashboards covering loan portfolio composition,
  risk-tier distribution, and repayment performance.
- Package summary views into a PowerPoint-style investor report.
