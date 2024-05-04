import sqlite3
import random
import string
import os


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

    # List of departments
    departments = ['Engineering', 'Marketing', 'Finance', 'HR']

    # Populate departments table
    for dept_name in departments:
        cursor.execute("INSERT INTO departments (name) VALUES (?)", (dept_name,))

    # Generate and insert sample employee data
    for _ in range(30):
        name = ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
        age = random.randint(20, 60)
        department_id = random.randint(1, len(departments))
        cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (?, ?, ?)", (name, age, department_id))

    # Add Bob
    cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (?, ?, ?)", ('bob', 10, 'Engineering'))

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


def sql_query_employee_by_name(db_name, user_input, show_query=False):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Vulnerable SQL query construction
    query = "SELECT * FROM employees WHERE name = '" + user_input + "'"

    # Print query if requested
    if show_query:
        print('Querying: ' + "'" + query + "")

    # Execute the query
    cursor.execute(query)

    # Fetch the results
    results = cursor.fetchall()

    # Print the results
    for row in results:
        print(row)

    # Close the database connection
    conn.close()


def run_user_prompt():
    print('Enter "Options" for options')
    print('Search employees by name')

    show_query = False
    while True:
        user_input = input("Database: ")
        if user_input == 'Options':
            user_input = input("(q)uit, (v)iew, (t)oggle show query: ")
            if user_input == 'q':
                break
            elif user_input == 'v':
                print()
                view_db('sample.db')
            elif user_input == 't':
                show_query = not show_query
        else:
            print()
            sql_query_employee_by_name('sample.db', user_input, show_query)
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

