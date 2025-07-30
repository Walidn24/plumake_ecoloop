import os
import csv
from calcolo import insert_process_data, init_postgres



def create_csv_categories(cleaned_category, raw_category, file_path='categories/categories.csv'):
    fieldnames = ["cleaned", "raw"]

    data = [
        {"cleaned": cleaned_category, "raw": raw_category}
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

# ✅ Percorso alla cartella CSV
cartella_csv = r'csv-large'
numero_file_da_leggere = 10

# ✅ Elenco dei primi N file .csv
file_csv = [f for f in os.listdir(cartella_csv) if f.endswith('.csv')][:numero_file_da_leggere]

cur, conn = init_postgres()

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

                insert_process_data(cur, conn, process_name, 1, "", "", uuid, category, description, version, tags, valid_from, valid_until, location, flow_schema)

    except Exception as e:
        print(f"  ⚠ Errore nel file {nome_file}: {e}")
