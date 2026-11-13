from http.client import HTTPException

from fastapi import APIRouter

from database import get_db_connection

router= APIRouter(
    prefix="/tavoli",
    tags=["Tavoli"]
)


@router.get("/")  # Definizione di un endpoint GET per ottenere i dati dei tavoli
def leggi_tavoli():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail= 'Impossibile connettersi al database')  # Solleva un'eccezione HTTP se la connessione al database fallisce
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # Creazione di un cursore per eseguire le query, con i risultati restituiti come dizionari
        cursor.execute('SELECT* FROM tavoli;')  # Esecuzione della query per ottenere tutti i dati dalla tabella "tavoli"
        tavoli = cursor.fetchall()  # Recupero di tutti i risultati della query
        cursor.close()  # Chiusura del cursore
        conn.close()  # Chiusura della connessione al database
        return tavoli  # Restituisce i dati dei tavoli come JSON
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Solleva un'eccezione HTTP se si verifica un errore durante l'esecuzione della query
@router.get("/api/menu")
def leggi_menu():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Impossibile connettersi al database")
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Recuperiamo solo i prodotti visibili in sala
        cursor.execute("SELECT * FROM food_and_beverage WHERE attivo = TRUE;")
        menu = cursor.fetchall()
        cursor.close()
        conn.close()
        return menu
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import psycopg2
import psycopg2.extras
from database import get_db_connection

# --- 1. MODELLI PYDANTIC (Validazione automatica dei dati in ingresso) ---

class DettaglioComandaInput(BaseModel):
    id_prodotto: str       # Corrisponde all'id_fb della tabella food_and_beverage
    quantità: int
    note_aggiuntive: Optional[str] = None
    prezzo_vendita: float  # Sovrascrivibile per varianti o piatti jolly

class ComandaCreateInput(BaseModel):
    id_tavolo: str
    id_utente: str         # Cameriere che batte la comanda
    dettagli: List[DettaglioComandaInput]