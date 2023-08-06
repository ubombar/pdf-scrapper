# Written by Ufuk Bombar
from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")

# This is the color MAC creates annotations, and my chosen color for unknown words. Only they will be extracted
MAC_ANNOT_COLOR = "#7cc867"

def create_visitor_body(highlights: list, coords:list):
    # ys [490.3896, 490.3896, 479.2215, 479.2215]
    # Cords look like this: [380.8758, 490.3896, 419.6901, 490.3896, 380.8758, 479.2215, 419.6901, 479.2215]
    # Since they share an edge, the rect can be represented with less numbers
    xs, ys = coords[::2], coords[1::2]

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = max(ys), min(ys)

    def visitor_body(text, cm, tm, fontDict, fontSize):
        x, y = tm[4], tm[5]
        if y > ymin and y < ymax: # Calculate according to coords
            highlights.append(text)
            
    return visitor_body

def extract_color_hex(annot_obj) -> str:
    r, g, b = tuple(annot_obj["/C"])
    rgb = int(255*r), int(255*g), int(255*b)
    color_hex = ("#%x%x%x" % rgb).lower()

    return color_hex

highlights = []

for page in reader.pages:
    if "/Annots" in page:
        for annot in page["/Annots"]:
            if not "/Subtype" in annot.get_object(): continue
            subtype = annot.get_object()["/Subtype"]
            if subtype == "/Highlight":
                annot_obj = annot.get_object()
                coords = annot_obj["/QuadPoints"]
                if len(coords) != 8: continue # Special filter, only search for rectangles
                if extract_color_hex(annot_obj) != MAC_ANNOT_COLOR: continue # Filter for color

                # Create an visitor_body function for filtering the text that will be extracted from the pdf
                visitor_body = create_visitor_body(highlights, coords)
                t = page.extract_text(0, visitor_text=visitor_body)

                print("Added one new (green) highlight:", highlights)

                break
    # 
    # print(page.extract_text(0))

# print(parts)