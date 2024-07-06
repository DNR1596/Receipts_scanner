import pandas as pd
import os 
import time as t
import numpy as np
import easyocr as ocr
from PIL import Image
import pillow_heif as ph
import cv2
from datetime import date as dt
import re
import matplotlib as plt

reader = ocr.Reader(['it'])




class ImageFormatControl ():
    def HeicChecker(Path):
        OutPath = os.path.pardir(Path)
        _, ext = os.path.splitext(Path)
        if ext.lower() == '.heic':
            return True

    def HeicConverter(input_path, output_path=None):
        try:
            # Controlla se il file di input esiste
            if not os.path.isfile(input_path):
                raise FileNotFoundError(f"File non trovato: {input_path}")
            print(f"Trovato file HEIC: {input_path}")

            # Se l'output_path non è specificato, usa la stessa directory e nome del file di input con estensione .jpg
            if output_path is None:
                base, _ = os.path.splitext(input_path)
                output_path = f"{base}.jpg"
            
            # Ottieni la directory del file di output
            output_dir = os.path.dirname(output_path)
            
            # Crea la directory di output
            os.makedirs(output_dir, exist_ok=True)
            print(f"Directory di output pronta: {output_dir}")

            # Carica l'immagine HEIC
            heif_file = ph.read_heif(input_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )

            # Salva l'immagine come JPG
            image.save(output_path, format="JPEG")
            print(f"Immagine salvata come: {output_path}")

            # Verifica se il file di output è stato creato
            if os.path.isfile(output_path):
                print(f"File JPG creato con successo: {output_path}")
            else:
                print(f"Errore nella creazione del file JPG: {output_path}")

        except Exception as e:
            print(f"Errore durante la conversione: {e}")









