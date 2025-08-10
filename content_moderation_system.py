# Code for Content Moderation System using OpenAI API

# Install dependencies (could also pip install in terminal from requirements.txt)
from openai import OpenAI
import pandas as pd
from openpyxl import Workbook
import json
import os
import pdfplumber
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
OPENAI_API_URL = os.getenv('OPENAI_API_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Function to analyze the content
def analyze_content(text):
    prompt = f"""
    Task: Please carefully analyze the following content for discriminatory, biased, or unethical language.
    When you analyze the following content, be mindful within the context of modern social discourse. Consider that this content may be viewed by a diverse group of individuals from various backgrounds. Be mindful of the potential for harm or offense.
    The content should be assessed based on the following categories:
    - Racial bias
    - Gender bias
    - Religious bias
    - Political bias
    - General unethical behavior

    Additionally, provide:
    1. A severity rating from 1 to 10, where 1 represents minimal bias and 10 represents extreme bias.
    2. A detailed explanation of the flagged content, including which specific biases or unethical behavior is present.
    3. Suggested improvements for making the content more inclusive and respectful. 
    4. If applicable, categorize the type of bias detected (e.g., racial, gender, political, etc.).
    """
    client = OpenAI(
    base_url=OPENAI_API_URL,
    api_key=OPENAI_API_KEY,  # required, but unused
)

    response = client.chat.completions.create(
        model='llama3.2-vision',
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]
    )


    return response.choices[0].message.content.strip()

# Function to set the severity of flagged content based on keywords (customize as needed)
def set_severity_flagged(content):
    if 'hate' in content.lower():
        return 10  # Very high severity
    elif 'offensive' in content.lower():
        return 7  # Medium severity
    elif 'discriminatory' in content.lower():
        return 8  # High severity
    else:
        return 1  # Low severity

# Function to create an Excel report with flagged content and results
def create_excel_report(data):
    wb = Workbook()
    ws = wb.active
    ws.append(["Content", "Severity", "Category", "Explanation"])  # Column headers
    
    # Loop through the data and add each entry to the Excel sheet
    for row in data:
        ws.append([row['content'], row['severity'], row['category'], row['explanation']])
    
    # Save the report
    wb.save("output_report.xlsx")

# Function to process input from a text file
def process_text_file(input_file):
    with open(input_file, 'r') as f:
        content = f.read()  # Read the entire text file content
    
    # Call the content moderation function for each chunk (or full text)
    analysis = analyze_content(content)
    severity = set_severity_flagged(content)
    
    # Create results and save to Excel
    results = [{
        'content': content,
        'severity': severity,
        'category': 'Bias detected',  # Customize categories as needed
        'explanation': analysis
    }]
    
    create_excel_report(results)

# Function to process PDF file input
def process_pdf_file(input_file):
    with pdfplumber.open(input_file) as pdf:
        content = ""
        for page in pdf.pages:
            content += page.extract_text()  # Extract text from each page
    
    # Call the content moderation function
    analysis = analyze_content(content)
    severity = set_severity_flagged(content)
    
    # Create results and save to Excel
    results = [{
        'content': content,
        'severity': severity,
        'category': 'Bias detected',  # Customize categories as needed
        'explanation': analysis
    }]
    
    create_excel_report(results)

# Function to process CSV file input
def process_csv_input(input_file):
    df = pd.read_csv(input_file)
    results = []

    for index, row in df.iterrows():
        content = row['text']  # Ensure the column name is correct
        analysis = analyze_content(content)
        severity = set_severity_flagged(content)
        
        results.append({
            'content': content,
            'severity': severity,
            'category': 'Bias detected',
            'explanation': analysis
        })

    create_excel_report(results)

# Function to handle pasted text
def process_pasted_text(pasted_text):
    # Call the content moderation function for the pasted text
    analysis = analyze_content(pasted_text)
    severity = set_severity_flagged(pasted_text)
    
    # Create results and save to Excel
    results = [{
        'content': pasted_text,
        'severity': severity,
        'category': 'Bias detected',  # Customize categories as needed
        'explanation': analysis
    }]
    
    create_excel_report(results)

# Function to process any input (text, PDF, CSV, or pasted text)
def process_input(input_data):
    if isinstance(input_data, str):
        # If input_data is a string, assume it's pasted text
        process_pasted_text(input_data)
    else:
        # Otherwise, process it as a file
        file_extension = os.path.splitext(input_data)[1].lower()  # Get the file extension
        
        if file_extension == '.txt':
            process_text_file(input_data)  # Process text file
        elif file_extension == '.pdf':
            process_pdf_file(input_data)  # Process PDF file
        elif file_extension == '.csv':
            process_csv_input(input_data)  # Process CSV file
        else:
            print("Unsupported file type. Please provide a .txt, .pdf, or .csv file.")

# Function to interactively get input from the user
def get_input():
    input_type = input("Do you want to paste text or provide a file? (Type 'paste' or 'file'): ").strip().lower()
    
    if input_type == 'paste':
        pasted_text = input("Paste your text here: ")
        process_input(pasted_text)
    elif input_type == 'file':
        file_path = input("Enter the file path: ").strip()
        process_input(file_path)
    else:
        print("Invalid input. Please type 'paste' or 'file'.")


