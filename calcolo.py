import olca_ipc as ipc
import olca_schema as o
import psycopg2
import time

def salva_su_postgres(process_id, method, impact_name, amount, unit):
    try:
        conn = psycopg2.connect(
            dbname="csv_db",
            user="walid",
            password="walidpass",
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

if __name__ == "__main__":
    # inserisci qui il tuo ID processo
    esempio_id = "00172b09-8b56-40eb-a9a8-d0e03dd59aa1"
    esegui_calcolo(esempio_id)
