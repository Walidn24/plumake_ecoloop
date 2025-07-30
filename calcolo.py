import psycopg2
import time
import olca_ipc as ipc
import olca_schema as o
import time
import logging
import os
import csv

# connect to postgres
def init_postgres():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "ecoloop_test"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "walid123"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5433")
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

# debug: for purpose to extract data as a csv
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


# delete all postgres tables
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

# creata postgres tables
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
                description VARCHAR(7000),
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
                ef VARCHAR(225),
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

# insert process data
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
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return inserted_id
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL inserting process data issues: {e}")
        raise      

# !DO Not populate multiple times
# save default values to db
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
        
# save impact result to database
def save_into_impact_result(id_process, ef, um, value, source_db_id, method_id):
    try:
        cur.execute(
            """
            INSERT INTO tab_emission_factors (id_process, ef, um, value, source_db_id, method_id)             
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (id_process, ef, um, value, source_db_id, method_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL inserting process data issues: {e}")
        raise          

def calculate_impact(process_id_returned, uuid, requested_method="EN15804+A2 (EF 3.1)"):
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
            name = impact.impact_category.name.replace("EN15804 (EF 3.1) | ", "").replace("EN15804 (EF3.0 & 3.1) | ", "").replace("Output | ", "").replace("Resource | ", "").replace("Waste | ", "")
            value = round(impact.amount, 5)
            um = impact.impact_category.ref_unit

            print(f"nome: {name}, valore: {value},  unità: {um}")
            # TODO: add insert to db methods
            save_into_impact_result(process_id_returned, name, um, value, source_db_id=1, method_id=3)
            
    except Exception as e:
        logging.error(f"Error retrieving impact results: {e}")

    # Dispose result to free memory
    time.sleep(1)  # Optional pause
    result.dispose()
    logging.info("Result disposed.")
    

def populate_data(amount_data=None):
    # ✅ Percorso alla cartella CSV
    cartella_csv = r'csv-large'
    
    if amount_data is not None:   
        numero_file_da_leggere = amount_data

        # ✅ Elenco dei primi N file .csv
        file_csv = [f for f in os.listdir(cartella_csv) if f.endswith('.csv')][:numero_file_da_leggere]
    
    else:
        file_csv = [f for f in os.listdir(cartella_csv) if f.endswith('.csv')]
    
    # ✅ Leggi ogni file e stampa UUID e Name
    for nome_file in file_csv:
        percorso_file = os.path.join(cartella_csv, nome_file)
        print(f"\n📄 File: {nome_file}")

        file_path = 'categories/cleaned_category.csv'
        try:
            with open(percorso_file, mode='r', encoding='utf-8') as f:
                lettore = csv.DictReader(f)
                for riga in lettore:
                    uuid = riga.get('UUID')
                    process_name = riga.get('Name')
                    category = riga.get('Category')
                    geo = riga.get('Location')
                    description = riga.get('Description')
                    version = riga.get('Version')
                    tags = riga.get('Tags')
                    valid_from = riga.get('Valid from')
                    valid_until = riga.get('Valid until')
                    location = riga.get('Location')
                    flow_schema = riga.get('Flow schema')

                    
                    # limit description length
                    short_description = description[:7000]
                    
                    # popola tabella process
                    process_id = insert_process_data(cur, conn, process_name, 1, "", "", uuid, category, short_description, version, tags, valid_from, valid_until, location, flow_schema)
                    
                    # calcola e popola tabella emmision factors
                    calculate_impact(process_id_returned=process_id, uuid=uuid, requested_method="EN15804+A2 (EF 3.1)")

        except Exception as e:
            print(f"  ⚠ Errore nel file {nome_file}: {e}")


if __name__ == "__main__":

    # connect to postgres
    cur, conn = init_postgres()
    
    # manipolare tabelle postgres 
    try:
        #!!!! DELETE ALL THE TABLES !!!!!
        # delete_all_tables(cur, conn)
        
        # create tables
        create_tables(cur, conn)

        #! use this method one time only to populate default data
        init_default_table_data(cur, conn)       

        # popola tabelle  
        # se volessi popolare tutti dati lascia input: amount_data=None
        populate_data(amount_data=10)
    finally:
        cur.close()
        conn.close()
      



    


