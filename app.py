import pandas as pd
import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse 
import streamlit as st
import time
import matplotlib.pyplot as plt

# Läs in CSV och JSON
products_df = pd.read_csv('products.csv', encoding='utf-8')

with open('suppliers.json', 'r', encoding='utf-8') as f:
    suppliers_data = json.load(f)

suppliers_df = pd.DataFrame(suppliers_data)

# Slå ihop data
merged_data = pd.merge(products_df, suppliers_df, on='SupplierID', how='inner')

# Anslut till MongoDB
# Läs lösenordet från secrets.toml
PWD = st.secrets["mongo"]["password"]
encoded_pwd = urllib.parse.quote_plus(PWD)
uri = f'mongodb+srv://nicolinalottsfeldtdata24hel:{encoded_pwd}@cluster0.xljmi.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))

# Testa kopplingen
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Konvertera den sammanslagna DataFrame till en lista
merged_json = merged_data.to_dict(orient='records')

# Definiera databasen och samlingarna
db = client['Dokumentdatabas']
collection = db['Kunskapskontroll 1 Databastyper']
suppliers = db['suppliers']

# Rensa gamla samlingar för att förhindra dubbletter
collection.delete_many({})  # Rensar alla gamla dokument i produktsamlingen
suppliers.delete_many({})  # Rensar leverantörsdatan för att säkerställa att det inte finns dubbletter

# Lägg till nya leverantörer, kontrollera först om det redan finns
suppliers.insert_many(suppliers_data)

# Förhindra duplicering av produkter genom att lägga till dem om de inte redan finns
for product in merged_json:
    # Kontrollera om produkten redan finns i samlingen
    existing_product = collection.find_one({
        'ProductName': product['ProductName'], 
        'SupplierID': product['SupplierID']
    })

    if not existing_product:
        # Lägg till produkt om den inte finns
        collection.insert_one(product)
    else:
        # Om produkten finns, uppdatera den
        collection.update_one(
            {'ProductName': product['ProductName'], 'SupplierID': product['SupplierID']},
            {'$set': product},
            upsert=True  # Om produkten inte finns, lägg till den; om den finns, uppdatera den
        )

# Kör en MongoDB-aggregering för att hitta produkter som behöver beställas
result = collection.aggregate([
    {
        '$match': {
            '$expr': {
                '$gt': ['$ReorderLevel', {'$add': ['$UnitsInStock', '$UnitsOnOrder']}]
            }
        }
    },
    {
        '$lookup': {
            'from': 'suppliers',
            'localField': 'SupplierID',
            'foreignField': 'SupplierID',
            'as': 'supplier_info'
        }
    },
    { '$unwind': '$supplier_info' },
    {
        '$project': {
            '_id': 0,
            'ProductName': 1,
            'ReorderLevel': 1,
            'UnitsInStock': 1,
            'UnitsOnOrder': 1,
            'SupplierName': '$supplier_info.CompanyName',
            'ContactName': '$supplier_info.ContactName',
            'ContactPhone': '$supplier_info.Phone'
        }
    }
])

# Visa resultaten i Streamlit
result_list = list(result)

# Lägg till en bild som visas överst
image_path = r"C:\Users\kolcz\Downloads\christmas-wallpaper-2009590_1280.jpg"  
st.image(image_path, use_container_width=True)

# Lägg till en titel
st.title('Produkter som behöver beställas')

# Kod för att visa produkter 
if result_list:
    product_names = [doc['ProductName'] for doc in result_list]
    selected_product = st.selectbox("Välj en produkt:", product_names)

    # Spinner medan man väntar på att produkten ska visas
    with st.spinner("Väntar på att produkten ska visas..."):
        time.sleep(2.5)

    # Hitta den valda produkten i result_list
    selected_doc = next(doc for doc in result_list if doc['ProductName'] == selected_product)

    # Visa produktinfo
    st.subheader(f"Produkt: {selected_doc['ProductName']}")

    # Skapa flikar för att välja vilken sektion som ska visas
    view_option = st.selectbox(
        "Välj vad du vill se:",
        ["Produktens Status", "Leverantörens Kontaktuppgifter", "Visa All Information"],
        index=0  # Standardval
    )

    if view_option == "Produktens Status":
        # Skapa en tabell med produktinformation (Reorder Level, Units in Stock, etc.)
        table_data = {
            "Egenskap": ['Reorder Level', 'Units in Stock', 'Units on Order'],
            "Värde": [selected_doc['ReorderLevel'], selected_doc['UnitsInStock'], selected_doc['UnitsOnOrder']]
        }

        # Omvandla till en DataFrame för att visa i en tabell
        table_df = pd.DataFrame(table_data)

        # Visa tabellen
        st.table(table_df)

        # Skapa en stapelgraf för produktens status
        fig, ax = plt.subplots()
        labels = ['Reorder Level', 'Units in Stock', 'Units on Order']
        values = [selected_doc['ReorderLevel'], selected_doc['UnitsInStock'], selected_doc['UnitsOnOrder']]

        ax.bar(labels, values, color=['red', 'green', 'blue'])

        # Lägg till etiketter och titel
        ax.set_ylabel('Antal')
        ax.set_title(f"Visualisering för {selected_doc['ProductName']}")

        # Visa stapeldiagrammet i Streamlit
        st.pyplot(fig)

    elif view_option == "Visa All Information":
        # Visa all information i en kombinerad vy (Produktens status, Diagram och Leverantörsinformation)
        st.subheader("Produktens Status")
        table_data = {
            "Egenskap": ['Reorder Level', 'Units in Stock', 'Units on Order'],
            "Värde": [selected_doc['ReorderLevel'], selected_doc['UnitsInStock'], selected_doc['UnitsOnOrder']]
        }
        table_df = pd.DataFrame(table_data)
        st.table(table_df)

        # Visa leverantörsinformation
        st.subheader("Leverantörsinformation")
        st.write(f"Leverantör: {selected_doc['SupplierName']}")
        st.write(f"Kontaktperson: {selected_doc['ContactName']}")
        st.write(f"Telefonnummer: {selected_doc['ContactPhone']}")

        # Skapa en stapelgraf för produktens status
        st.subheader("Diagram")
        fig, ax = plt.subplots()
        labels = ['Reorder Level', 'Units in Stock', 'Units on Order']
        values = [selected_doc['ReorderLevel'], selected_doc['UnitsInStock'], selected_doc['UnitsOnOrder']]

        ax.bar(labels, values, color=['red', 'green', 'blue'])

        ax.set_ylabel('Antal')
        ax.set_title(f"Visualisering för {selected_doc['ProductName']}")

        st.pyplot(fig)

    elif view_option == "Leverantörens Kontaktuppgifter":
        # Visa leverantörens kontaktuppgifter
        st.subheader("Leverantörens Kontaktuppgifter")
        st.write(f"Leverantör: {selected_doc['SupplierName']}")
        st.write(f"Kontaktperson: {selected_doc['ContactName']}")
        st.write(f"Telefonnummer: {selected_doc['ContactPhone']}")

else:
    st.write("Inga produkter behöver beställas just nu.")
