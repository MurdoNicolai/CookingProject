#!/usr/bin/env python
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import io
import re
import json
import psycopg2
from word2number import w2n
import pandas as pd
import numpy as np
import string
from googleapiclient.http import MediaIoBaseDownload
import unicodedata
import pandas as pd
import numpy as np
import re
def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

def replace_fractions_with_decimals(text):
    # Map for unicode fractions
    unicode_fractions = {
        '¼': 0.25,
        '½': 0.5,
        '¾': 0.75,
        '⅐': 1/7,
        '⅑': 1/9,
        '⅒': 0.1,
        '⅓': 1/3,
        '⅔': 2/3,
        '⅕': 0.2,
        '⅖': 0.4,
        '⅗': 0.6,
        '⅘': 0.8,
        '⅙': 1/6,
        '⅚': 5/6,
        '⅛': 0.125,
        '⅜': 0.375,
        '⅝': 0.625,
        '⅞': 0.875,
    }
    # Replace unicode fractions
    for uf, dec in unicode_fractions.items():
        text = text.replace(uf, str(round(dec, 2)))

    # Replace ascii fractions like 1/2, 3/4, etc.
    def frac_to_dec(match):
        num, denom = match.group(1), match.group(2)
        try:
            return str(round(float(num) / float(denom), 2))
        except ZeroDivisionError:
            return match.group(0)
    # This regex matches fractions like 1/2, 3/4, etc.
    text = re.sub(r'(\d+)\s*/\s*(\d+)', frac_to_dec, text)
    return text


# Function to list all files within a specific folder
def download_file(service, file_id, mimeType):
    if mimeType.startswith('application/vnd.google-apps.'):
        export_mime_type = {
            'application/vnd.google-apps.document': 'application/pdf',
        }.get(mimeType, 'application/pdf')
        request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
    else:
        # Handle binary files
        request = service.files().get_media(fileId=file_id)

    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_data.seek(0)
    return file_data.read()

def organise_file(organise_file_list, service, current_folder_id, path = "/", example_file = False):
    """
    returns a list of files frome a folder and all subfolders adding path:
        organise_file_list - current list of files
        current_folder_id - id of the folder to extract
        example_file - if set to true returns only one file
        return -> list of tuples (file, path)
        """
    page_token = None
    query = f"'{current_folder_id}' in parents"
    while True:
        response = service.files().list(
            q=query,
            pageSize=20,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()
        files = response.get('files', [])
        for file in files:
            if example_file and len(organise_file_list) > 0:
                return organise_file_list
            if file['mimeType'] == "application/vnd.google-apps.folder":
                if file['id'] not in ["1bwfPxsj64eJci9nGFmqxb73421B3Yse2", "1RxbtxvCGETDJcwv1YKXmY5DJ0FoLcJL-"] : #ids of the folders we ignore: core, condiment
                    organise_file_list = organise_file(organise_file_list, service, file['id'], path + file['name'] + "/", example_file)
            elif example_file and file['id'] != "1EEFwn3mUjXrEAI9zi5s9UGP2qaT-YcIP-oRypJUN9gM": #use to get specifique file while testing
                pass
            elif file['mimeType'] == "application/vnd.google-apps.document":
                organise_file_list.append((path, file))
            elif file['mimeType'] == "text/plain":
                organise_file_list.append((path, file))
            else:
                print(f"unrecognised file: {file['mimeType']}")
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return organise_file_list


def get_amount(line, ingredient_found, UnitsOM_dict, recepi_warnings):
    """
    Returns the amount of ingredient in the given line.
    If no amount is found, returns None.
    """
    UnitOM = "None"
    #use dictionary to find the unit of measurement

    line_lower = line.lower()
    UnitOM = ""
    for key, values in UnitsOM_dict.items():
        for unit in values:
            # Match the unit as a whole word, allowing for an optional trailing 's'
            pattern = r'\b' + re.escape(unit) + r's?\b'
            if re.search(pattern, line_lower):
                UnitOM = key
                break
        if UnitOM != "":
            break
    # get ingredient_found AI
    model_name = "./flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    prompt = f"What is the correct unit of measurement of {ingredient_found} in the following line: {line}? (answer only if it's written)"
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length= 200
    )

    outputs = model.generate(**inputs, max_new_tokens=10)

    ai_Unit = tokenizer.decode(outputs[0], skip_special_tokens=True)


    prompt = f"In the following line: {line}. How many {ai_Unit} {ingredient_found} ? (answer with a number when possible, answer 'some' if you really don't know)\n"
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length= 200
    )

    outputs = model.generate(**inputs, max_new_tokens=10)

    amount = tokenizer.decode(outputs[0], skip_special_tokens=True)

    prompt = f"There are {amount} {ai_Unit} {ingredient_found} in the following line? \n {line} \n (answer with yes or no)"
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length= 200
    )

    outputs = model.generate(**inputs, max_new_tokens=10)

    ai_responce = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if ai_responce.lower() == "no" or bool(re.search(r'\d', ai_Unit)):
        prompt = f"There are {amount} {UnitOM} {ingredient_found} in the following line? \n {line} \n (answer with yes or no)"
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length= 200
        )

        outputs = model.generate(**inputs, max_new_tokens=10)
        ai_responce = tokenizer.decode(outputs[0], skip_special_tokens=True)
        if ai_responce.lower() == "no":
            recepi_warnings.append(f"unrecognised amount in {line}")
            return None, None, recepi_warnings
    else:
        UnitOM = ai_Unit
    return amount, UnitOM, recepi_warnings
