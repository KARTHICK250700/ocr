import os
import re
import json

TXT_FOLDER = "output_txt"
JSON_FOLDER = "output_json"
os.makedirs(JSON_FOLDER, exist_ok=True)

def clean_line(text):
    # Clean unwanted characters, keep meaningful ones
    text = text.replace('\n', ' ').strip()
    text = re.sub(r'[^0-9a-zA-Z.% ,\-:/]+', '', text)
    return text

def find_key_value(lines, keys):
    # Find value for any of the given keys in lines (case-insensitive)
    for line in lines:
        for key in keys:
            if key.lower() in line.lower():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
                else:
                    # If ':' missing, try after key itself
                    after_key = line.lower().split(key.lower(),1)[1].strip()
                    if after_key:
                        return after_key
    return ""

def extract_gstin(text):
    # GSTIN is 15 char alphanumeric (numbers and uppercase letters)
    match = re.search(r'\b[0-9A-Z]{15}\b', text)
    if match:
        return match.group()
    return ""

def parse_items(lines, start_index):
    items = []
    for line in lines[start_index:]:
        if line.strip() == '' or 'total' in line.lower():
            break
        parts = line.split()
        # At least 6 columns needed (adjust based on invoice)
        if len(parts) < 6:
            continue
        # Create item dict with safety
        item = {
            "HSN": parts[0] if len(parts)>0 else "",
            "Code": parts[1] if len(parts)>1 else "",
            "Quantity": parts[2] if len(parts)>2 else "",
            "Unit Price": parts[3] if len(parts)>3 else "",
            "CGST Amount": parts[4] if len(parts)>4 else "",
            "SGST %": parts[5] if len(parts)>5 else "",
            "SGST Amount": parts[6] if len(parts)>6 else "",
            "IGST %": parts[7] if len(parts)>7 else "",
            "IGST Amount": parts[8] if len(parts)>8 else "",
            "Amount": parts[9] if len(parts)>9 else "",
        }
        items.append(item)
    return items

def parse_invoice_text(text):
    lines = [clean_line(l) for l in text.split('\n') if l.strip()]

    invoice = {
        "Invoice Type": find_key_value(lines, ["Invoice Type", "Invoice"]),
        "Branch": find_key_value(lines, ["Branch", "Location"]),
        "Billing Name": find_key_value(lines, ["Billing Name", "Bill To"]),
        "Billing Address": find_key_value(lines, ["Billing Address", "Bill Address"]),
        "Shipping Name": find_key_value(lines, ["Shipping Name", "Ship To"]),
        "Shipping Address": find_key_value(lines, ["Shipping Address", "Ship Address"]),
        "GSTIN": extract_gstin(text),
        "Items": [],
        "Total Tax Amount": find_key_value(lines, ["Total Tax Amount", "Tax Amount"]),
        "Grand Total": find_key_value(lines, ["Grand Total", "Total Amount", "Amount Payable"])
    }

    # Find items table header line index
    header_index = None
    for i, line in enumerate(lines):
        # Common headers in invoice item tables (adjust as needed)
        if all(k in line.lower() for k in ['hsn', 'code', 'quantity']):
            header_index = i
            break

    if header_index is not None:
        invoice["Items"] = parse_items(lines, header_index + 1)

    return invoice

def txt_to_json_pipeline():
    for txt_file in os.listdir(TXT_FOLDER):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(TXT_FOLDER, txt_file)
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()

            invoice_json = parse_invoice_text(text)

            json_filename = txt_file.replace('.txt', '.json')
            json_path = os.path.join(JSON_FOLDER, json_filename)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(invoice_json, f, ensure_ascii=False, indent=4)
            print(f"Saved {json_path}")

if __name__ == "__main__":
    txt_to_json_pipeline()
