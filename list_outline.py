import docx

doc = docx.Document('AgroNex_Pi_IEEE_Formatted.docx')
for i, p in enumerate(doc.paragraphs):
    if p.text.strip():
        if p.style and ('Heading' in p.style.name or 'Title' in p.style.name):
            print(f"P{i:03d} [{p.style.name}]: {p.text}")
        elif p.text.strip().startswith('TABLE') or p.text.strip().startswith('Fig.'):
            print(f"P{i:03d} [Caption]: {p.text[:70]}")
