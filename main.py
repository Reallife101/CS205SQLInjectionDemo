import sqlite3
import random
import string
import os
from faker import Faker
from enum import Enum


class QueryBuffer:
    def __init__(self):
        self.queries = []

    def push(self, query):
        self.queries.append(query)

    def print(self, i=0):
        i = len(self.queries) if i == 0 else i
        # stack = self.queries[-1:(-1-i):-1]
        stack = self.queries[-i:]
        for q in stack:
            print('    \033[92m' + q + '\033[0m')

query_history = QueryBuffer()


def create_random_db(db_name):
    # Connect to the SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create employees table
    cursor.executescript('''CREATE TABLE IF NOT EXISTS employees (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            age INTEGER,
                            department_id INTEGER,
                            FOREIGN KEY (department_id) REFERENCES departments(id)
                          )''')

    # Create departments table
    cursor.executescript('''CREATE TABLE IF NOT EXISTS departments (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL
                          )''')

    # Create account table
    cursor.executescript('''CREATE TABLE IF NOT EXISTS account_details (
                            id INTEGER PRIMARY KEY, 
                            username TEXT NOT NULL,
                            password TEXT NOT NULL
                          )''')

    # List of departments
    departments = ['Engineering', 'Marketing', 'Finance', 'HR']

    # Populate departments table
    for dept_name in departments:
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (dept_name,))

    # Generate and insert sample employee data
    Faker.seed(123)
    fake = Faker()
    for _ in range(30):
        name = fake.first_name()
        username = 'user_' + name
        password = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
        age = random.randint(20, 60)
        department_id = random.randint(1, len(departments))
        cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (?, ?, ?)", (name, age, department_id))
        cursor.execute("INSERT INTO account_details (username, password) VALUES (?, ?)", (username, password))

    # Add Bob
    name = 'Bob'
    username = 'user_Bob'
    password = 'bobpass'
    age = 10
    department_id = 1
    cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (?, ?, ?)", (name, age, department_id))
    cursor.execute("INSERT INTO account_details (username, password) VALUES (?, ?)", (username, password))

    # Commit the changes
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


def view_db(db_name):
    import sqlite3

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get a list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Iterate over each table and print its contents
    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}")
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        print()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


def delete_db(db_name):
    # Check if the database file exists
    if os.path.exists(db_name):
        # Delete the database file
        os.remove(db_name)


def fit_name(name, length):
    extra = length - len(name)
    return name + ' '*extra


def print_employee_query(rows):
    max_name = max([ len(str(r[0])) for r in rows ] + [5]) + 1
    max_age = max([ len(str(r[1])) for r in rows ] + [4]) + 1
    print(fit_name('Name:', max_name) + fit_name('Age:', max_age) + 'Department:')
    for r in rows:
        print(fit_name(str(r[0]), max_name) + fit_name(str(r[1]), max_age) + str(r[2]))

def sql_query_employee_by_name(db_name, user_input, show_query=False, raw_sql=False, strong_sec=False):
    # Clean input
    if strong_sec:
        user_input = user_input.split("'")[0]

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query the prompt
    # query = user_input if raw_sql else "SELECT name, age, department_id FROM employees WHERE name COLLATE NOCASE = '" + user_input + "'"
    query = user_input if raw_sql else "SELECT name, age, department_id FROM employees WHERE name COLLATE NOCASE LIKE '%" + user_input + "%'"
    query_history.push(query)
    if raw_sql:
        print('    --- Executing: ' + "\033[92m" + query + "\033[0m ---")
    elif show_query:
        print('    --- Querying: ' + "\033[92m" + query + "\033[0m ---")
    try:
        cursor.execute(query)
    except Exception as e:
        if show_query:
            print("\033[91m    --- Invalid Prompt ---\033[0m", e)
        else:
            print("No Results")
        return

    # Fetch the results
    results = cursor.fetchall()

    # Print the results
    if not len(results):
        print("No Results")
    else:
        if raw_sql:
            for row in results:
                print(row)
        else:
            print_employee_query(results)

    # Close the database connection
    if raw_sql:
        conn.commit()
    cursor.close()
    conn.close()