def get_amount_ingredient(line, UnitsOM_dict, recepi_errors = [], recepi_warnings = []):
    """
    Returns the (ingredient_key, amount, UnitsOM) that was found in give line
    """
    line_lower = remove_accents(line.lower().translate(str.maketrans("", "", string.punctuation)))
    if line_lower.startswith('for the'):
        return 0

    line = replace_fractions_with_decimals(line)
    # get ingredient_found
    model_name = "./flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    prompt = f"Extract the ingredient from the following line: \n{line}"
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length= 300
    )
    outputs = model.generate(**inputs, max_new_tokens=10)
    ingredient_found = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(ingredient_found) >35 or bool(re.search(r'\d', ingredient_found)):
        prompt = f"Find and extract the ingredient from the following line: \n{line}"
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length= 300
        )
        outputs = model.generate(**inputs, max_new_tokens=10)
        ingredient_found = tokenizer.decode(outputs[0], skip_special_tokens=True)


    amount = None
    UnitsOM = "none"
    amount, UnitsOM, recepi_warnings = get_amount(line, ingredient_found, UnitsOM_dict, recepi_warnings)
    if UnitsOM is None or UnitsOM in ingredient_found:
        UnitsOM = ""

    add_ingredient_to_database(ingredient_found)
    return (ingredient_found, amount, UnitsOM, recepi_warnings, recepi_errors)

