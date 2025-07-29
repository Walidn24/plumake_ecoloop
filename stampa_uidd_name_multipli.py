import os
import csv

# ✅ Percorso alla cartella CSV
cartella_csv = r'C:\Users\walid\Desktop\csv-convertiti-02'
numero_file_da_leggere = 10

# ✅ Elenco dei primi N file .csv
file_csv = [f for f in os.listdir(cartella_csv) if f.endswith('.csv')][:numero_file_da_leggere]

# ✅ Leggi ogni file e stampa UUID e Name
for nome_file in file_csv:
    percorso_file = os.path.join(cartella_csv, nome_file)
    print(f"\n📄 File: {nome_file}")
    try:
        with open(percorso_file, mode='r', encoding='utf-8') as f:
            lettore = csv.DictReader(f)
            for riga in lettore:
                uuid = riga.get('UUID')
                name = riga.get('Name')
                if uuid and name:
                    print(f"  ➤ UUID: {uuid}, Name: {name}")
    except Exception as e:
        print(f"  ⚠ Errore nel file {nome_file}: {e}")
