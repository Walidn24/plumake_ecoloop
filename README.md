# plumake_ecoloop

Questo programma prende tutti i dati OpenLCA e converte a CSV e popola tutti dati per un postgresql database

sviluppato da Isuru Fernando e Walid Jebali

## Instruzioni

-  [Installare OpenLCA](#installare-openlca-sul-linux)
-  [creare virtual env per python](#creare-virtual-machine)
-  [installare tutte le dipendenze e librerie python](#installare-dipendenze)
-  [installare il database postgresql e creare le tabelle di arrivo](#installazione-postgresql)
-  importare i database ecoinvent e agribalyse in openLCA
-  esportare i csv
-  mettere i csv in una cartella e lanciare lo script che esegue i calcoli e salva i risultati sul database

### Installare OpenLCA sul Linux

Scarica tar.gz: [link](https://www.openlca.org/download/)

> nome file scaricato può essere non simile a quello che vedi sul commando e
> devi entrare sulla cartella dove hai scaricato prima di eseguire il comando

```
tar -zxvf openLCA_mkl_Linux_x64_2.5.0_2025-06-16.tar.gz
```

Cambiare a posizione permenete

```
sudo mv ~/Downloads/openLCA /opt/openLCA
```

Aggiungere openLCA al path

```
echo 'export PATH=$PATH:/opt/openLCA' >> ~/.bashrc
source ~/.bashrc
```

Apri openLCA

```
openLCA
```

dopo aver aperto openLCA, andate sul file in alto sinistra. Premete e ci dovra essere scritto import. Lo premete vi comparirà una piccola finestrina con scritto file -> import -> file. Premete sul file e caricate file ecoinvent.zolca

![alt text](image.png)

Quando hai caricato vedrai database come sotto

![alt text](image-2.png)

premete due volte su file che vi comparirà sul openLCA, dopo aver premuto vi comparirà usa schermata per update database. Premete su OK

Ripremete su file zolca vi comparirà delle cartelle, voi andate sul cartella process e premete tasto destro -> export, dopo vi comparirà una schermata per convertire tutti file in formato Excel.

![alt text](image-3.png)

premete sul Next, vi comparirà una altra schermata che vi da la possibilità di decidere quale cartella vuoi convertire. Noi nel nostro caso convertiamo tutti🤯💥.

dopo aver selezionato tutte le cartelle da convertire, dovete premere su Browse per dove vuoi esportare
![alt text](image-4.png)

poi premete finish e aspettate un pò

> Più il file lungo più ci mette tanto a convertire nell nostro caso ci e voluto 3 ore

![alt text](image-5.png)

### Creare virtual machine

#### in Linux

```
python3 -m venv .venv
```

attivare virtual machine

```
source .venv/bin/activate
```

### Installare dipendenze

> Devi attivare virtual machine prima di installazione dipendenze

```
pip install -r requirements.txt
```

### Installazione Postgresql

```
apt install postgresql
```

Automizzare configurazione repository

```
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
```

per più dettagli: [link](https://www.postgresql.org/download/linux/ubuntu/)

### Struttura dei CSV deve seguire la struttura qui sotto

```
UUID,
Name,
Category,
Description,
Version,
Tags,
Valid from,
Valid until,
Location,
Flow schema
```
