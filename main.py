import sqlite3
import random
import string
import os
from faker import Faker


def create_random_db(db_name):
    # Connect to the SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create employees table
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        age INTEGER,
                        department_id INTEGER,
                        FOREIGN KEY (department_id) REFERENCES departments(id)
                      )''')

    # Create departments table
    cursor.execute('''CREATE TABLE IF NOT EXISTS departments (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL
                      )''')

    # Create account table
    cursor.execute('''CREATE TABLE IF NOT EXISTS account_details (
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
    username = 'user_' + name
    password = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
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


def sql_query_employee_by_name(db_name, user_input, show_query=False, raw_sql=False):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Vulnerable SQL query construction
    if raw_sql:
        query = user_input
    else:
        query = "SELECT * FROM employees WHERE name = '" + user_input + "'"

    # Print query if requested
    if show_query:
        print('Querying: ' + "\033[92m" + query + "\033[0m")

    # Execute the query
    try:
        cursor.execute(query)
    except Exception as e:
        if show_query:
            print("\033[91mInvalid Prompt: \033[0m", e)
        else:
            print("\033[91mInvalid Prompt\033[0m")
        return

    # Fetch the results
    results = cursor.fetchall()

    # Print the results
    if not len(results):
        print("No Results")
    else:
        for row in results:
            print(row)

    # Close the database connection
    conn.close()


def run_user_prompt():
    print('\033[94mEnter "Options" for options\033[0m')

    show_query = False
    raw_sql = False
    while True:
        if raw_sql:
            user_input = input("\033[94mRaw SQL: \033[0m")
        else:
            user_input = input("\033[94mSearch Employee: \033[0m")

        if user_input == 'Options':
            user_input = input("\033[94m(q)uit, (v)iew, (t)oggle show query, (r)aw sql: \033[0m")
            if user_input == 'q':
                break
            elif user_input == 'v':
                print()
                view_db('sample.db')
            elif user_input == 't':
                show_query = not show_query
            elif user_input == 'r':
                raw_sql = not raw_sql
        else:
            print()
            sql_query_employee_by_name('sample.db', user_input, show_query|raw_sql, raw_sql)
            print()
 

if __name__ == '__main__':
    delete_db('sample.db')
    create_random_db('sample.db')
    # print("------------------BEFORE DB-----------------")
    # view_db('sample.db')
    # print("------------------QUERY-----------------")
    # # sql_query_employee_by_name('sample.db', "'; DELETE FROM employees WHERE name = 'bob'; --")
    # sql_query_employee_by_name('sample.db', "'; DROP TABLE employees; --")
    # print("------------------AFTER INJECTION-----------------")
    # view_db('sample.db')
    run_user_prompt()

