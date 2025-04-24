from flask import Flask, request, jsonify, render_template, request, redirect, url_for
import pandas as pd
import pickle
from PIL import Image
import pytesseract
import re
import cv2
import numpy as np
import os
import json
from flask_cors import CORS
from flask import Flask, render_template, request
import database 
import sqlite3

app = Flask(__name__)
CORS(app) 
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
with open('model.pickle', 'rb') as file:  # Modeli yükleyin
    model = pickle.load(file)

with open('label_encoders.pickle', 'rb') as file:  # Etiket kodlayıcılarını yükleyin
    label_encoders = pickle.load(file)


@app.route('/iletisim', methods=['POST'])
def contact():
    name = request.form['isim']
    phone = request.form['tel']
    email = request.form['mail']
    subject = request.form['konu']
    message = request.form['mesaj']
    
    # Veritabanına ekleme
    database.insert_contact(name, phone, email, subject, message)

    return "Mesajınız başarıyla gönderildi!"

@app.route('/contacts')
def show_contacts():
    conn = sqlite3.connect('contact_form.db')
    c = conn.cursor()
    c.execute("SELECT * FROM contacts")
    contacts = c.fetchall()
    conn.close()

    return render_template('contacts.html', contacts=contacts)

def transform_feature(feature, value):
    le = label_encoders.get(feature)
    if le is not None:
        if value in le.classes_:
            return le.transform([value])[0]
        else:
            unseen_label = max(le.transform(le.classes_)) + 1
            return unseen_label
    return value

def predict_allergens(main_ingredient, sweetener, fat_oil, seasoning):
    main_ingredient = transform_feature('Main Ingredient', main_ingredient)
    sweetener = transform_feature('Sweetener', sweetener)
    fat_oil = transform_feature('Fat/Oil', fat_oil)
    seasoning = transform_feature('Seasoning', seasoning)

    if None in [main_ingredient, sweetener, fat_oil, seasoning]:
        return {'error': 'Geçersiz giriş yaptınız: bilinmeyen etiketler içeriyor'}

    input_data = pd.DataFrame([[main_ingredient, sweetener, fat_oil, seasoning]], 
                              columns=['Main Ingredient', 'Sweetener', 'Fat/Oil', 'Seasoning'])

    prediction = model.predict(input_data)[0]

    return {
        'prediction': int(prediction)
    }

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

with open('allergen_info.json', 'r') as f:
    allergen_info = json.load(f)["AllergenInfo"]

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    new_width = 800
    aspect_ratio = new_width / float(blurred_image.shape[1])
    new_height = int(blurred_image.shape[0] * aspect_ratio)
    resized_image = cv2.resize(blurred_image, (new_width, new_height))
    processed_image_path = 'processed_image.jpg'
    cv2.imwrite(processed_image_path, resized_image)
    return processed_image_path

def extract_text_from_image(image_path):
    custom_config = r'--oem 3 -l eng'
    extracted_text = pytesseract.image_to_string(image_path, config=custom_config)
    return extracted_text

def process_text(txt):
    nutrition_pat = {
        "Calories": r'(?<=Calories)[\s.,\(\)|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Energy": r'(?<=Energy)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Sodium": r'(?<=Sodium)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "TotalFat": r'(?<=Total Fat)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "SaturatedFat": r'(?<=Saturated Fat)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "TransFat": r'(?<=Trans Fat)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Cholesterol": r'(?<=Cholesterol)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "TotalCarb": r'(?<=Total Carb)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Carbohydrate": r'(?<=Carbohydrate)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Calcium": r'(?<=Calcium)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Protein": r'(?<=Protein)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})',
        "Sugars": r'(?<=Sugars)[\s.,\(\)\|a-zA-Z]*(\d+.{0,1}\d*\w{0,2})'
    }

    nutrient_out = {}

    for pat in nutrition_pat:
        tt = None
        for i in txt.split("\n"):
            i = re.sub(r'\(.*\)', '', i)
            i = re.sub(r'[^\w.]', ' ', i)
            pp = re.compile(nutrition_pat[pat])
            res = re.search(pp, i)
            if res:
                tt = res.group(1)
        if tt:
            tt = re.sub(r'[^\d.]', '', tt)
        nutrient_out[pat] = tt

    if nutrient_out["Energy"]:
        nutrient_out["Calories"] = nutrient_out["Energy"]
        del nutrient_out["Energy"]

    ingredients = re.sub(r'[^\w,. ]', ' ', txt)
    ingredients = re.sub(r'[\d]+\.*[\d]*', ',', ingredients)
    ingredients = re.sub(r'and', ',', ingredients)
    ingredients = re.sub(r'from|From', '', ingredients)
    ingredients = re.sub(r'[ ]+', ' ', ingredients)

    ingredients_regex = r'(Ingredients|INGREDIENTS|ingredients):*([\w\[\]\(\),\s]*)[\n]*'
    res = re.search(ingredients_regex, ingredients)
    ingredients = []

    for i in list(range(1, 3))[::-1]:
        try:
            ingredients = res.group(i)
            break
        except:
            continue

    if ingredients:
        ingredients = ingredients.split(",")
        ingredients = list(map(lambda x: re.sub(r'[\s+]', ' ', x), ingredients))
        ingredients = list(filter(len, ingredients))
        ingredients = list(filter(lambda x: not re.match(r'[ ]+$', x), ingredients))

    allergens = re.sub(r'[\[\]\(\)]', ',', txt)
    allergens = re.sub(r'and', ',', allergens)

    allergen_regex = r'(Contains|CONTAINS|May Contain|contain)(.*)'
    res = re.search(allergen_regex, allergens)
    allergens = []

    for i in list(range(1, 3))[::-1]:
        try:
            allergens = res.group(i)
            break
        except:
            continue

    if allergens:
        allergens = allergens.split(",")
        allergens = list(map(lambda x: re.sub(r'[\s+]', ' ', x), allergens))
        allergens = list(filter(len, allergens))
        allergens = list(filter(lambda x: not re.match(r'[ ]+$', x), allergens))

    allergens = [item.lower() for item in allergens]

    result = {
        "nutrients": nutrient_out,
        "ingredients": ingredients,
        "allergens": allergens
    }

    return result

@app.route('/get_allergen_info', methods=['GET'])
def get_allergen_info():
    return jsonify(allergen_info)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    main_ingredient = data.get('Main Ingredient')
    sweetener = data.get('Sweetener')
    fat_oil = data.get('Fat/Oil')
    seasoning = data.get('Seasoning')

    result = predict_allergens(main_ingredient, sweetener, fat_oil, seasoning)
    return jsonify(result)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        processed_image_path = preprocess_image(file_path)
        extracted_text = extract_text_from_image(processed_image_path)
        processed_text = process_text(extracted_text)

        allergens_found = []
        for allergen in processed_text['allergens']:
            for known_allergen in allergen_info.keys():
                if known_allergen.lower() in allergen:
                    allergens_found.append({
                        "allergen": known_allergen,
                        "description": allergen_info[known_allergen]['description'],
                        "symptoms": allergen_info[known_allergen]['symptoms']
                    })

        return jsonify({
            "nutrients": processed_text['nutrients'],
            "ingredients": processed_text['ingredients'],
            "allergens": allergens_found
        })



if __name__ == '__main__':
    app.run(debug=True)
