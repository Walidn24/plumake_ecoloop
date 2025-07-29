import psycopg2
import time
import olca_ipc as ipc
import olca_schema as o
import time
import logging
import os
import csv

def init_postgres():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "ecoloop_test"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "1234"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        return cur, conn
    
    except Exception as e:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print(f"PostgreSQL init issues: {e}")
        raise


def create_csv_categories(category, file_path='categories/categories.csv'):
    fieldnames = ["Category"]

    data = [
        {"Category": category}
    ]

    # file_path = 'categories/categories.csv'

    # Ensure the 'categories' directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if the file exists and is empty
    file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0

    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)


def delete_all_tables(cur, conn):
    try:
        # Set search_path to include public schema
        cur.execute("SET search_path TO public;")

        cur.execute(
            """
            DROP TABLE IF EXISTS tab_emission_factors CASCADE;
            DROP TABLE IF EXISTS tab_process CASCADE;
            DROP TABLE IF EXISTS tab_source_db CASCADE;
            DROP TABLE IF EXISTS tab_methods CASCADE;
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table dropping issues: {e}")
        raise 


def create_tables(cur, conn):
    try:
        # Create tab_process table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tab_process (
                id SERIAL NOT NULL PRIMARY KEY,
                process_name VARCHAR(255),
                macro_cat INT,
                note VARCHAR(500),
                geo VARCHAR(25),
                uuid UUID, 
                category VARCHAR(500),
                description VARCHAR(2500),
                version VARCHAR(10),
                tags VARCHAR(225),
                valid_form DATE,
                valid_until DATE,
                location VARCHAR(65),
                flow_schema VARCHAR(225)
            );
            """
        )
        conn.commit()

        # Create tab_source_db table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tab_source_db (
                id SERIAL NOT NULL PRIMARY KEY,
                source_db_name VARCHAR(255)
            );
            """
        )
        conn.commit()

        # Create tab_methods table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tab_methods (
                id SERIAL NOT NULL PRIMARY KEY,
                method_name VARCHAR(255)
            );
            """
        )
        conn.commit()

        # Create tab_emission_factors table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tab_emission_factors (
                id SERIAL NOT NULL PRIMARY KEY,
                id_process INT NOT NULL,
                ef VARCHAR(25),
                um VARCHAR(25),
                value DOUBLE PRECISION,
                source_db_id INTEGER NOT NULL,
                method_id INTEGER NOT NULL,
                FOREIGN KEY (id_process) REFERENCES tab_process (id) ON DELETE CASCADE,
                FOREIGN KEY (source_db_id) REFERENCES tab_source_db (id) ON DELETE RESTRICT,
                FOREIGN KEY (method_id) REFERENCES tab_methods (id) ON DELETE RESTRICT
            );
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table creating issues: {e}")
        raise 


