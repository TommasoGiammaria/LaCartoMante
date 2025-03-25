from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from PIL import Image

"""
This module contains the functions to write texts and images on a PDF file.
"""


def _text_to_pdf(text: str, pdf: PdfPages):
    """
    Change the text format based on its length and put it in a pdf page
    """

    formatted_text = ""
    for line in text.split("\n"):
        for index in range(0, len(line), 95):
            formatted_text += "\n"
            endindex = index + 96
            newline = ""
            if endindex < len(line) - 1:
                newline = line[index:endindex]
            else:
                newline = line[index:]
            formatted_text += newline
    newtextfig = Figure()
    newtextfig.text(0.05, 0.05, formatted_text, size=8)
    pdf.savefig(newtextfig)


def _image_text_to_pdf(
    card_image: Image,
    card_title: str,
    card_text: str,
    pdf: PdfPages
):
    """
    Put the card on the left of the page and its title + description on the right
    the description is also formatted to fit the space
    """

    description_card_lines = card_text.split("\n")
    new_image = card_image.resize(
        (240, 475), Image.LANCZOS
    )  # resizes the image to fit the pdf page
    newfig = Figure()
    newfig.figimage(new_image)
    stringsize = 8
    pdf_txt_width = 60
    pdf_page_max_lines = 30
    formatted_correctly = False
    while not formatted_correctly:
        formatted_description = ""
        for line in description_card_lines:
            for index in range(0, len(line), pdf_txt_width):
                formatted_description += "\n"
                endindex = index + pdf_txt_width
                newline = ""
                if endindex < len(line) - 1:
                    newline = line[index:endindex]
                else:
                    newline = line[index:]
                formatted_description += newline
        if len(formatted_description.split("\n")) > pdf_page_max_lines:
            stringsize -= 1
            pdf_txt_width += 10
            pdf_page_max_lines += 8
        else:
            formatted_correctly = True
    newfig.text(
        0.4,
        0.05,
        formatted_description,
        size=stringsize,
    )  # add formatted description
    newfig.text(0.4, 0.9, card_title, size=12)  # add card_title
    pdf.savefig(newfig)  # save to pdf
