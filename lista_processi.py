import logging
import olca_ipc as ipc
import olca_schema as o

def count_processes():
    # Configura logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Inizializza il client IPC
    try:
        client = ipc.Client(8080)  # Cambia porta se necessario
        logging.info("Connessione al server IPC riuscita.")
    except Exception as e:
        logging.error(f"Errore nella connessione al server IPC: {e}")
        return

    # Ottieni tutti i processi
    try:
        process_list = client.get_descriptors(o.Process)
        num_processes = len(process_list)

        logging.info(f"Numero totale di processi nel database: {num_processes}")
        print(f"\nNumero totale di processi nel database OpenLCA: {num_processes}")

        # Se vuoi vedere anche i primi 10 processi:
        print("\nLista dei primi processi trovati (massimo 10):")
        for i, process in enumerate(process_list[:10]):
            print(f"{i+1}. {process.name} (ID: {process.id})  - Categoria: {process.category}")

    except Exception as e:
        logging.error(f"Errore durante il recupero dei processi: {e}")
        return

    # ⚠️ Rimuoviamo questa riga perché non esiste:
    # client.close()
    logging.info("Fine elaborazione.")

# Esegui il metodo
if __name__ == "__main__":
    count_processes()
