from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from database import get_db_connection
from schemas.admin import ComandaCreateInput
from schemas.admin import ComandaChiudiInput
import uuid
import psycopg2
import psycopg2.extras
router= APIRouter(
    prefix="/api/comande",
    tags=["Comande"]
)

# --- 2. ENDPOINT POST: INSERIMENTO COMANDA COMPLETA ---

@router.post("/")
def crea_comanda(payload: ComandaCreateInput):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Impossibile connettersi al database")
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # A. Generiamo l'UUID e l'orario per la testa della comanda
        id_comanda = str(uuid.uuid4())
        orario_apertura = datetime.now()
        stato_comanda = "aperta"

        # B. Inseriamo il record principale in 'comande'
        cursor.execute(
            """
            INSERT INTO comande (id_comanda, orario_apertura, stato, id_tavolo, id_utente)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (id_comanda, orario_apertura, stato_comanda, payload.id_tavolo, payload.id_utente)
        )

        # C. Inseriamo ogni singola riga nella tabella 'dettaglio_comande'
        for dettaglio in payload.dettagli:
            id_dettaglio = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO dettaglio_comande (id_dettaglio, id_comanda, id_prodotto, quantità, note_aggiuntive, prezzo_vendita)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                (
                    id_dettaglio,
                    id_comanda,
                    dettaglio.id_prodotto,
                    dettaglio.quantità,
                    dettaglio.note_aggiuntive,
                    dettaglio.prezzo_vendita
                )
            )

        # D. Aggiorniamo automaticamente lo stato del tavolo su 'occupato'
        cursor.execute(
            "UPDATE tavoli SET stato = 'occupato' WHERE id_tavolo = %s;",
            (payload.id_tavolo,)
        )

        # E. CONFERMA TRANSAZIONE: Scriviamo tutto definitivamente sul DB
        conn.commit()
        
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "messaggio": "Comanda inviata con successo in cucina!",
            "id_comanda": id_comanda
        }

    except Exception as e:
        # Se si verifica un qualsiasi errore, annulliamo tutte le operazioni pendenti
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Errore durante l'invio della comanda: {str(e)}")
    from fastapi import FastAPI, HTTPException

      #  F. PROCESSO CHIUSURA DELLA COMANDA E CALCOLO DEL CONTO TOTALE  

@router.post("/chiudi")
def chiudi_comanda(payload: ComandaChiudiInput):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Impossibile connettersi al database")
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # 1. Calcolo del totale della comanda 
        cursor.execute(
            """
            SELECT COALESCE(SUM(quantità * prezzo_vendita), 0.0) AS totale_conto
            FROM dettaglio_comande
            WHERE id_comanda = %s;
            """,
            (payload.id_comanda,)
        )
        risultato = cursor.fetchone()
        totale_conto = risultato["totale_conto"] if risultato else 0.0

        # 2. Aggiornamento stato comanda + recupero immediato di id_tavolo con RETURNING
        cursor.execute(
            """
            UPDATE comande
            SET stato = 'chiusa',
                orario_chiusura = %s,
                totale = %s,
                metodo_pagamento = %s
            WHERE id_comanda = %s AND stato = 'aperta'
            RETURNING id_tavolo;
            """,
            (datetime.now(), totale_conto, payload.metodo_pagamento, payload.id_comanda)
        )
        
        comanda_aggiornata = cursor.fetchone()
        
        # Se non restituisce nulla, la comanda non esisteva o era già chiusa
        if not comanda_aggiornata:
            conn.rollback()
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail="Comanda non trovata o già chiusa."
            )

        id_tavolo = comanda_aggiornata["id_tavolo"]

        # 3. Liberazione automatica del tavolo
        cursor.execute(
            """
            UPDATE tavoli
            SET stato = 'libero'
            WHERE id_tavolo = %s;
            """,
            (id_tavolo,)
        )

        # 4. COMMIT ATOMICO: Se tutte e tre le operazioni riescono
        conn.commit()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "messaggio": "Comanda chiusa con successo e tavolo liberato",
            "id_comanda": payload.id_comanda,
            "id_tavolo": id_tavolo,
            "totale_incassato": float(totale_conto)
        }

    except HTTPException as http_ex:
    
        raise http_ex
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Errore nella chiusura della comanda: {str(e)}")