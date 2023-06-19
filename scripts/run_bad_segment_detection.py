"""
This script contains the code to process an input pdf and perform the bad segment detection on
it, and also save the output in a dataframe so that it can be used later. This script will first
convert the pdf files into images, after which tesseract is run on the text and the bad segment detection
is performed on this text. The output can also be configured to be run on the original text extracted
using pdftotext.
"""

from pdf2image import convert_from_path

import argparse
import pdftotext
import pytesseract
import pandas as pd

from badsegmentdetector import *


def convert_pdf_to_png(input_pdf_path: str):

    # Checking if it is a pdf file
    if not input_pdf_path.lower().endswith('.pdf'):
        raise FileNotFoundError

    # Load the image
    images = convert_from_path(input_pdf_path)
    return images


def main(arguments):
    text_of_pages = []
    if arguments.do_tesseract:
        input_images = convert_pdf_to_png(arguments.input_pdf)
        for image in input_images:
            text_of_pages.append(pytesseract.image_to_string(image))
    else:
        # extract the text with pdftotext
        with open(arguments.input_pdf, "rb") as pdf_file:
            pdf = pdftotext.PDF(pdf_file, physical=True)
        text_of_pages = [page for page in pdf]

    # Now perform the bad segment detection for all pages with the stats
    input_text_ser = pd.Series(text_of_pages)
    bad_segment_stats, bad_segment_lengths = run_bad_segment_detection(input_text_ser, tolerance=arguments.tolerance)

    # now save to a dataframe
    bad_segment_stats.to_csv('../examples/output.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_pdf', type=str, required=True)
    # Specify the output path where a dataframe with the output of the
    # bad segment data detection will be written to.
    parser.add_argument('--output_path', type=str, required=True)
    parser.add_argument('--do_tesseract', type=bool, default=False)
    parser.add_argument('--tolerance', type=int, default=3)

    args = parser.parse_args()

    main(args)

