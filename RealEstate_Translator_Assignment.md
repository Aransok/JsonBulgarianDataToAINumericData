
# 📝 Python Project Assignment: Real Estate Listings Translator & Formatter

## 🎯 Objective
Create a Python project that processes property listings in JSON format. The program should:

1. Translate all Bulgarian text into English.
2. Convert all numeric values into their **Bulgarian word equivalents using English letters** (e.g., `182756` ➝ `sto osemdeset i dve hilyadi sedemstotin pedeset i shest`).
3. Generate a **well-structured PDF report** with a clean and readable layout.

---

## 📂 Input Format

You will receive a JSON object structured like this:

```json
{
  "София": {
    "квартал": "Драгалевци", "тип": "Къща",
    "площ": "240 квадратни метра",
    "цена": "824545 лева",
    "цена на квадратен метър": "3435 лева",
    
    "квартал": "Лагера", "тип": "Къща",
    "площ": "220 квадратни метра",
    "цена": "896954 лева",
    "цена на квадратен метър": "4077 лева"
    
    // ... and so on
  }
}
```

---

## ✅ Requirements

### 1. Translation Module
Translate all keys and values from Bulgarian to English using a library like `googletrans` or `deep-translator`. For example:
- "София" ➝ "Sofia"
- "квартал" ➝ "District"
- "площ" ➝ "Area"
- "цена" ➝ "Price"

### 2. Number-to-Words (Bulgarian in English Letters)
Convert any numeric value into **Bulgarian number words written using English letters**:
- Example: `824545` ➝ `osemsto dvadeset i chetiri hilyadi petstotin chetirideset i pet`

This applies to:
- Area
- Price
- Price per sq.m

**Note:** You must extract the numeric part from strings like `"824545 лева"` before converting.

---

## 🖨️ PDF Report Styling Requirements

Generate a PDF file for the output using a library such as `fpdf`, `reportlab`, or `pdfkit`.

Each city (e.g., Sofia) should have its own section with a bold heading.

Each property listing should include:
- District (bold)
- Type (italic)
- Area: `<value>` sq.m (`<value in Bulgarian words>`)
- Price: `<value>` BGN (`<value in Bulgarian words>`)
- Price per sq.m: `<value>` BGN (`<value in Bulgarian words>`)

### Layout example:

```
City: Sofia

1. District: Dragalevtsi
   • Type: House
   • Area: 240 sq.m (dvesta i chetirideset kvadratni metra)
   • Price: 824,545 BGN (osemsto dvadeset i chetiri hilyadi petstotin chetirideset i pet leva)
   • Price per sq.m: 3,435 BGN (tri hilyadi chetiristotin trideset i pet leva)
```

Ensure:
- Clean alignment and padding
- Use bullet points for property attributes
- Use readable fonts and maintain consistent formatting

---

## 🔧 Suggested Libraries

```bash
pip install googletrans==4.0.0-rc1
pip install fpdf
```

---

## 📤 Submission

Submit a `.zip` file or GitHub repo that includes:
- `main.py`
- Input JSON file
- Output PDF file
- `README.md` with setup instructions and dependencies

---

Happy Coding!
