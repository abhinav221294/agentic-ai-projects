import fitz

def load_pdf(path):

    doc = fitz.open(path)

    text = ""

    for i, page in enumerate(doc):

        page_text = page.get_text()

        #print(f"Page {i+1}: {len(page_text)} characters")

        text += page_text

    return text