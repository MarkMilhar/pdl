import re
import random
import requests
import os
import google.generativeai as genai
import logging

# Configure Google AI Studio API Key
# It is advisable to store your API key as an environment variable
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")  
if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable.")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Gemini Pro model
gemini_pro = genai.GenerativeModel('gemini-pro')

# Configure logging
logging.getLogger('google').setLevel(logging.ERROR)
logging.getLogger('grpc').setLevel(logging.ERROR)

def remove_multiline_comments(text):
    """Removes /* */ style comments."""
    return re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

def split_lines(text):
    """Splits text by both \n and \r\n."""
    return re.split(r'\r?\n', text)

def remove_eol_comments_and_trim(lines):
    """Removes // comments and trims each line, while ignoring URLs."""
    processed_lines = []
    for line in lines:
      # Split the line into parts, but keep the separator //
        parts = re.split(r'(?<!:)//', line)
        # if found //
        if len(parts) > 1:
             processed_lines.append(parts[0].strip())
        else: # // not found
            processed_lines.append(line.strip())
    return processed_lines

def combine_incomplete_directives(lines):
    """Combines lines with incomplete directives."""
    combined_lines = []
    in_directive = False
    current_directive = ""
    for line in lines:
        if line.startswith("#") and "{" in line:
             in_directive = True

        if in_directive: 
            current_directive += line + " "

            if "}" in current_directive:
                in_directive = False
                combined_lines.append(current_directive)
                current_directive = ""
                
        else:
            combined_lines.append(line)

    if current_directive:
        combined_lines.append(current_directive)

    return combined_lines

def group_paragraphs(lines):
    """Groups non-empty lines into single lines."""
    retval = []
    current_paragraph = []
    in_paragraph = False
    for line in lines:
        if line.startswith("#") or line == "": # directive
            if in_paragraph:
                retval.append(" ".join(current_paragraph))
                current_paragraph = []
                in_paragraph = False
            retval.append(line)
            continue
        current_paragraph.append(line)
        in_paragraph = True
    if current_paragraph:
         retval.append(" ".join(current_paragraph))
    return retval

def remove_empty_lines(lines):
    """Removes repeated empty lines."""
    return [line for i, line in enumerate(lines) if line or (i > 0 and lines[i-1])]


def process_include(file_path):
    """Handles #include directive."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {file_path}"


def process_open(url):
    """Handles #open directive."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        response.encoding = 'utf-8'  # Ensure response is decoded as UTF-8
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: Could not open URL: {url} - {e}"


def process_ask(prompt):
    """Handles #ask directive using Google AI Studio."""
    try:
        response = gemini_pro.generate_content(prompt)
        response.resolve()
        if response.text:
            return response.text
        else:
           return f"Error: No text response from AI for prompt: {prompt}"
    except Exception as e:
       return f"Error: AI service issue: {e}"
    
def process_random(choices_str):
    """Handles #random directive with space separated name and comma separated choices inside the curly braces."""
    choices = re.split(r',\s*', choices_str)
    if choices:
        return random.choice(choices)
    else:
        return "Error: No choices for #random"

def process_define(content):
    """Handles #define directive."""
    return content

def expand_macros(text, macros):
    """Expands macros recursively."""
    
    def replace_macro(match):
       macro_name = match.group(1)
       if macro_name in macros:
            return expand_macros(macros[macro_name], macros) # recursive expansion
       else:
         return match.group(0) # return as is if not found

    pattern = r'#(\w+)'
    while True:
        new_text = re.sub(pattern, replace_macro, text)
        if new_text == text:
            break
        text = new_text
    return text

def process_line(line, macros):
    """Processes a single line, handling directives or expanding macros."""
    if line.startswith('#'):
        match = re.match(r'#(\w+)\s*(?:(\w+)\s*)?{(.*)}', line)
        if match:
            keyword, name, content = match.groups()
            if keyword == 'include':
                 content = process_include(content)
            elif keyword == 'open':
                content = process_open(content)
            elif keyword == 'ask':
                content = process_ask(content)
            elif keyword == 'random':
                 content = process_random(content)
            elif keyword == 'define':
                content = process_define(content)

            if name:
                macros[name] = content.rstrip()
                return "" # return empty string as directive shall be removed, but name shall be saved
            else:
                return content.rstrip()
    else:
        return expand_macros(line, macros)
    return line # return original line if not handled


def preprocess(input_text):
    """Main preprocessing function."""
    
    output_text = input_text
    previous_output_text = ""
    macros = {}
    
    while output_text != previous_output_text:
        previous_output_text = output_text
        # 1. Remove /* */ comments
        output_text = remove_multiline_comments(output_text)
        # 2. Split by carriage returns or CRLF
        lines = split_lines(output_text)
        # 3. Remove EOL comments and trim
        lines = remove_eol_comments_and_trim(lines)
        # 4. Combine incomplete directives
        lines = combine_incomplete_directives(lines)
        # 5. Group non-empty lines as paragraphs
        lines = group_paragraphs(lines)
        # 6. Remove repeated empty lines
        lines = remove_empty_lines(lines)
        #7. process lines
        processed_lines = []
        for line in lines:
           processed_lines.append(process_line(line, macros))
        for line in processed_lines:
            line = line.strip()

        output_text = "\n".join(processed_lines)
        output_text = remove_empty_lines(output_text.splitlines())
        output_text = "\n".join(output_text)

    return output_text

if __name__ == "__main__":
    # Read raw prompt from file
    try:
        with open("rawprompt.txt", "r", encoding='utf-8') as f:
             raw_prompt = f.read()
    except FileNotFoundError:
        raw_prompt = "rawprompt.txt file not found. Please create one."

    current_text = raw_prompt
    preprocessed_text = preprocess(current_text)
    while preprocessed_text != current_text:
        current_text = preprocessed_text
        preprocessed_text = preprocess(current_text)

    print("Preprocessed text:\n", preprocessed_text)
