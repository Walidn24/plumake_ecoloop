import olca_ipc as ipc
import olca_schema as o
import psycopg2
import time
import os
import csv

# === CONFIG ===
cartella_csv = r'C:\Users\walid\Desktop\csv-convertiti-02'
numero_file_da_leggere = 10

# === FUNZIONE PER SALVARE I RISULTATI ===
def salva_calcolo(id_flux, ef, unita, valore):
    conn = None
    try:
        print("🔌 Connessione a PostgreSQL...")
        conn = psycopg2.connect(
            dbname="csv_db",
            user="postgres",
            password="walid123",
            host="localhost",
            port="5433"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO impact_results (process_id, impact_name, unit, amount)
            VALUES (%s, %s, %s, %s)
        """, (id_flux, ef, unita, valore))
        conn.commit()
        cur.close()
        print(f"✅ Salvato: {ef} = {valore} {unita}")
    except Exception as e:
        print("❌ Errore nel salvataggio:", e)
    finally:
        if conn:
            conn.close()

# === FUNZIONE PER ESEGUIRE IL CALCOLO ===
def esegui_calcolo(process_id):
  try:
    client = ipc.Client(8080)
    # Prova una chiamata semplice per vedere se OpenLCA è acceso
    _ = client.ping()
  except Exception as e:
    print("⚠ OpenLCA non è avviato o non risponde:", e)
    return

    try:
        process = client.get(o.Ref(o.RefType.PROCESS, process_id))
        if not process:
            print(f"❌ Processo non trovato: {process_id}")
            return

        setup = o.CalculationSetup()
        setup.calculation_type = o.CalculationType.SIMPLE_CALCULATION
        setup.model_type = o.ModelType.PRODUCT_SYSTEM
        setup.ref_flow = process.quantitative_reference
        setup.processes = [process_id]
        setup.amount = 1.0
        setup.impact_method = client.find(o.ImpactMethod, "EF v3.0")

        print(f"⚙ Calcolo per processo {process.name}...")
        result = client.calculate(setup)
        time.sleep(1)

        for impact in result.impact_results:
            salva_calcolo(process_id, impact.impact_category.name, impact.impact_category.reference_unit, impact.value)

        print(f"✅ Calcolo completato: {process.name}")
        client.dispose(result)

    except Exception as e:
        print(f"❌ Errore nel calcolo {process_id}:", e)

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Avvio programma automatico...\n")
    file_csv = [f for f in os.listdir(cartella_csv) if f.endswith('.csv')][:numero_file_da_leggere]

    for nome_file in file_csv:
        percorso = os.path.join(cartella_csv, nome_file)
        print(f"\n📄 CSV: {nome_file}")
        try:
            with open(percorso, mode='r', encoding='utf-8') as f:
                lettore = csv.DictReader(f)
                for riga in lettore:
                    uuid = riga.get('UUID')
                    name = riga.get('Name')
                    if uuid and name:
                        print(f"  ➤ {name} ({uuid})")
                        esegui_calcolo(uuid)
        except Exception as e:
            print(f"⚠ Errore in {nome_file}: {e}")
