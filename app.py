from flask import Flask, render_template, request, send_from_directory
import google.generativeai as genai
import os
import shutil
from transformers import pipeline
from PIL import Image
from werkzeug.utils import secure_filename #

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
genai.configure(api_key="AIzaSyALSKKUK2CHfalVYT9tKzxtBCa7EBO6Gbk")
model = genai.GenerativeModel('gemini-pro')

@app.route("/")
def home():
    return render_template("test.html")

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/predict", methods=["POST", "GET"])
def predict():
    
    def delete_and_create_uploads():
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['UPLOAD_FOLDER'])  

    if request.method == "POST":
        delete_and_create_uploads()

        image_prompts = []
        images = request.files.getlist('imageUpload') 
        if images:
            print("I'm inside!")
            for image in images:
                filename = secure_filename(image.filename)  # Sanitize filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img = Image.open(image_path)
                image_prompts.append(pipe(img)[0]['generated_text'])
                
        choice = request.form.get("type")
        input_text = request.form.get("content")
        text_prompts = input_text.split(',')
        prompts = image_prompts + text_prompts
        print(prompts)
        
        if(choice=="poem"):
            response = model.generate_content(f"Generate a poem with the following prompts: {prompts}")
        else:
            response = model.generate_content(f"Generate a short story with the following prompts: {prompts}")
        result=True

    uploaded_images = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in os.listdir(app.config['UPLOAD_FOLDER'])]
    print(uploaded_images)

    return render_template("test.html", choice=choice, result=result, response=response, text=input_text, uploaded_images=uploaded_images)

if __name__=="__main__":
    app.run(debug=True)

