import json
import re
from deep_translator import GoogleTranslator
from fpdf import FPDF

def load_data(file_path):
    """Load and parse JSON data from file, with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        raise
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' contains invalid JSON.")
        raise
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def extract_numeric_part(text):
    """Extract numeric values from text strings."""
    if not text or not isinstance(text, str):
        return None, text
    
    # Use regex to extract numbers
    numeric_match = re.search(r'(\d+)', text)
    if not numeric_match:
        return None, text
    
    numeric_part = numeric_match.group(1)
    # Remove the numeric part from the original text
    remaining_text = text.replace(numeric_part, '', 1).strip()
    
    return numeric_part, remaining_text

def translate_text(text):
    """Translate text from Bulgarian to English with error handling."""
    if not text or not isinstance(text, str):
        return text
        
    try:
        translator = GoogleTranslator(source='bg', target='en')
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

def process_property_item(property_item):
    """Process a single property item regardless of structure."""
    if isinstance(property_item, dict):
        result = {}
        for key, value in property_item.items():
            translated_key = translate_text(key)
            
            # Process numeric values
            if isinstance(value, str):
                numeric_part, text_part = extract_numeric_part(value)
                
                if numeric_part:
                    try:
                        numeric_word = number_to_bulgarian_words(int(numeric_part))
                        translated_text = translate_text(text_part)
                        
                        # Fix for "lev/leva"
                        if translated_text and "lev" in translated_text.lower():
                            translated_text = "leva"
                            
                        translated_value = f"{numeric_word} {translated_text}"
                    except:
                        # Fallback if number conversion fails
                        translated_value = translate_text(value)
                else:
                    translated_value = translate_text(value)
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                translated_value = process_property_item(value)
            elif isinstance(value, list):
                # Recursively process lists
                translated_value = [process_property_item(item) for item in value]
            else:
                # Handle other types
                translated_value = str(value)
                
            result[translated_key] = translated_value
        return result
    elif isinstance(property_item, list):
        return [process_property_item(item) for item in property_item]
    elif isinstance(property_item, str):
        return translate_text(property_item)
    else:
        return property_item

def translate_data(data):
    """Process and translate property data with flexible structure support."""
    if not data:
        return {}
        
    # For simple dictionary structure
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            translated_key = translate_text(key)
            
            # Process the value based on its type
            if isinstance(value, dict):
                result[translated_key] = process_property_item(value)
            elif isinstance(value, list):
                result[translated_key] = [process_property_item(item) for item in value]
            else:
                result[translated_key] = translate_text(str(value))
                
        return result
    # For list structure
    elif isinstance(data, list):
        return [process_property_item(item) for item in data]
    else:
        return {}

# Updated Bulgarian digits and words based on reference
_bgd = {
    0: "nula", 1: "edno", 2: "dve", 3: "tri", 4: "chetiri",
    5: "pet", 6: "shest", 7: "sedem", 8: "osem", 9: "devet",
    10: "deset", 11: "edinadeset", 12: "dvanadeset", 13: "trinadeset",
    14: "chetirinadeset", 15: "petnadeset", 16: "shestnadeset",
    17: "sedemnadeset", 18: "osemnadeset", 19: "devetnadeset",
    20: "dvadeset", 30: "trideset", 40: "chetirideset", 50: "petdeset",
    60: "shestdeset", 70: "sedemdeset", 80: "osemdeset", 90: "devetdeset"
}

# Hundreds in Bulgarian (based on reference)
_hundreds = {
    1: "sto", 2: "dvesta", 3: "trista", 4: "chetiristotin", 
    5: "petstotin", 6: "sheststotin", 7: "sedemstotin", 8: "osemstotin", 9: "devetstotin"
}

def number_to_bulgarian_words(number):
    """Convert a number to its Bulgarian word representation using English letters."""
    if not isinstance(number, int):
        try:
            number = int(number)
        except:
            return str(number)  # Return the original if conversion fails
            
    if number == 0:
        return _bgd[0]
    
    words = []
    
    # Billions
    if number >= 1000000000:
        billions = number // 1000000000
        if billions == 1:
            words.append("edin miliard")
        elif billions > 1:
            billion_words = number_to_bulgarian_words(billions)
            words.append(f"{billion_words} miliarda")
        number %= 1000000000
    
    # Millions
    if number >= 1000000:
        millions = number // 1000000
        if millions == 1:
            words.append("edin milion")
        elif millions > 1:
            million_words = number_to_bulgarian_words(millions)
            words.append(f"{million_words} miliona")
        number %= 1000000
    
    # Thousands
    if number >= 1000:
        thousands = number // 1000
        if thousands == 1:
            words.append("hilyada")
        elif thousands > 1:
            thousand_words = number_to_bulgarian_words(thousands)
            words.append(f"{thousand_words} hilyadi")
        number %= 1000
    
    # Hundreds
    if number >= 100:
        hundreds_digit = number // 100
        if hundreds_digit in _hundreds:
            words.append(_hundreds[hundreds_digit])
        number %= 100
    
    # Tens and units
    if number > 0:
        if number < 20 and number in _bgd:
            words.append(_bgd[number])
        else:
            tens = (number // 10) * 10
            units = number % 10
            if tens in _bgd:
                if units == 0:
                    words.append(_bgd[tens])
                elif units in _bgd:
                    words.append(f"{_bgd[tens]} i {_bgd[units]}")
    
    return " ".join(words)

def extract_properties(data_structure, processed_properties=None):
    """Extract property data from potentially nested structures and convert to a flat list."""
    if processed_properties is None:
        processed_properties = []
    
    if isinstance(data_structure, dict):
        property_like = False
        district = None
        
        # Check if this dict looks like a property listing
        for key in data_structure.keys():
            translated_key = translate_text(key.lower()) if isinstance(key, str) else ""
            if translated_key in ["district", "type", "area", "price"]:
                property_like = True
            if translated_key == "district":
                district = data_structure[key]
        
        if property_like:
            # This is a property, add it to our list
            processed_properties.append(data_structure)
        else:
            # This might be a container, process its contents
            for value in data_structure.values():
                extract_properties(value, processed_properties)
    
    elif isinstance(data_structure, list):
        for item in data_structure:
            extract_properties(item, processed_properties)
    
    return processed_properties

def generate_pdf(data, output_file="property_listings_en.pdf"):
    """Generate a PDF report from the translated property data."""
    pdf = FPDF()
    pdf.add_page()
    
    if not data:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "No data available", ln=True)
        pdf.output(output_file)
        return
    
    # Extract city-property structure if it exists
    cities = {}
    
    # Check if the data is in the expected city-properties format
    city_properties_format = False
    
    for key, value in data.items() if isinstance(data, dict) else []:
        if isinstance(value, list) or isinstance(value, dict):
            city_properties_format = True
            cities[key] = value
    
    # If not in the expected format, try to extract properties and group by city
    if not city_properties_format:
        # Extract all properties from the data structure
        all_properties = extract_properties(data)
        
        # Group by city if possible
        for prop in all_properties:
            city = None
            for key, value in prop.items():
                if translate_text(key.lower()) == "city":
                    city = value
                    break
            
            if not city:
                city = "Unknown"
                
            if city not in cities:
                cities[city] = []
            
            cities[city].append(prop)
    
    # If still no cities found, treat the whole data as one property list
    if not cities:
        cities = {"Properties": data if isinstance(data, list) else [data]}
    
    # Process each city
    for city, properties in cities.items():
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"City: {city}", ln=True)
        pdf.ln(5)
        
        # Process properties
        property_list = []
        
        # Convert to a standard list format
        if isinstance(properties, dict):
            # Try to extract properties from dict
            extracted = extract_properties(properties)
            if extracted:
                property_list = extracted
            else:
                # If no properties extracted, treat each key-value as a property detail
                property_list = [properties]
        elif isinstance(properties, list):
            property_list = properties
        else:
            # Handle unexpected types
            property_list = [{"Value": str(properties)}]
        
        # Generate PDF content for each property
        for idx, property_item in enumerate(property_list, 1):
            # Get district if available
            district = None
            for key, value in property_item.items() if isinstance(property_item, dict) else []:
                if translate_text(key.lower()) == "district":
                    district = value
                    break
            
            if not district:
                district = f"Property {idx}"
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{idx}. District: {district}", ln=True)
            
            if isinstance(property_item, dict):
                for key, value in property_item.items():
                    # Skip district in details as it's already in the header
                    if translate_text(key.lower()) != "district":
                        pdf.cell(10)  # Indent
                        pdf.set_font("ZapfDingbats", '', 12)
                        pdf.cell(5, 10, "l")  # Bullet point
                        pdf.set_font("Arial", '', 12)
                        pdf.cell(0, 10, f"{key}: {value}", ln=True)
            else:
                # Handle non-dict properties
                pdf.cell(10)  # Indent
                pdf.set_font("ZapfDingbats", '', 12)
                pdf.cell(5, 10, "l")  # Bullet point
                pdf.set_font("Arial", '', 12)
                pdf.cell(0, 10, f"Value: {property_item}", ln=True)
            
            pdf.ln(5)
    
    pdf.output(output_file)
    print(f"PDF generated successfully: {output_file}")

# Main execution
def main(input_file='input.json', output_file='property_listings_en.pdf'):
    """Main program execution with error handling."""
    try:
        print("Loading data...")
        data = load_data(input_file)
        
        print("Translating data...")
        translated_data = translate_data(data)
        
        print("Generating PDF...")
        generate_pdf(translated_data, output_file)
        
        print(f"Process completed successfully! Output saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error during execution: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'property_listings_en.pdf'
        main(input_file, output_file)
    else:
        main()
