from fastapi import APIRouter, HTTPException
import psycopg2
import psycopg2.extras
import uuid
from database import get_db_connection
from schemas.admin import (
    TavoloCreate, 
    StaffCreate, 
    FoodAndBeverageCreate, 
    MagazzinoCreate
)

router = APIRouter(
    prefix="/api/admin",
    tags=["Pannello Admin"]
)

# A. AGGIUNGI UN NUOVO TAVOLO
@router.post("/tavoli")
def crea_tavolo(payload: TavoloCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Errore di connessione al database")
    
    cursor = conn.cursor()
    try:
        id_tavolo = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO tavoli (id_tavolo, numero_tavolo, coperti, stato)
            VALUES (%s, %s, %s, %s);
            """,
            (id_tavolo, payload.numero_tavolo, payload.coperti, payload.stato)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "messaggio": "Tavolo creato con successo", "id_tavolo": id_tavolo}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    # B. AGGIUNGI UN NUOVO DIPENDENTE (STAFF)
@router.post("/staff")
def crea_staff(payload: StaffCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Errore di connessione al database")
    
    cursor = conn.cursor()
    try:
        id_utente = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO staff (
                id_utente, nome, cognome, data_di_nascita, codice_fiscale,
                attestato_haccp, attestato_corsi_sicurezza, iban, contratto, ruolo, attivo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                id_utente, payload.nome, payload.cognome, payload.data_di_nascita,
                payload.codice_fiscale, payload.attestato_haccp, payload.attestato_corsi_sicurezza,
                payload.iban, payload.contratto, payload.ruolo, payload.attivo
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "messaggio": "Membro dello staff registrato", "id_utente": id_utente}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    # C. AGGIUNGI PIATTO O BEVANDA AL MENU
@router.post("/menu")
def crea_prodotto_menu(payload: FoodAndBeverageCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Impossibile connettersi al database")
    
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        id_fb = str(uuid.uuid4())

        # 1. Inseriamo la voce di menu principale
        cursor.execute(
            """
            INSERT INTO food_and_beverage (id_fb, nome, prezzo, categoria, allergeni, id_prodotto_magazzino, attivo)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (
                id_fb,
                payload.nome,
                payload.prezzo,
                payload.categoria,
                payload.allergeni,
                payload.id_prodotto_magazzino,
                payload.attivo
            )
        )

        # 2. Inserimento opzionale nel ricettario (se il pop-up sul frontend è stato compilato)
        if payload.ricetta:
            for ingrediente in payload.ricetta:
                id_ricetta = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO ricettario (id_ricetta, id_prodotto, id_fb, quantità_usata)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (
                        id_ricetta,
                        ingrediente.id_prodotto,
                        id_fb,
                        ingrediente.quantità_usata
                    )
                )

        conn.commit()

        return {
            "status": "success",
            "messaggio": "Prodotto creato con successo!",
            "id_fb": id_fb,
            "ricetta_collegata": bool(payload.ricetta)
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Errore nell'inserimento menu/ricetta: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
# D. AGGIUNGI PRODOTTO IN MAGAZZINO
@router.post("/magazzino")
def crea_articolo_magazzino(payload: MagazzinoCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Errore di connessione al database")
    
    cursor = conn.cursor()
    try:
        id_prodotto = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO magazzino (
                id_prodotto, nome_prodotto, giacenza_totale, unità_misura, soglia_minima, attivo
            ) VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                id_prodotto, payload.nome_prodotto, payload.giacenza_totale,
                payload.unità_misura, payload.soglia_minima, payload.attivo
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success", "messaggio": "Prodotto aggiunto al magazzino", "id_prodotto": id_prodotto}
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))