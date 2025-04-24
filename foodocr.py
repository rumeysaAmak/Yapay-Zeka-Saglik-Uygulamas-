import os
import cv2
import json
import gradio as gr
from paddleocr import PaddleOCR
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# OCR işlemi için PaddleOCR'ı başlat
def initialize_ocr():
    return PaddleOCR(ocr_version='PP-OCRv4', use_angle_cls=True)

# LLM'i başlat ve şablonu oluştur
def initialize_llm(api_key, temperature):
    os.environ["OPENAI_API_KEY"] = api_key
    llm = OpenAI(temperature=temperature)
    template = """
    Extract food labels from the given list {question} and represent them in JSON format. 
    Include the following keys:
    1. "Name": The name or description of the food item.
    2. "Quantity": The amount or serving size (e.g., "100g," "1 cup," "1 slice").
    3. "Calories": The energy content in kilocalories (kcal).
    4. "Total Fat": The total fat content in grams.
    5. "Saturated Fat": The saturated fat content in grams.
    6. "Trans Fat": The trans fat content in grams.
    7. "Cholesterol": The cholesterol content in milligrams.
    8. "Sodium": The sodium content in milligrams.
    9. "Total Carbohydrates": The total carbohydrate content in grams.
    10. "Dietary Fiber": The dietary fiber content in grams.
    11. "Sugars": The sugar content in grams.
    12. "Protein": The protein content in grams.
    13. "Vitamins and Minerals": Specific vitamins (e.g., Vitamin C, Vitamin A) and minerals (e.g., Iron, Calcium) with their respective amounts.
    14. "Allergens": Any allergens present (e.g., "Contains milk," "May contain nuts").
    15. "Ingredients": A list of ingredients used in the food product.
    16. "Barcode":
    -If you do not have a value for a key in your retrieved JSON dictionary, please put "N/A
    """
    prompt = PromptTemplate(template=template, input_variables=["question"])
    return LLMChain(prompt=prompt, llm=llm)

# OCR ve LLM işlemini gerçekleştiren ana fonksiyon
def perform_ocr(img, temperature, api_key):
    # OCR ve LLM başlat
    ocr = initialize_ocr()
    llm_chain = initialize_llm(api_key, temperature)

    # Görüntü üzerinde OCR işlemi yap
    result = ocr.ocr(img)

    # Tanınan metinleri saklamak için boş bir liste oluştur
    recognized_texts = []

    # Tanınan metinleri listeye ekle ve görüntü üzerinde kutucuklar çiz
    for line in result:
        for word in line:
            text = word[1][0]
            recognized_texts.append(text)
            bbox = word[0]
            overlay = img.copy()
            cv2.rectangle(overlay, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[2][0]), int(bbox[2][1])), (255, 255, 0), -1)
            cv2.addWeighted(overlay, 100 / 255, img, 1 - 100 / 255, 0, img)

    # Tanınan metinleri Langchain ile işle
    langchain_output = llm_chain.run(recognized_texts)

    return img, langchain_output  # Görüntü ve işlenmiş metinlerin çıktısını döndür

# Gradio arayüzünü tanımla
def create_interface():
    api_key_input = gr.Textbox(label="OpenAI API Key", type="password", info="Enter your OpenAI API key here.")
    temperature_slider = gr.Slider(minimum=0, maximum=2, label="Temperature", info="Adjust temperature (0-2)")

    inputs = [gr.Image(), temperature_slider, api_key_input]
    outputs = [gr.Image(), gr.Textbox(type="text", label="Food Labels")]  # JSON çıktısını bir metin kutusunda göster

    interface = gr.Interface(
        fn=perform_ocr,
        inputs=inputs,
        outputs=outputs,
        title="Eurofins Multi-language Food Label OCR",
        description="Upload an image to perform OCR.",
        allow_flagging=False
    )

    # Gradio arayüzünü başlat
    interface.launch(share=True, debug=True)

# Ana program
if __name__ == "__main__":
    create_interface()
