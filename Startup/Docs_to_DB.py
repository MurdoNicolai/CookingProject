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
            elif example_file and file['id'] != "1695kRv72ThqhOzKKaX1190kZZYMzUIpZMu8EtQxO2xU": #use to get specifique file qhile testing
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


def get_all_ingredients():
    """
    Returns a list of all ingredients in 'gredient names.xlsx' + all Flavor Bombs in 'All flavour bomb names.xlsx',
    with any text inside parentheses removed and trailing 's' characters removed.
    """
    try:
        ingredients = pd.read_excel("All ingredient names.xlsx").values
        ingredients = ingredients.flatten()
        ingredients = np.array([re.sub(r'\(.*?\)', '', x).lower().rstrip('s') for x in ingredients if isinstance(x, str)]).tolist()
    except FileNotFoundError:
        print("The file 'All ingredient names.xlsx' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        Flavor_bombs = pd.read_excel("All flavour bomb names.xlsx").values
        Flavor_bombs = Flavor_bombs.flatten()
        Flavor_bombs = np.array([re.sub(r'\(.*?\)', '', x).lower().rstrip('s') for x in Flavor_bombs if isinstance(x, str)]).tolist()
    except FileNotFoundError:
        print("The file 'All flavour bomb names.xlsx' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return ingredients + Flavor_bombs


def get_amount(line, ingrediant_key, weight_dict, recepi_warnings):
    """
    Returns the amount of ingredient in the given line.
    If no amount is found, returns None.
    """
    # get weight type
    line_split = line.lower().split()
    amount = 0
    weight = None
    extra_info = None
    for w in range(len(line_split)):
        word = line_split[w]
        # print(word) #debugging
    print(weight)
    if amount == 0:
        amount = 0.0

    return None
def get_amount_ingrediant(line, weight_dict, ingrediant_list, recepi_errors = [], recepi_warnings = []):
    """
    Returns the (ingredient_key, amount, weight) that was found in give line
    """
    line_lower = remove_accents(line.lower().translate(str.maketrans("", "", string.punctuation)))
    if line_lower.startswith('for the'):
        return 0

    # get ingrediant_key
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
    ingrediant_key = tokenizer.decode(outputs[0], skip_special_tokens=True)

    if len(ingrediant_key) >35:
        prompt = f"Find and extract the ingredient from the following line: \n{line}"
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length= 300
        )
        outputs = model.generate(**inputs, max_new_tokens=10)
        ingrediant_key = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"line: {line}") #debugging

    print(f"ingrediant_key_AI: {ingrediant_key}") #debugging

    prompt = f"What amount of {ingrediant_key} is in the folowing line: \n{line}"
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length= 200
    )
    outputs = model.generate(**inputs, max_new_tokens=10)
    amount = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"ingrediant_amount_AI: {amount}") #debugging
    weight = "none"
    get_amount(amount, ingrediant_key, weight_dict, recepi_warnings)
    return (ingrediant_key, amount, weight)

def split_file_info(service, file, mimeType, ingrediant_list, errorlist, recepi_warnings):
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
    weight_dict = { #list of measures for ingrediant amounts
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
    'gramme' : ['gramme', 'g'],
    'slice': ['slice'] ,
    'pound': ['pound','lb'] ,
    'milliliters': ['milliliters','ml'] ,
    'centiliters': ['centiliters','cl'] ,
    'deciliter': ['deciliter','dl'] ,
    'liter': ['liter', 'l'],
    'package': ['package'],
    'slice': ['slice'] ,
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
        line_section = re.match(r'^[\w\s/]+\s*:', line)
        if line_section is not None:
            line_section = line_section[0].strip()[:-1]
            line_section = line_section.rstrip('s').lower()
            if line_section in ["allergens/diet", "diet", "allergen"]:
                line_key = None
                continue
            for key, values in Alternate_names_dict.items():
                if line_section in values:
                    line_key = key
                    if key != "Cooking_Time":
                        line = line.split(":", 1)[1].strip()
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
            ingrediant_key = None

            amount_ingredient = get_amount_ingrediant(line, weight_dict, ingrediant_list, recepi_errors, recepi_warnings)
            if amount_ingredient == 0:
                continue
            else:
                ingrediant_key, amount,  weight = amount_ingredient
            split_file_dict["Ingredients"].append({"ingrediant_key" : ingrediant_key, "amount" : amount, "weight" : weight, "text" : line})
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

def get_unlisted_ingrediants(service, file_id, mimeType, ingrediant_list, file_sections = None, weight_types = None):
    """
    gets ingrediants not listed in all ingrediants name that are present in recepies
    file_id - id of the file in google drive
    mimeType - file mimetype
    returns -> array of all line not having ingrediants prelisted
    """
    #get the text
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


    split_line = file_info.splitlines()

    isingrediant = False
    new_ingrediants = []
    for entry in split_line[1:]:
        entry_section = re.match(r'^[\w\s]+\s*:', entry)
        if entry_section is not None:
            entry_section = entry_section[0]
            if file_sections is not None and (entry_section not in file_sections):
                file_sections.append(entry_section)

        if entry_section == "Ingredients:":
            isingrediant = True
            continue
        elif entry_section is not None and isingrediant:
            isingrediant = False

        if isingrediant:
            entry = entry.lower()
            if all(ingrediant not in entry for ingrediant in ingrediant_list):
                new_ingrediants.append(entry)
            weight_type = None
            for word in entry.split():
                if not word.isdigit() and word != "*":
                    weight_type = word
                    break
            if weight_types is not None and (weight_type not in weight_types):
                weight_types.append(weight_type)
    return new_ingrediants
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

#use to get unlisted ingrediants
unlisted_ingrediants = []
ingrediant_list = get_all_ingredients()
file_sections = []
weight_types = []
errorlist = []
recepi_warnings = []

for file in all_files:
    file_id = file[1]['id']
    name = file[1]['name']
    mimeType = file[1]['mimeType']
    #use to get unlisted ingrediants
    # unlisted_ingrediants.extend(get_unlisted_ingrediants(service, file_id, mimeType, ingrediant_list, file_sections, weight_types))

    file_info = split_file_info(service, file, mimeType, ingrediant_list, errorlist, recepi_warnings) #this is None if there was an error

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
    # if file_info is not None:
    #     for key, value in file_info.items():
    #         print(f"{key}: {value}")

if unlisted_ingrediants != []:
    with open("unlisted ingrediants.txt", 'w') as file:
        for item in unlisted_ingrediants:
            try:
                file.write(f"{item}\n")
            except:
                print(item)
if file_sections != []:
    with open("file_sections.txt", 'w') as file:
        for item in file_sections:
            try:
                file.write(f"{item}\n")
            except:
                print(item)

if weight_types != []:
    with open("weight_types.txt", 'w') as file:
        for item in weight_types:
            try:
                file.write(f"{item}\n")
            except:
                print(item)

if errorlist != []:
    with open("errorlist.txt", 'w') as file1, open("ingredient_errors.txt", 'w') as file2:
        for item in errorlist:
            if any("unrecognised ingrediant in" in error for error in item):
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
