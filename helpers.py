def create_tables(cur, conn):
    try:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tab_process (
                id SERIAL NOT NULL PRIMARY KEY,
                process_name VARCHAR(255),
                macro_cat INT,
                note VARCHAR(500),
                geo VARCHAR(25),
                uuid uuid
            );

            # CREATE TABLE IF NOT EXISTS tab_macro_cat (
            #     id SERIAL NOT NULL PRIMARY KEY,
            #     macro_cat VARCHAR(255)
            # );

            CREATE TABLE IF NOT EXISTS tab_source_db (
                id SERIAL NOT NULL PRIMARY KEY,
                source_db_name VARCHAR(255)
            );

            CREATE TABLE IF NOT EXISTS tab_methods (
                id SERIAL NOT NULL PRIMARY KEY,
                method_name VARCHAR(255)
            );

            # CREATE TABLE IF NOT EXISTS tab_geography (
            #     id SERIAL NOT NULL PRIMARY KEY,
            #     geography VARCHAR(255)
            # );

            CREATE TABLE IF NOT EXISTS tab_emmision_factors (
                id SERIAL NOT NULL PRIMARY KEY,
                id_process integer NOT NULL,
                EF VARCHAR(25),
                UM VARCHAR(25),
                value DOUBLE PRECISION,
                source_db integer NOT NULL,
                method_id integer NOT NULL,
                FOREIGN KEY (id_process) REFERENCE tab_process(id),
                FOREIGN KEY (source_db) REFERENCE tab_source_db(id),
                FOREIGN KEY (method_id) REFERENCE tab_methods(id)
            )
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table creating issues: {e}")
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

            INSERT INTO tab_macro_cat (macro_cat) VALUES ('Energia');
            INSERT INTO tab_macro_cat (macro_cat) VALUES ('materie prime');
            INSERT INTO tab_macro_cat (macro_cat) VALUES ('Rifiuti');

            # INSERT INTO tab_geography (geography) VALUES ('global');
            # INSERT INTO tab_geography (geography) VALUES ('euro area');
            """
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL table creating issues: {e}")
        raise     
