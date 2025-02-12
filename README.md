## 🎓 Databastyper

I det här repositoriet finns mina filer och kod samlat för databastyper inom NoSQL. 

### Streamlit

Här finns även min webb-app hos Streamlit där jag visar data hanterad via MongoDB som är en dokumentationsdatabas. I appen visar jag data för produkter som behöver beställas.

### Vad som krävs i installation och import

För att kunna köra Streamlit tillsammans med MongoDB krävs det:

* import pandas as pd
* import json
* from pymongo.mongo_client import MongoClient
* from pymongo.server_api import ServerApi
* import urllib.parse 
* import streamlit as st
* import time
* import matplotlib.pyplot as plt

### Filer för de olika databastyperna

* Redis: här använder jag filen orders.csv i sitt ursprungsformat.
  
* MongoDB: här använder jag en sammanslagning av products.csv och suppliers.json till collections samt konverterar Pandas DataFrame till en lista av dictionaries (JSON-liknande struktur) som kan hantera data mot databasen i MongoDB.
  
* Neo4j: här har jag skapat nya csv-filer från ursprungsdatan movies.json för att bättre kunna arbeta med datan och strukturen till min grafdatabas i Neo4j. De nya filerna är:
    * actors.csv
    * actors_movies.csv
    * directors.csv
    * genres.csv
    * genres_movies.csv
    * movies.csv
_______________________________________________________________________________________________

*Mycket nöje!* 🪄
