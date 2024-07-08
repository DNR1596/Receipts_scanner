import pandas as pd
import os
import easyocr as ocr
from PIL import Image
import pillow_heif as ph
import cv2
from datetime import date as dt
import re


reader = ocr.Reader(['it'])




class ImageFormatControl ():
    def HeicChecker(Path):
        
        _, ext = os.path.splitext(Path)
        if ext.lower() == '.heic':
            return True

    def HeicConverter(input_path, output_path=None):
        try:
            
            if not os.path.isfile(input_path):
                raise FileNotFoundError(f"File not found: {input_path}")
            

            
            if output_path is None:
                base, _ = os.path.splitext(input_path)
                output_path = f"{base}.jpg"
            
            
            output_dir = os.path.dirname(output_path)
            
            
            os.makedirs(output_dir, exist_ok=True)
            

            
            heif_file = ph.read_heif(input_path)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )

            
            image.save(output_path, format="JPEG")
            print(f"Image saved as: {output_path}")

            
            if os.path.isfile(output_path):
                print(f"File jpg succesfully Created: {output_path}")
            else:
                print(f"Error encountered in creating jpg file: {output_path}")
            return output_path

        except Exception as e:
            print(f"Could not convert: {e}")









def Acq_Bill(path):
    

    
    image_path = path
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    scale_percent = 150  
    width = int(binary.shape[1] * scale_percent / 100)
    height = int(binary.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(binary, dim, interpolation=cv2.INTER_LINEAR)




    
    
    text = reader.readtext(resized, detail = 0)
    #avoiding details for easier string manipulation
    return text

class Clean():
    def SubString(text):

        # Splits the receipts, taking only the part where prices are displayed
        # works only in Italian up to now due to variables being called
        # Prezzo (price), Sub, Totale (Total)
        # can be adapted to languages if changed
        
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

        # identify iva (italian tax on products), str in format price and other distractor.
        # avoid appending it to a list composed of only producs and prices

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

        #Identify Prices trhough a regex equation and is able to recognise prices such as '2','99' if Ocr fails to group them up into a single string
        formatted_prices = []
        temp_price = ""
        for item in text2: 
            
            item = item.strip()
            item2 = ''.join(item.split())
            
            if Clean.is_valid_price(item2):
                
                formatted_prices.append(f"{float(item2.replace(',', '.')):,.2f}")
                temp_price = ""
            elif item2.replace(',', '').replace('.', '').isdigit():
                
                if temp_price:
                    temp_price += item2
                    
                    if Clean.is_valid_price(temp_price):
                        formatted_prices.append(f"{float(temp_price.replace(',', '.')):,.2f}")
                        temp_price = ""
                else:
                    temp_price = item2
            else:
                temp_price = ""

        return formatted_prices


    def is_valid_price(price):
        
        pattern = re.compile(r'^\d{1,2}[.,]\d{2}$')
        return bool(pattern.match(price))    

class Adj():
    def Product(Prod):

        for i in range(len(Prod)):
            print('-------------------------------------------------------------------')
            Prod_ok = input(
            f'''recognised product: {Prod[i]}, \ncorrect product if written wrong, \nif it is correct press enter: ''')
            if Prod_ok != '':
                Prod[i] = Prod_ok
        print('-------------------------------------------------------------------')
        print('Index) Product')
        
        for i in range(len(Prod)):
            print(f'{i}) {Prod[i]}')
        Indexstr = input("Write index number of the element you want to remove, if everything is right press enter.\n")

        if Indexstr != '':
            IndexList = [int(el) for el in Indexstr.split(",")]
            IndexList = sorted(IndexList, reverse=True)
            for i in IndexList:
                Prod.pop(i)
            del IndexList


        return Prod
    
    def Prices(Prod = list, Price = list):
        Prodlen = len(Prod)
        Pricelen = len(Price)
        if Prodlen > Pricelen:
            diff = Prodlen - Pricelen
            Price.extend('*' for i in range(diff))
        print(
        '''check price linked to the product, \n add price if "*" is used, write new prices in the following format:\n index, price, ... if the price missing is assigned to a product wich already has a price\n don't worry, price will climb downwards''')
        print('-------------------------------------------------------------------')
        print(f'Indice) Product : Price')
        for _ in range(len(Prod)):
            print(f'{_} ) {Prod[_]} : {Price[_]}')
        CorrectedList = (input('Value to change').split(','))
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
            Price.insert(index+1,price)
            Price.remove('*')
        return Price

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
        df = pd.DataFrame(L, columns=['Product',f'{formatted_day}'])
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df

    def Merge(df1, ListToDf):
        df2 = pd.DataFrame(ListToDf, columns=['Product', f'{formatted_day}'])
        df1 = df1.loc[:, ~df.columns.str.contains('^Unnamed')]
        df1 = pd.concat([df1, df2], axis=0, ignore_index=True)
        return df1

            

print('Welcome to the auto-record of your bills')
print('-----------------------------------')
valid = True
while valid:
    User = input('Please type N if you want to create a new table for receipts or U if you want to update one already existing ').upper()
    day = dt.today()
    formatted_day = day.strftime('%d/%m/%Y')
    if User == 'N':
        Path1 = input(r'Please insert path: ')
        Path1 = Path1.removeprefix("'").removesuffix("'")
        
        if ImageFormatControl.HeicChecker(Path1):
            Path2 = ImageFormatControl.HeicConverter(Path1)
        else:
            Path2 = Path1
        text = Acq_Bill(Path2)
        MidProd = Clean.SubString(text) #Testo suddiviso ma da pulire
        Product = Clean.FinString(MidProd) #Testo Finale dei prodotti
        Price = Clean.prices(MidProd) #Prezzi ottenuti tramite le regex
        FinProd = Adj.Product(Product) #Permette all'utente di correggere eventuali erorri di identificazione nei Prodotti
        FinPrice = Adj.Prices(FinProd, Price) #Permette all'utente di correggere eventuali errori di identificazione nei Prezzi
        Check = SameLenght(FinProd, FinPrice)
        print(Check)
        Finlist = Unification(FinProd, FinPrice)
        df = Dataframe.Create(Finlist)
        df.to_csv("FirstReceipt.csv")
        valid = False
    elif User == 'U':
        Path1 = input(r"Please insert path:").removeprefix('"').removesuffix('"')
        if ImageFormatControl.HeicChecker(Path1):
            Path2 = ImageFormatControl.HeicConverter(Path1)
        else:
            Path2 = Path1
        df = pd.read_csv(r"D:\Informatica\Python\Scontrini\FirstReceipt.csv")
        text = Acq_Bill(Path2)
        MidProd = Clean.SubString(text)
        Product = Clean.FinString(MidProd)
        Price = Clean.prices(MidProd)
        FinProd = Adj.Product(Product)
        FinPrice = Adj.Prices(FinProd, Price)
        Check = SameLenght(FinProd, FinPrice)
        print(Check)
        Finlist = Unification(FinProd, FinPrice)
    
        df = Dataframe.Merge(df, Finlist).to_csv(r"D:\Informatica\Python\Scontrini\FirstReceipt.csv")
        valid = False
    else:
        print(f'{User} does not correpond to either N or U, please try again')
        valid = True