def insert_process_data(cur, conn, process_name, macro_cat, note, geo, uuid, category, description, version, tags, valid_from, valid_until, location, flow_schema):
    try:
        cur.execute(
            """
            INSERT INTO tab_process (process_name, macro_cat, note, geo, uuid, category, description, version, tags, valid_form, valid_until, location, flow_schema)             
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (process_name, macro_cat, note, geo, uuid, category, description, version, tags, valid_from, valid_until, location, flow_schema)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL inserting process data issues: {e}")
        raise      

# !DO Not populate multiple times
def init_default_table_data(cur, conn):
    try:
        cur.execute(
            """
            INSERT INTO tab_source_db (source_db_name) VALUES ('Ecoinvent 3.10');
            INSERT INTO tab_source_db (source_db_name) VALUES ('Agribalyse');
            INSERT INTO tab_source_db (source_db_name) VALUES ('DEFRA');

            INSERT INTO tab_methods (method_name) VALUES ('IPCC 2021');
            INSERT INTO tab_methods (method_name) VALUES ('EN15804');
            INSERT INTO tab_methods (method_name) VALUES ('EF 3.1');
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table creating issues: {e}")
        raise     

def insert_data(cur, conn):
    try:
        # Set search_path to include public schema
        cur.execute("SET search_path TO public;")

        cur.execute(
            """
            INSERT INTO cars (brand, model, year)
            VALUES ('Ford', 'Mustang', 1964);
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table creating issues: {e}")
        raise 

def salva_su_postgres(process_id, method, impact_name, amount, unit):
    try:
        # Set search_path to include public schema
        cur.execute("SET search_path TO public;")

        conn = psycopg2.connect(
            dbname="csv_db",
            user="walid",
            password="walid123",
            host="localhost",
            port="5432"  # default PostgreSQL
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO impact_results (process_id, method, impact_name, amount, unit)
            VALUES (%s, %s, %s, %s, %s)
        """, (process_id, method, impact_name, amount, unit))
        conn.commit()
        cur.close()
        conn.close()
        print(f"[✔] Salvato: {impact_name} = {amount} {unit}")
    except Exception as e:
        print(f"[✘] Errore salvataggio PostgreSQL: {e}")

def esegui_calcolo(process_id, metodo_richiesto="EN15804+A2 (EF 3.1)"):
    client = ipc.Client(8080)
    process = client.get_descriptor(o.Process, process_id)
    if not process:
        print(f"[✘] ID Processo non trovato: {process_id}")
        return

    methods = client.get_descriptors(o.ImpactMethod)
    metodo = next((m for m in methods if metodo_richiesto in m.name), None)
    if not metodo:
        print(f"[✘] Metodo impatto '{metodo_richiesto}' non trovato.")
        return

    setup = o.CalculationSetup(target=process, impact_method=metodo)
    result = client.calculate(setup)

    if not result.wait_until_ready():
        print("[✘] Calcolo non completato in tempo.")
        return

    impact_results = result.get_total_impacts()
    print("\n=== RISULTATI CALCOLO ===")
    for impatto in impact_results:
        print(f"{impatto.impact_category.name}: {impatto.amount:.4f} {impatto.impact_category.ref_unit}")
        salva_su_postgres(process.id, metodo.name, impatto.impact_category.name, impatto.amount, impatto.impact_category.ref_unit)

    result.dispose()


def calculate_impact(uuid, requested_method="EN15804+A2 (EF 3.1)"):
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize the IPC client
    try:
        client = ipc.Client(8080)  # Adjust the port if necessary
    except Exception as e:
        logging.error(f"Failed to connect to IPC server: {e}")
        exit()

    # Define the process ID
    process_id = uuid  # Replace with your actual process ID

    # Retrieve the process descriptor
    try:
        process = client.get_descriptor(o.Process, process_id)
        if not process:
            raise ValueError(f"Process with ID {process_id} not found.")
        logging.info(f"Found process: {process.name} (ID: {process_id})  (Tag: {process.category})")
        # create_csv_categories(process.category)

    except Exception as e:
        logging.error(f"Error retrieving process: {e}")
        exit()

    # Select the first available impact method (you can refine this to pick TRACI if needed)
    try:
        methods = client.get_descriptors(o.ImpactMethod)
        # print(f"this is method: {methods}")

        if not methods:
            raise ValueError("No impact methods found in the database.")
        
        method = next((m for m in methods if requested_method in m.name), methods[0])

        logging.info(f"Using impact method: {method.name} (ID: {method.id})")
    except Exception as e:
        logging.error(f"Error retrieving impact method: {e}")
        exit()

    # Prepare the calculation setup
    setup = o.CalculationSetup(
        target=process,
        impact_method=method
    )

    # Perform the calculation
    try:
        result = client.calculate(setup)
        if result.error:
            raise ValueError(f"Calculation failed: {result.error}")
        logging.info("ready to calculate")
        logging.info(f"result: {result}")
    except Exception as e:
        logging.error(f"Error during calculation: {e}")
        exit()

    # Wait for the calculation to finish
    try:
        logging.info("Waiting for calculation to complete...")
        max_wait_time = 120  # seconds
        poll_interval = 2  # seconds
        start_time = time.time()


        while not result.wait_until_ready():
            num = num + 1
            print(f"waiting: {num}")
            if time.time() - start_time > max_wait_time:
                raise TimeoutError("Calculation did not complete within the expected time.")
            time.sleep(poll_interval)

        logging.info("Calculation completed successfully.")

        # Retrieve results
        impact_results = result.get_total_impacts()
        # flow_results = result.get_total_flows()

        # print(f'result: {impact_results, flow_results}')


    except Exception as e:
        logging.error(f"Error during or after calculation: {e}")
        result.dispose()
        exit()

    # Print impact assessment results
    try:
        print("\nImpact Assessment Results:")
        if not impact_results:
            print("No impact results available.")
        for impact in impact_results:
            print(f"{impact.impact_category.name}: {impact.amount:.5f} {impact.impact_category.ref_unit}")
            # TODO: add insert to db methods

    except Exception as e:
        logging.error(f"Error retrieving impact results: {e}")


    # Dispose result to free memory
    time.sleep(1)  # Optional pause
    result.dispose()
    logging.info("Result disposed.")


if __name__ == "__main__":
    # inserisci qui il tuo ID processo
    esempio_id = "00172b09-8b56-40eb-a9a8-d0e03dd59aa1"
    # esegui_calcolo(esempio_id)
    # calculate_impact(esempio_id)
    cur, conn = init_postgres()


    # create_csv_categories()
    try:

        #! use this method one time only to populate default data
        # init_default_table_data(cur, conn)
        
        #!!!! DELETE ALL THE TABLES !!!!!
        delete_all_tables(cur, conn)
        create_tables(cur, conn)

        # insert_data(cur, conn)

    finally:
        cur.close()
        conn.close()


