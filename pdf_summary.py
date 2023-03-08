import os
import openai
import pdfplumber
from time import time,sleep
import textwrap
import re
import glob2


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def convert_pdf2txt(src_dir, dest_dir):
    files = os.listdir(src_dir)
    files = [i for i in files if '.pdf' in i]
    for file in files:
        try:
            with pdfplumber.open(src_dir+file) as pdf:
                output = ''
                for page in pdf.pages:
                    output += page.extract_text()
                    output += '\n\nNEW PAGE\n\n'  # change this for your page demarcation
                save_file(dest_dir+file.replace('.pdf','.txt'), output.strip())
        except Exception as oops:
            print(oops, file)
            
openai.api_key = open_file('settings/openaiapikey.txt')

chatbot = open_file('settings/chatbot.txt')

#THIS FUNCTION USES ChatGPT API TO SUMMARIZE (CHEAPER)
def chatgpt3 (userinput, temperature=0.7, frequency_penalty=0, presence_penalty=0):
    messagein = [
        {"role": "user", "content": userinput },
        {"role": "system", "content": chatbot}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        messages=messagein
    )
    text = response['choices'][0]['message']['content']
    return text

if __name__ == '__main__':
    #Call PDF Converter Function
    convert_pdf2txt('PDFs/', 'textPDF/')
    
    #Your Pathfolder
    pathfolder = 'textPDF'
    
    # get a list of all text files in the specified folder
    files = glob2.glob(f'{pathfolder}/*.txt')
    
    # initialize an empty string to store the contents of all the text files
    alltext = ""
    

    # iterate over the list of files
    for file in files:
        with open(file, 'r') as infile:  # open the file
            alltext += infile.read()  # read the contents of the file and append it to the alltext string
    chunks = textwrap.wrap(alltext, 4000)
    result = list()
    count = 0
    
    #write a summary
    for chunk in chunks:
        count = count + 1
        prompt = open_file('settings/prompt.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
        summary = chatgpt3(prompt)
        print('\n\n\n', count, 'out of', len(chunks), 'Compressions', ' : ', summary)
        result.append(summary)
        save_file("output/pdfsummary.txt", '\n\n'.join(result))

# Split the contents of pfdsummary.txt into chunks with a textwrap of 3000
    with open("output/pdfsummary.txt", 'r', encoding='utf-8') as infile:
        summary = infile.read()
        chunks = textwrap.wrap(summary, 3000)

    #Initialize empty lists to store the results
    result = []
    result2 = []

    #WRITE NOTES FROM CHUNKS
    for i, chunk in enumerate(chunks):
        # Read the contents of prompt2.txt
        with open("settings/prompt2.txt", 'r', encoding='utf-8') as infile:
            prompt = infile.read()

        # Replace the placeholder in the prompt with the current chunk
        prompt = prompt.replace("<<NOTES>>", chunk)

        # Run the chunk through the gpt_3 function
        notes = chatgpt3(prompt)
        
        #WRITE A SUMMARY FROM NOTES
        keytw = open_file('settings/prompt6.txt').replace('<<NOTES>>', chunk)
        keytw2 = chatgpt3(keytw)


        # Print the result
        print(f"\n\n\n{i+1} out of {len(chunks)} Compressions: {notes}")

        # Append the results to the lists
        result.append(notes)
        result2.append(keytw2)


    #Save the results to a file
    with open("output/notes.txt", 'w', encoding='utf-8') as outfile:
        outfile.write("\n\n".join(result))
        
    with open("output/notessum.txt", 'w', encoding='utf-8') as outfile:
        outfile.write("\n\n".join(result2))
    #SUMMARY OF NOTES
    sumnotes = open_file("output/notessum.txt")
    
    
    #WRITE A STEP BY STEP GUIDE FROM NOTES
    #keytw = open_file('prompt3.txt').replace('<<NOTES>>', sumnotes)
    #keytw2 = chatgpt3(keytw)
    #print(keytw2)
    #save_file("steps.txt", keytw2)  

        
    #WRITE ESSENCIAL INFO
    essencial1 = open_file('settings/prompt4.txt').replace('<<NOTES>>', sumnotes)
    essencial2 = chatgpt3(essencial1)
    print(essencial2)
    save_file("output/essencial.txt", essencial2)    
    
    #WRITE A BLOG POST
    #blogpost = open_file('essencial.txt')
    #blogpostw = open_file('prompt5.txt').replace('<<NOTES>>', blogpost)
    #blogpostw2 = chatgpt3(blogpostw)
    #print(blogpostw2)
    #save_file("blogpost.txt", blogpostw2)
    
  
    #WRITE A VISUAL PROMPT
    #midj = open_file("essencial.txt")
    #mjv4 = open_file('mjv4prompts.txt').replace('<<SCENE>>', midj)
    #desc = chatgpt3(mjv4)
    #print('\n\n', desc)
    #save_file("midprompts.txt", desc)