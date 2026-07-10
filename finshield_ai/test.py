import fitz

doc = fitz.open("data/insurance/LIC_Jeevan-Labh_Brochure_9-inch-x-8-inch_Eng.pdf")

for i, page in enumerate(doc):

    pix = page.get_pixmap(dpi=100)

    print(f"Page {i+1}: {pix.width} x {pix.height}")