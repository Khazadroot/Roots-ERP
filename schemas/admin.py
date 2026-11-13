# MODELLI PYDANTIC PER IL PANNELLO ADMIN

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
import uuid
import psycopg2
import psycopg2.extras
from database import get_db_connection


class IngredienteRicettaInput(BaseModel):
    id_prodotto: str  # ID della materia prima in magazzino (magazzino.id_prodotto)
    quantità_usata: float = Field(..., alias="quantita_usata")  # Supporta sia con che senza accento da JSON

    class Config:
        populate_by_name = True
class DettaglioComandaInput(BaseModel):
    id_prodotto: str       # Corrisponde all'id_fb della tabella food_and_beverage
    quantità: int
    note_aggiuntive: Optional[str] = None
    prezzo_vendita: float  # Sovrascrivibile per varianti o piatti jolly

class ComandaCreateInput(BaseModel):
    id_tavolo: str
    id_utente: str         # Cameriere che batte la comanda
    dettagli: list[DettaglioComandaInput]
    
class TavoloCreate(BaseModel):
    numero_tavolo: int
    coperti: int
    stato: Optional[str] = "libero"

class StaffCreate(BaseModel):
    nome: str
    cognome: str
    data_di_nascita: Optional[date] = None
    codice_fiscale: Optional[str] = None
    attestato_haccp: Optional[str] = None
    attestato_corsi_sicurezza: Optional[str] = None
    iban: Optional[str] = None
    contratto: Optional[str] = None
    ruolo: str  # es. "cameriere", "chef de rang", "amministratore"
    attivo: Optional[bool] = True

class FoodAndBeverageCreate(BaseModel):
    nome: str
    prezzo: float
    categoria: str  # es. "Primi", "Bevande", "Dolci"
    allergeni: Optional[str] = None
    id_prodotto_magazzino: Optional[str] = None  # Collegamento opzionale al magazzino
    attivo: Optional[bool] = True
    ricetta: Optional[List[IngredienteRicettaInput]] = None

class MagazzinoCreate(BaseModel):
    nome_prodotto: str
    giacenza_totale: float
    unità_misura: str  # es. "KG", "LT", "PZ"
    soglia_minima: int
    attivo: Optional[bool] = True

class ComandaChiudiInput(BaseModel):
    id_comanda: str
    metodo_pagamento: Optional[str] = "contanti"