def split_file_info(service, file, mimeType, errorlist, recepi_warnings):
    """
    gets all the information of a recepi file and seperates them into the future database columns
    file - tuple (path name, file in google drive )
    mimeType - file mimetype
    errorlist - updates errorlist array with any error
    returns -> json dict containing each file info seperated (title, ingredients...) or None if errors
    """
    #get the text
    file_id = file[1]['id']
    if mimeType == 'application/vnd.google-apps.document':
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    else:
        request = service.files().get_media(fileId=file_id)

    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_data.seek(0)

    file_info = file_data.read().decode('utf-8')


    #treat the text
    UnitsOM_dict = { #list of measures for ingredient amounts
    'tablespoon' : ['tablespoon','tbsp' ],
    'teaspoon' : ['teaspoon', 'ts', 'tsp', 't'],
    'large': ['large'] ,
    'medium' : ['medium'],
    'small': ['small'] ,
    'cup': ['cup','c'] ,
    'whole': ['whole'] ,
    'half' : ['half' ],
    'handfull' : ['handfull' ],
    'ounce': ['ounce','oz'] ,
    'quart': ['quart','qt'],
    'gramme' : ['gramme', 'g', 'gram'],
    'slice': ['slice'] ,
    'pound': ['pound','lb'] ,
    'milliliter': ['milliliter','ml'] ,
    'centiliter': ['centiliter','cl'] ,
    'deciliter': ['deciliter','dl'] ,
    'litre': ['liter', 'litre', 'l'],
    'package': ['package'],
    'segment': ['segment'],
    'piece': ['piece'],
    'pinch': ['pinch'],
    'slice': ['slice'],
    'stalk' : ['stalk'],
    'clove' : ['clove'],
    'bunch' : ['bunch'],
    'leaf' : ['leaf', 'leaves'],
    }

    split_line = file_info.splitlines()
    title = file[1]['name'].removesuffix(".txt")
    split_file_dict = {"Title":  title,
                       "Folder_Path": file[0], # get frome parent folders
                       "Geography": None,
                       "Season": None,
                       "Cooking_Time": None,
                       "Total_yield" : None,
                       "Type": None,
                       "Ingredients" : [],
                       "Directions" : None,
                       "Equipment": None,
                       "Notes": None
                       }
    Alternate_names_dict = {
                       "Geography": ["geography"],
                       "Season": ["season"],
                       "Cooking_Time": ["cooking time", "total time", "prep time", "prep"], # (Active, Total)
                       "Total_yield" : ["yield", "serve", "serving", "make"],
                       "Type": ["type"],
                       "Ingredients" : ["ingredient"],
                       "Directions" : ["direction", "method", "preparation", "preparation method", "instruction"], #
                       "Equipment": ["aquipment", "special equipment"],
                       "Notes": [ "note", "variations", "variation", "storage", "comment", "optional"]
                       }
    Cooking_Time_text = ""  #used only in cooking time
    recepi_errors = [f"{file[0]}{file[1]['name']}: {file_id}"]
    line_key = None
    for line in split_line:

        #set correct line key
        line_section = re.match(r'^[\w\s/]+\s*', line)
        if line_section is not None:
            line_section = line_section[0].strip()
            if line_section.endswith(":"):
                line = line[:-1]
            line_section = line_section.rstrip('s').lower()
            if line_section in ["allergens/diet", "diet", "allergen"]:
                line_key = None
                continue
            for key, values in Alternate_names_dict.items():
                if line_section in values:
                    line_key = key
                    if key != "Cooking_Time":
                        line = line[len(line_section):].strip()
                        if line.startswith("s"):
                            line = line[1:]
                        if line.startswith(":"):
                            line = line[1:]
        if line_key is None:
            continue
        elif line_key == "Cooking_Time":
            line_split = line.split()
            if split_file_dict["Cooking_Time"] is None:
                longuest_time = 0 #we assume longuest time in the line is the total time
            else:
                longuest_time = split_file_dict["Cooking_Time"]["Total"]
            for w in range(len(line_split)):
                time = 0
                if line_split[w].isdigit():
                    time = float(line_split[w])
                    if re.sub(r'[^a-zA-Z]', '', line_split[w+1]).lower().startswith("hour"):
                        time *= 60
                        if len(line_split) > w+2:
                            if line_split[w+2].isdigit():
                                time += float(line_split[w+2])
                            elif line_split[w+2] == "and" and line_split[w+3].isdigit():
                                time += float(line_split[w+3])
                    if time > longuest_time:
                        longuest_time = time
            if len(line) > 2:
                Cooking_Time_text = Cooking_Time_text + " | " + line
            split_file_dict["Cooking_Time"] = {"Total": longuest_time, "text": Cooking_Time_text}
        elif line_key == "Ingredients":
            if line.strip() == '':
                continue
            ingredient_found = None

            amount_ingredient = get_amount_ingredient(line, UnitsOM_dict, recepi_errors, recepi_warnings)
            if amount_ingredient == 0:
                continue
            else:
                ingredient_found, amount, UnitsOM, recepi_warnings, recepi_errors = amount_ingredient
            split_file_dict["Ingredients"].append({"ingredient_found" : ingredient_found, "amount" : amount, "UnitsOM" : UnitsOM, "text" : line})
        elif split_file_dict[line_key] is None:
            split_file_dict[line_key] = line
        elif line != "":
            split_file_dict[line_key] = split_file_dict[line_key]+ "\n" + line
    for key in ["Folder_Path", "Directions"]:
        if split_file_dict[key] is None:
            recepi_errors.append(f"{key} missing")
    if  len(recepi_errors) == 1:
        split_file_dict["Ingredients"] = json.dumps(split_file_dict["Ingredients"])
        split_file_dict["Cooking_Time"] = json.dumps(split_file_dict["Cooking_Time"])
        return (split_file_dict)
    errorlist.append(recepi_errors)
    return(None)

