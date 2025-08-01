import pandas as pd
import os

# Cartella contenente i file originali verticali
cartella_input = 'raw'
# Cartella dove salvare i file CSV convertiti orizzontalmente
cartella_output = 'csv_files'

# Crea la cartella di output se non esiste
os.makedirs(cartella_output, exist_ok=True)

# Scorri tutti i file nella cartella input
for filename in os.listdir(cartella_input):
    if filename.endswith('.xlsx'):
        percorso_file = os.path.join(cartella_input, filename)
        try:
            # Legge il file come dataframe verticale
            df = pd.read_excel(percorso_file, header=None)
            
            # Filtra righe valide (con almeno 2 colonne)
            df = df.dropna(subset=[0, 1], how='any')

            # Crea un dizionario con chiave = colonna 0, valore = colonna 1
            dati = dict(zip(df[0], df[1]))

            # Converte in dataframe orizzontale
            df_orizzontale = pd.DataFrame([dati])

            # Percorso del nuovo file CSV
            nome_csv = os.path.splitext(filename)[0] + '.csv'
            percorso_output = os.path.join(cartella_output, nome_csv)

            # Salva il file CSV
            df_orizzontale.to_csv(percorso_output, index=False)

            print(f"✅ Convertito: {filename}")
        except Exception as e:
            print(f"❌ Errore con {filename}: {e}")