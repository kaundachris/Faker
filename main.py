"""
Generates four CSVs — employees, customers, loans, payments — that correspond to schema.sql. 

Run this BEFORE creating the tables described there, so the CSVs exist to import.

IMPORTANT PRECONDITION: this script assumes the database it's headed for is freshly created and empty, 
with no failed/retried inserts before the real import. Postgres's SERIAL id counter advances on every insert
attempt, whether it succeeds or not, and never reuses a number — so IDs are assumed to start at 1 with no gaps. 

If your actual database's ids don't start cleanly at 1 (check with `SELECT MIN(id) FROM <table>;`), the hardcoded 
ranges in `loan()` (customer_id 1-1000) and the id reconstruction in `read_employee_data()` will be wrong, and every
foreign key this script generates downstream will point at the wrong row.

No random seed is set, so each run produces different data.
"""

from faker import Faker
import datetime, csv, random

class Company():
    EMPLOYEE_FIELDNAMES = ["name", "country_code", "phone_number", "dob", "address",
                           "position", "salary", "department_id", "created_at", "status"]
    CUSTOMER_FIELDNAMES = ["name", "business_name", "country_code", "phone_number", "address",
                           "monthly_cashflow", "asset_value", "business_type", "created_at", "status"]
    BUSINESS_TYPES = ["retail", "wholesale", "agriculture", "hospitality", "health", "transport"]
    LOAN_STATUS = ['active', 'paid_off', 'defaulted', 'pending']
    LOAN_FIELDNAMES = ["customer_id", "product_id", "principal", "loan_duration_months",
                       "interest_rate", "disbursement_date", "employee_id", "status"]
    PAYMENTS_KEYS = ["loan_id", "amount", "payment_date", "payment_method"]
    PAYMENT_METHODS = ["cash", "mpesa", "bank_transfer", "cheque"]

    def __init__(self,):
        """initialize the list of employees"""
        self.employees = []
        self.customers = []
        self.loans = []
        self.payments = []
        self.fake = Faker()

    def employee(self):
        """Generate the basic details of the employee"""
        person_details = {
            "name": self.fake.name(), "country_code": "+254", "phone_number": self.fake.phone_number(),
            "dob": None, "address": self.fake.address(),"position": None, "salary": None, "department_id": None,
            "created_at": datetime.date(2026, 8, 29), "status": "active"
            }
        return person_details

    def heads(self):
        """Generates the position details of heads of departments"""
        person_details = self.employee()
        person_details["dob"] = self.fake.date_of_birth(minimum_age=35, maximum_age=45)
        person_details["position"] = "head"
        person_details["salary"] = 157500
        return person_details

    def specialists(self):
        """Generates the position details of speecialists"""
        person_details = self.employee()
        person_details["dob"] = self.fake.date_of_birth(minimum_age=30, maximum_age=40)
        person_details["position"] = "specialist"
        person_details["salary"] = 105000
        return person_details

    def associates(self):
        """Generates the position details of associates"""
        person_details = self.employee()
        person_details["dob"] = self.fake.date_of_birth(minimum_age=25, maximum_age=35)
        person_details["position"] = "associate"
        person_details["salary"] = 70000
        return person_details

    def populate_specialists(self, no_of_employees: int, department_id: int):
        """Populates the departmental specialists"""
        for _ in range(no_of_employees):
            team_member = self.specialists()
            team_member["department_id"] = department_id
            self.employees.append(team_member)

    def populate_associates(self, no_of_employees: int, department_id: int):
        """Populates the departmental associates"""
        for _ in range(no_of_employees):
            team_member = self.associates()
            team_member["department_id"] = department_id
            self.employees.append(team_member)

    def sales(self):
        """Populates the sales team"""
        # hod
        sales_head = self.heads()
        sales_head["department_id"] = 1
        self.employees.append(sales_head)

        # specialists
        self.populate_specialists(3, 1)

        # associates
        self.populate_associates(6, 1)

    def cx(self):
        """Populates the cx team"""
        # hod
        cx_head = self.heads()
        cx_head["department_id"] = 2
        self.employees.append(cx_head)

        # specialists
        self.populate_specialists(3, 2)

        # associates
        self.populate_associates(6, 2)

    def hr(self):
        """Populates the hr team"""
        # hod
        hr_head = self.heads()
        hr_head["department_id"] = 3
        self.employees.append(hr_head)

        # specialists
        self.populate_specialists(2, 3)

        # associates
        self.populate_associates(2, 3)

    def finance(self):
        """Populates the finance team"""
        # hod
        finance_head = self.heads()
        finance_head["department_id"] = 4
        self.employees.append(finance_head)

        # specialists
        self.populate_specialists(2, 4)

        # associates
        self.populate_associates(2, 4)

    def collections(self):
        """Populates the collections team"""
        # hod
        collections_head = self.heads()
        collections_head["department_id"] = 6
        self.employees.append(collections_head)

        # specialists
        self.populate_specialists(3, 6)

        # associates
        self.populate_associates(6, 6)

    def underwriters(self):
        """Populates the underwriters team"""
        # hod
        underwriters_head = self.heads()
        underwriters_head["department_id"] = 7
        self.employees.append(underwriters_head)

        # specialists
        self.populate_specialists(3, 7)

        # associates
        self.populate_associates(3, 7)

    def c_suite(self):
        """Generates the details of the c-suite"""
        # ceo details
        ceo = self.employee()
        ceo["dob"] = self.fake.date_of_birth(minimum_age=35, maximum_age=45)
        ceo["position"] = "ceo"
        ceo["salary"] = 354375
        ceo["department_id"] = 5
        self.employees.append(ceo)

        # cfo details
        cfo = self.employee()
        cfo["dob"] = self.fake.date_of_birth(minimum_age=35, maximum_age=45)
        cfo["position"] = "cfo"
        cfo["salary"] = 236250
        cfo["department_id"] = 5
        self.employees.append(cfo)

        # coo details
        coo = self.employee()
        coo["dob"] = self.fake.date_of_birth(minimum_age=35, maximum_age=45)
        coo["position"] = "coo"
        coo["salary"] = 236250
        coo["department_id"] = 5
        self.employees.append(coo)

    def customer(self):
        """Generate the basic details of the customer"""
        asset_value = int(random.triangular(10000, 5000000, 100000))
        cashflows = int(random.triangular(5000, 10000000, 60000))
        business_type = random.choice(self.BUSINESS_TYPES)

        person_details = {
            "name": self.fake.name(), "business_name": self.fake.company(), "country_code": "+254", 
            "phone_number": self.fake.phone_number(), "address": self.fake.address(), "monthly_cashflow": cashflows,
            "asset_value": asset_value, "business_type": business_type, "created_at": datetime.date(2026, 8, 29),
            "status": "active"
            }
        return person_details

    def populate_customers(self, no_of_customers:int):
        """Populates the customers"""
        for _ in range(no_of_customers):
            customer = self.customer()
            self.customers.append(customer)

    def generate_employee_file(self):
        """Generates the full employee data"""
        self.sales()
        self.cx()
        self.hr()
        self.finance()
        self.collections()
        self.underwriters()
        self.c_suite()
        with open("kaunda_ltd_employees.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.EMPLOYEE_FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.employees)

    def generate_customer_file(self):
        """Generates the full customer data"""
        self.populate_customers(1000)
        with open("kaunda_ltd_customers.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.CUSTOMER_FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.customers)

    def read_customer_data(self):
        """Loads the customer data to memory"""
        customers_data = []
        with open("kaunda_ltd_customers.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                customers_data.append(row)

        return customers_data

    def read_employee_data(self):
        """Loads the employee data to memory"""
        collection_team_ids = []
        with open("kaunda_ltd_employees.csv", "r") as file:
            reader = csv.DictReader(file)
            i = 1
            for row in reader:
                if int(row["department_id"]) == 6:
                    collection_team_ids.append(i)
                i += 1

        return collection_team_ids

    def product_category(self, loan_amount, cashflow, asset_value):
        """determines the product category/risk profile of the customer"""
        if cashflow >= loan_amount or asset_value >= loan_amount:
            return {"id": 3, "interest": 6}
        elif cashflow >= (.5 * loan_amount) or asset_value >= (.5 *loan_amount):
            return {"id": 2, "interest": 9}
        return {"id": 1, "interest": 12}
        

    def loan(self, customer_data, collection_team_ids):
        """Generates loan data"""
        customer_id = random.randint(1, 1000)
        customer = customer_data[customer_id - 1]
        loan_amount = int(random.triangular(30000, 10000000, 100000))
        product = self.product_category(loan_amount, cashflow=int(customer["monthly_cashflow"]), asset_value=int(customer["asset_value"]))
        product_id = product["id"]
        loan_duration = int(random.triangular(1, 12, 3))
        interest_rate = product["interest"]

        start_of_company = datetime.date(2025, 1, 1)
        db_creation = datetime.date(2026, 8, 29)
        random_days = random.randint(0, (db_creation - start_of_company).days)
        disbursement_date = start_of_company + datetime.timedelta(days=random_days)
        loan_status = random.choices(self.LOAN_STATUS, weights=[45, 30, 5, 5], k=1)[0]

        loan = {
            "customer_id": customer_id, "product_id": product_id, "principal": loan_amount, "loan_duration_months": loan_duration,
            "interest_rate": interest_rate, "disbursement_date": disbursement_date,
            "employee_id": random.choice(collection_team_ids), "status": loan_status
        }

        return loan

    def populate_loans(self):
        """Populates the loans data - loans given out"""
        customer_data = self.read_customer_data()
        collection_team_ids = self.read_employee_data()
        for _ in range(10000):
            self.loans.append(self.loan(customer_data, collection_team_ids))

    def generate_loans_file(self):
        """Generates the full payment data"""
        self.populate_loans()
        with open("kaunda_ltd_loans.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.LOAN_FIELDNAMES)
            writer.writeheader()
            writer.writerows(self.loans)

    def populate_payments(self):
        """Populates the payments"""
        with open("kaunda_ltd_loans.csv", "r") as file:
            reader = csv.DictReader(file)
            i = 0
            for row in reader:
                i += 1
                if row["status"] == "paid_off" or row["status"] == "active":
                    row_id = i
                    principal = int(row["principal"])
                    loan_duration = int(row["loan_duration_months"])
                    interest_rate = int(row["interest_rate"])/100
                    disbursement_date = row["disbursement_date"]
                    year, month, date = disbursement_date.split("-")
                    year, month, date = int(year), int(month), 28
                    total_interest = principal * interest_rate * loan_duration
                    payable_amount = principal + total_interest
                    installments = int(payable_amount / loan_duration)
                    for _ in range(loan_duration):
                        month = month + 1
                        if month > 12:
                            month -= 12
                            year += 1
                        payment = {
                            "loan_id": row_id, "amount": installments, "payment_date": f"{year}-{month}-{date}",
                            "payment_method": random.choice(self.PAYMENT_METHODS)
                        }
                        self.payments.append(payment)

    def generate_payments_file(self):
        """Generates the full payment data"""
        self.populate_payments()
        with open("kaunda_ltd_payments.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.PAYMENTS_KEYS)
            writer.writeheader()
            writer.writerows(self.payments)

    def form_company(self):
        """Generates all the company's files"""
        self.generate_employee_file()
        self.generate_customer_file()
        self.generate_loans_file()
        self.generate_payments_file()
        return None


kaunda_ltd = Company()
kaunda_ltd.form_company()
print(f"employees: {len(kaunda_ltd.employees)}")
print(f"customers: {len(kaunda_ltd.customers)}")
print(f"loans: {len(kaunda_ltd.loans)}")
print(f"payments: {len(kaunda_ltd.payments)}")