def add_employee(db_name, show_query=False, strong_sec=False):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    employee_name = input("Enter name: ")
    age = input("Enter age: ")
    department_id = input("Enter department number: ")

    if strong_sec:
        employee_name = employee_name.split("'")[0]
        age = age.split("'")[0]
        department_id = department_id.split("'")[0]

    query = f"INSERT INTO employees (age, name, department_id) VALUES ({age}, '{employee_name}', {department_id})"
    query_history.push(query)
    if show_query:
        print('    --- Inserting: ' + "\033[92m" + query + "\033[0m ---")
    try:
        cursor.executescript(query)
        conn.commit()
    except Exception as e:
        if show_query:
            print("\033[91m    --- Invalid Prompt ---\033[0m", e)

    cursor.close()
    conn.close()


def create_employee_account(db_name, show_query=False):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    employee_name = input("Enter employee name: ")
    if "'" in employee_name:
        print('\033[91m    --- Invalid Name ---\033[0m')
        return

    query = "SELECT * FROM employees WHERE name = '" + employee_name + "'"
    query_history.push(query)
    if show_query:
        print('    --- Querying: ' + "\033[92m" + query + "\033[0m ---")
    try:
        cursor.execute(query)
    except Exception as e:
        if show_query:
            print("\033[91m    --- Invalid Prompt ---\033[0m", e)

    results = cursor.fetchall()
    if not len(results) == 1:
        return

    username = input("Create username: ")
    password = input("Create password: ")
    query = f"INSERT INTO account_details (username, password) VALUES ('{username}', '{password}')"
    query_history.push(query)
    if show_query:
        print('    --- Inserting: ' + "\033[92m" + query + "\033[0m ---")
    try:
        cursor.executescript(query)
        conn.commit()
    except Exception as e:
        if show_query:
            print("\033[91m    --- Invalid Prompt ---\033[0m", e)

    cursor.close()
    conn.close()


def employee_login(db_name, show_query=False):
    user = ''

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    username = input("Enter username: ")
    query = "SELECT username, password FROM account_details WHERE username = '" + username + "'"
    query_history.push(query)
    if show_query:
        print('    --- Querying: ' + "\033[92m" + query + "\033[0m ---")
    try:
        cursor.execute(query)
    except Exception as e:
        if show_query:
            print("\033[91m    --- Invalid Prompt ---\033[0m", e)

    results = cursor.fetchall()
    if not len(results) == 1:
        print('\033[91m    --- No account with that username ---\033[0m')
        return user

    password = input("Enter password: ")
    if password == results[0][1]:
        user = results[0][0] + ' - '

    cursor.close()
    conn.close()

    return user


def run_user_prompt():
    print('\033[94mEnter "Options" for options\033[0m')

    user = ''
    strong_sec = False
    show_query = False
    raw_sql = False
    while True:
        # Prompt Search
        if raw_sql:
            user_input = input("\033[94mRaw SQL: \033[0m")
        else:
            user_input = input("\033[93m" + user + "\033[0m" + "\033[94mSearch Employee: \033[0m")

        # Handle Options 
        if user_input == 'Options':
            user_input = input("(q)uit, Add-(e)mployee, Add-(a)ccount, (l)ogin, log(o)ut: ")
            if user_input == 'q':
                break
            elif user_input == 'e':
                add_employee('sample.db', show_query, strong_sec)
            elif user_input == 'a':
                create_employee_account('sample.db', show_query)
            elif user_input == 'l':
                user = employee_login('sample.db', show_query)
            elif user_input == 'o':
                user = ''

        # Handle Debug
        elif user_input == 'Debug':
            user_input = input("(v)iew database, (t)oggle show query, (r)aw sql, (s)trong security: ")
            if user_input == 'v':
                print()
                view_db('sample.db')
            elif user_input == 't':
                show_query = not show_query
            elif user_input == 'r':
                raw_sql = not raw_sql
            elif user_input == 's':
                strong_sec = not strong_sec

        # Print Query History
        elif user_input and user_input[0] == ':':
            i = int(user_input[1])
            query_history.print(i)
            
        # Handle Search
        else:
            sql_query_employee_by_name('sample.db', user_input, show_query|raw_sql, raw_sql, strong_sec)
 

if __name__ == '__main__':
    delete_db('sample.db')
    create_random_db('sample.db')
    run_user_prompt()
    