def get_all_ingredients():
    """
    Returns a list of all ingredients from the database.
    """
    conn = psycopg2.connect(
        dbname='postgres',
        user='murdo',
        password='n9XLSLHx',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT primary_name FROM ingredients")
    ingredients = cursor.fetchall()
    cursor.close()
    conn.close()
    return [ingredient[0] for ingredient in ingredients]

def add_ingredient_to_database(ingredient):
    """
    Adds an ingredient to the DB if it is not already present.
    """
    conn = psycopg2.connect(
        dbname='postgres',
        user='murdo',
        password='n9XLSLHx',
        host='localhost',
        port='5432'
    )
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id SERIAL PRIMARY KEY,
            primary_name TEXT,
            secondary_names TEXT[],
            nutrition JSONB,
            season TEXT,
            kg_per_litre FLOAT,
            notes TEXT
        )
    ''')
    conn.commit()

    ingredient_list = get_all_ingredients()
    ingredient = remove_accents(ingredient.lower().translate(str.maketrans("", "", string.punctuation)))
    # Use ILIKE for case-insensitive match
    query = """
        SELECT id, primary_name, secondary_names
        FROM ingredients
        WHERE %s = ANY(secondary_names)
    """

    c.execute(query, (ingredient,))
    result = c.fetchall()
    print(result)
    if not result:
        print(f"Ingredient:   {ingredient} \n not found, adding to database.")
        # Insert the ingredient into the database
        for name in ingredient_list:
            if ingredient.lower().find(name.lower()) != -1:
                c.execute('''
                    UPDATE ingredients
                    SET secondary_names = array_append(secondary_names, %s)
                    WHERE primary_name = %s
                ''', (ingredient, name))
                conn.commit()
                c.close()
                conn.close()
                return()
        # If no match found, insert the new ingredient
        model_name = "./flan-t5-large"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        prompt = f"what are the nutritional values of {ingredient} in the format: {{'calories': 0, 'protein': 0, 'fat': 0, 'carbohydrates': 0}}"
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length= 20000
        )

        outputs = model.generate(**inputs, max_new_tokens=10)

        primary_name = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"\n\n here: {primary_name}")
        if primary_name in ingredient_list:
            if ingredient.lower().find(primary_name.lower()) != -1:
                c.execute('''
                    UPDATE ingredients
                    SET secondary_names = array_append(secondary_names, %s)
                    WHERE primary_name = %s
                ''', (ingredient, primary_name))
                conn.commit()
                c.close()
                conn.close()
                return()
        c.execute('''
            INSERT INTO ingredients (primary_name, secondary_names)
            VALUES (%s, %s)
        ''', (primary_name, [ingredient]))
    #     print(f"Added ingredient: {primary_name} ")
    # print(f"with secondary name: {ingredient} to the database.")
    conn.commit()
    c.close()
    conn.close()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Authenticate and create the Drive API service
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('drive', 'v3', credentials=creds)


conn = psycopg2.connect(
    dbname='postgres',
    user='murdo',
    password='n9XLSLHx',
    host='localhost',
    port='5432'
)
c = conn.cursor()
folder_id = '1hnJVeCp34UuG8tgK8CMFrtURvcmlRuEc' #the database folder id on the drive

organised_file_list_for_db = []

c.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id SERIAL PRIMARY KEY,
        title TEXT,
        folder_path TEXT,
        geography TEXT,
        season TEXT,
        cooking_time TEXT,
        total_yield TEXT,
        type TEXT,
        ingredients TEXT,
        directions TEXT,
        special_equipment TEXT,
        notes TEXT,
        UNIQUE(title, folder_path)
    )
''')
conn.commit()

# all_files = organise_file(organised_file_list_for_db, service, folder_id)
all_files = organise_file(organised_file_list_for_db, service, folder_id, example_file = True)
# all_files = []


#use to get unlisted ingredients

file_sections = []
UnitsOM_types = []
errorlist = []
recepi_warnings = []

for file in all_files:
    file_id = file[1]['id']
    name = file[1]['name']
    mimeType = file[1]['mimeType']

    file_info = split_file_info(service, file, mimeType, errorlist, recepi_warnings) #this is None if there was an error

    try:
        c.execute('''
            INSERT INTO recipes (title, folder_path, geography, season, cooking_time, Total_yield, type, ingredients, directions, special_equipment, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (title, folder_path) DO UPDATE SET
                geography = EXCLUDED.geography,
                season = EXCLUDED.season,
                cooking_time = EXCLUDED.cooking_time,
                total_yield = EXCLUDED.total_yield,
                type = EXCLUDED.type,
                ingredients = EXCLUDED.ingredients,
                directions = EXCLUDED.directions,
                special_equipment = EXCLUDED.special_equipment,
                notes = EXCLUDED.notes
        ''', (file_info['Title'],
              file_info['Folder_Path'],
              file_info['Geography'],
              file_info['Season'],
              file_info['Cooking_Time'],
              file_info['Total_yield'],
              file_info['Type'],
              file_info['Ingredients'],
              file_info['Directions'],
              file_info['Equipment'],
              file_info['Notes']))

        conn.commit()
        print(f"Saved or replaced {name} in the database.")

    except Exception as e:
        print(f"Failed to save {name}: {e}")

    # use for debugging file_info
    if file_info is not None:
        for key, value in file_info.items():
            print(f"{key}: {value}")

if file_sections != []:
    with open("file_sections.txt", 'w') as file:
        for item in file_sections:
            try:
                file.write(f"{item}\n")
            except:
                print(item)

if UnitsOM_types != []:
    with open("UnitsOM_types.txt", 'w') as file:
        for item in UnitsOM_types:
            try:
                file.write(f"{item}\n")
            except:
                print(item)

if errorlist != []:
    with open("errorlist.txt", 'w') as file1, open("ingredient_errors.txt", 'w') as file2:
        for item in errorlist:
            if any("unrecognised ingredient in" in error for error in item):
                try:
                    file2.write(f"{item}\n")
                except:
                    print(item)
            else:
                try:
                    file1.write(f"{item}\n")
                except:
                    print(item)

if recepi_warnings != []:
    with open("recepi_warnings.txt", 'w') as file:
        for item in recepi_warnings:
            try:
                file.write(f"{item}\n")
            except:
                print(item)
# Close the database connection
c.close()
conn.close()
