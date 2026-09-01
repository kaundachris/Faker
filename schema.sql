-- ============================================================
-- Kaunda Ltd — Dummy MSME Lending Database
-- Run against a FRESH, EMPTY Postgres database (see README
-- "Important precondition" before running this).
-- ============================================================

-- 1. DEPARTMENTS
-- department_head_id is left nullable and without a FK constraint
-- here because employees doesn't exist yet — departments and
-- employees reference each other (a circular dependency), so we
-- create departments first without the constraint, create
-- employees next, then add the constraint back with ALTER TABLE.
CREATE TABLE departments (
    id SERIAL PRIMARY KEY NOT NULL,
    department_name TEXT NOT NULL,
    department_head_id INTEGER,
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL
);

INSERT INTO departments (department_name, department_head_id, created_at, updated_at) VALUES
('sales', NULL, '2026-08-29', '2026-08-29'),
('customer_service', NULL, '2026-08-29', '2026-08-29'),
('human_resources', NULL, '2026-08-29', '2026-08-29'),
('finance_and_accounting', NULL, '2026-08-29', '2026-08-29'),
('c_suite', NULL, '2026-08-29', '2026-08-29'),
('collections', NULL, '2026-08-29', '2026-08-29'),
('underwriters', NULL, '2026-08-29', '2026-08-29');

-- 2. EMPLOYEES
-- department_id can safely reference departments inline now,
-- since departments already exists with rows.
CREATE TABLE employees (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    country_code TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    dob DATE NOT NULL,
    address TEXT NOT NULL,
    position TEXT NOT NULL,
    salary DECIMAL NOT NULL,
    department_id INTEGER NOT NULL,
    created_at DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- >>> Import kaunda_ltd_employees.csv into `employees` here <<<
-- (via Supabase Table Editor's CSV import, or your own loader)

-- Now that employees exists, close the circular dependency:
ALTER TABLE departments ADD FOREIGN KEY (department_head_id) REFERENCES employees(id);

-- Set each department's head to the employee with position = 'head'
-- (or 'ceo' for c_suite) in that department. Adjust department ids
-- below to match your actual departments table if they differ.
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 1 AND position = 'head') WHERE id = 1; -- sales
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 2 AND position = 'head') WHERE id = 2; -- customer_service
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 3 AND position = 'head') WHERE id = 3; -- human_resources
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 4 AND position = 'head') WHERE id = 4; -- finance_and_accounting
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 5 AND position = 'ceo')  WHERE id = 5; -- c_suite
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 6 AND position = 'head') WHERE id = 6; -- collections
UPDATE departments SET department_head_id = (SELECT id FROM employees WHERE department_id = 7 AND position = 'head') WHERE id = 7; -- underwriters

-- 3. CUSTOMERS
CREATE TABLE customers (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    business_name TEXT NOT NULL,
    country_code TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    address TEXT NOT NULL,
    monthly_cashflow INTEGER NOT NULL,
    asset_value INTEGER NOT NULL,
    business_type TEXT NOT NULL,
    created_at DATE NOT NULL,
    status TEXT NOT NULL
);

-- >>> Import kaunda_ltd_customers.csv into `customers` here <<<

-- 4. PRODUCTS
CREATE TABLE products (
    id SERIAL PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    risk_tier TEXT NOT NULL,
    interest_rate DECIMAL NOT NULL,
    created_at DATE NOT NULL
);

-- Order matters: product_category() in company.py maps risk tiers
-- to product ids assuming this exact insert order (high, medium, low
-- landing on ids 1, 2, 3 respectively).
INSERT INTO products (name, risk_tier, interest_rate, created_at) VALUES
('saidika_high_risk', 'high', 12.0, '2026-08-29'),
('saidika_medium_risk', 'medium', 9.0, '2026-08-29'),
('saidika_low_risk', 'low', 6.0, '2026-08-29');

-- 5. LOANS
CREATE TABLE loans (
    id SERIAL PRIMARY KEY NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    principal INTEGER NOT NULL,
    loan_duration_months INTEGER NOT NULL,
    interest_rate DECIMAL NOT NULL,
    disbursement_date DATE NOT NULL,
    employee_id INTEGER,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- >>> Import kaunda_ltd_loans.csv into `loans` here <<<

-- 6. PAYMENTS
-- Deliberately has no customer_id — it's derivable via
-- loan_id -> loans.customer_id, so storing it again here would be
-- a normalization violation (the same value could go stale/
-- contradict itself if a loan's customer_id ever changed).
CREATE TABLE payments (
    id SERIAL PRIMARY KEY NOT NULL,
    loan_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    payment_method TEXT NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(id)
);

-- >>> Import kaunda_ltd_payments.csv into `payments` here <<<