def Acq_Bill(path):
    

    # Caricamento dell'immagine
    image_path = path
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Utilizzo del filtro Gaussian per ridurre il rumore
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Applicazione di una soglia binaria
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Ridimensionamento dell'immagine
    scale_percent = 150  # Percentuale di scala
    width = int(binary.shape[1] * scale_percent / 100)
    height = int(binary.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(binary, dim, interpolation=cv2.INTER_LINEAR)




    
    
    text = reader.readtext(resized, detail = 0)
    return text

class Clean():
    def SubString(text):
        #Identifica la porzione di testo da mantenere sottoforma di lista
        text2 = []
            
        for i in range(len(text)):
            text[i] = str.upper(text[i])                

        for i in range(len(text)):
            if 'PREZZO' in text[i]:
                text1 = text[i+1:]
                break
        for i in range(len(text1)):
            
            if 'SUB' in text1[i]:
                text1 = text1[:i]
                break
            elif 'TOTALE' in text1[i]:
                text1 = text1[:i-1]
                break
        for i in text1:
            if 'EUR' not in i:
                text2.append(i)
        return text2
    
    def FinString(text2):
        #identifica i pattern dell'iva e non li appende in una lista nuova
        iva_pattern = re.compile(r'\d{1,2}%')
        iva_pattern2 = re.compile(r'\d{1,2}X')
        iva_pattern3 = re.compile(r'\bVI[A-Za-z]\b')
        iva = iva_pattern.findall(str(text2))
        iva2 = iva_pattern2.findall(str(text2))
        iva3 = iva_pattern3.findall(str(text2))
        iva.append('VI*')
        iva.extend(iva2)
        iva.extend(iva3)
        del iva2
        del iva3 
        
        text3 = []
        for el in text2:
            if el not in iva:
                text3.append(el)

        Prodotto = ''
        for el in text3[:]:
            el = el.strip()
            el2 = ''.join(el.split())
            el2 = el2.replace(',', '.')
            if el == 'X' or 'SCONTO' in el or '~' in el:
                text3.remove(el)
            try:
                float(el2)
                text3.remove(el)
            except ValueError:
                Prodotto = ''
        return text3
        
    def prices(text2):
        formatted_prices = []
        temp_price = ""
        for item in text2: #identifica i prezzi
            # Rimuove gli spazi
            item = item.strip()
            item2 = ''.join(item.split())
            
            if Clean.is_valid_price(item2):
                # Aggiunge direttamente i prezzi validi alla lista dei prezzi formattati
                formatted_prices.append(f"{float(item2.replace(',', '.')):,.2f}")
                temp_price = ""
            elif item2.replace(',', '').replace('.', '').isdigit():
                # Se l'elemento è una parte di un numero, aggiungilo al prezzo temporaneo
                if temp_price:
                    temp_price += item2
                    # Controlla se la concatenazione è un prezzo valido
                    if Clean.is_valid_price(temp_price):
                        formatted_prices.append(f"{float(temp_price.replace(',', '.')):,.2f}")
                        temp_price = ""
                else:
                    temp_price = item2
            else:
                temp_price = ""

        return formatted_prices


    def is_valid_price(price):
        # Definisce la regex per verificare se il prezzo è nella forma corretta
        pattern = re.compile(r'^\d{1,2}[.,]\d{2}$')
        return bool(pattern.match(price))    

class Adj():
    def Product(Prodotto):

        for i in range(len(Prodotto)):
            print('-------------------------------------------------------------------')
            Prod_ok = input(
            f'''il prodotto scansionato è {Prodotto[i]}, \nriscrivere il prodotto in maniera corretta, \nse il prodotto è corretto premere invio \nProdotto corretto: ''')
            if Prod_ok != '':
                Prodotto[i] = Prod_ok
        print('-------------------------------------------------------------------')
        print('Di seguito: Indice) Prodotto')
        
        for i in range(len(Prodotto)):
            print(f'{i}) {Prodotto[i]}')
        Indexstr = input("Inserire l'indice dell'elemento che si vuole rimuovere, altrimenti se non sono presenti errori premere invio.")

        if Indexstr != '':
            IndexList = [int(el) for el in Indexstr.split(",")]
            IndexList = sorted(IndexList, reverse=True)
            for i in IndexList:
                Prodotto.pop(i)
            del IndexList


        return Prodotto
    
    def Prices(Prod = list, Prezzo = list):
        Prodlen = len(Prod)
        Pricelen = len(Prezzo)
        if Prodlen > Pricelen:
            diff = Prodlen - Pricelen
            Prezzo.extend('*' for i in range(diff))
        print(
        '''correggere eventuali incorrette assegnazioni prodotto prezzo: \n
        in particolare correggere il prezzo dove è presente "*"
        scrivere i prezzi sostitutivi nel formato: indice, prezzo del prodotto
        non preoccuparsi se i prezzi scaleranno, il sistema lo supporta''')
        print('-------------------------------------------------------------------')
        print(f'Di seguito indicati: Indice) Prodotto : Prezzo')
        for _ in range(len(Prod)):
            print(f'{_} ) {Prod[_]} : {Prezzo[_]}')
        CorrectedList = (input('inserire i valori da rimuovere').split(','))
        TupleCorrectedList = []
        while len(CorrectedList) > 1:
            index = CorrectedList[0]
            price = CorrectedList[1]
            TupleCorrectedList.append((int(index), float(price)))
            CorrectedList.pop(0)
            CorrectedList.pop(0)
            
            
        for i in range(len(TupleCorrectedList)):
            index = TupleCorrectedList[i][0]
            price = TupleCorrectedList[i][1]
            Prezzo.insert(index+1,price)
            Prezzo.remove('*')
        return Prezzo

def SameLenght(L1, L2):
    if len(L1) != len(L2):
        return False
    return True

def Unification(L1, L2):
    Finlist = []
    for i in range(len(L1)):
        Finlist.append((L1[i], (L2[i])))
    return Finlist

class Dataframe():
    def Create(L):
        df = pd.DataFrame(L, columns=['Prodotti',f'{giorno_formattato}'])
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df

    def Merge(df1, ListToDf):
        df2 = pd.DataFrame(ListToDf, columns=['Prodotti', f'Prova2'])
        df1 = df1.loc[:, ~df.columns.str.contains('^Unnamed')]
        df1 = pd.concat([df1, df2], axis=0, ignore_index=True)
        return df1

            

print('Welcome to the auto-record of your bills')
print('-----------------------------------')
valid = True
while valid:
    User = input('Vuoi iniziare una nuova tabella o aggiornarne una già esistente? Rispondi con N o U').upper()
    giorno = dt.today()
    giorno_formattato = giorno.strftime('%d/%m/%Y')
    if User == 'N':
        Path1 = input(r"Per piacere inserire il percorso dell'immagine di seguito: ").removeprefix('"').removesuffix('"')
        if ImageFormatControl.HeicChecker(Path1):
            Path2 = ImageFormatControl.HeicConverter(Path1)
        text = Acq_Bill(Path2)
        MidProd = Clean.SubString(text) #Testo suddiviso ma da pulire
        Prodotto = Clean.FinString(MidProd) #Testo Finale dei prodotti
        Prezzo = Clean.prices(MidProd) #Prezzi ottenuti tramite le regex
        FinProd = Adj.Product(Prodotto) #Permette all'utente di correggere eventuali erorri di identificazione nei Prodotti
        FinPrezzo = Adj.Prices(FinProd, Prezzo) #Permette all'utente di correggere eventuali errori di identificazione nei Prezzi
        Check = SameLenght(FinProd, FinPrezzo)
        print(Check)
        Finlist = Unification(FinProd, FinPrezzo)
        df = Dataframe.Create(Finlist)
        df.to_csv("PrimoScontrino.csv")
        valid = False
    elif User == 'U':
        Path1 = input("Per piacere inserire il percorso dell'immagine di seguito: ").removeprefix('"').removesuffix('"')
        if ImageFormatControl.HeicChecker(Path1):
            Path2 = ImageFormatControl.HeicConverter(Path1)
        df = pd.read_csv(r'D:\Informatica\Python\PrimoScontrino.csv')
        text = Acq_Bill(Path2)
        MidProd = Clean.SubString(text)
        Prodotto = Clean.FinString(MidProd)
        Prezzo = Clean.prices(MidProd)
        FinProd = Adj.Product(Prodotto)
        FinPrezzo = Adj.Prices(FinProd, Prezzo)
        Check = SameLenght(FinProd, FinPrezzo)
        print(Check)
        Finlist = Unification(FinProd, FinPrezzo)
    
        df = Dataframe.Merge(df, Finlist).to_csv('Tentativo1.cvs')
        valid = False
    else:
        print(f'la risposta: {User} non corrisponde né a N né a U, si prega di specificare')
        valid = True