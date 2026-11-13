from http.client import HTTPException

from fastapi import FastAPI, HTTPException  # Importazione di FastAPI e HTTPException per la gestione degli errori
from database import get_db_connection  # Importazione della funzione per ottenere la connessione al database
import psycopg2.extras #importante per far diventare i risultati delle query JSON
app = FastAPI(title="Roots ERP API", description="Api per la gestione del sistema ERP Roots", version="0.0.2", contact={"name": "Enrico"})  # Creazione dell'istanza FastAPI con titolo, descrizione e versione, e nome autore temporaneo
@app.get("/")  # Definizione di un endpoint GET per la root dell'applicazione
def check_status():
    return {"status": "online", "message": "Roots ERP server is running"}  # Restituisce lo stato dell'applicazione come JSon


from routers import tavoli  #Modulo relativo ai tavoli in cartella routers
from routers import comande  #Modulo relativo alle comande in cartella routers
from routers import admin  #Modulo relativo all'admin in cartella routers

app.include_router(tavoli.router) # Includo il router per i tavoli
app.include_router(comande.router)  # Includo il router per le comande
app.include_router(admin.router)  # Includo il router per l'admin

