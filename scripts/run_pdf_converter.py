import os
import argparse
from pdfconverter import PDFConverter



def main(arguments):
    # Set up the converter
    file_converter = PDFConverter()
    # First, upgrade the quality of the OCR of the file with Tesseract
    file_converter.upgrade_pdf_OCR(arguments.input_pdf_file, arguments.input_pdf_file)

    # Save the xml to a file with the same name as the input pdf file
    xml_filename = os.path.splitext(arguments.input_pdf_file)[0] + '.xml'
    file_converter.convert_PDF_to_XML(arguments.input_pdf_file, output_xml_path=xml_filename)

    # Save the md to a file with the same name as the input pdf file
    md_filename = os.path.splitext(arguments.input_pdf_file)[0] + '.md'
    file_converter.convert_XML_to_markdown(xml_filename, md_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_pdf_file', type=str, required=True)
    args = parser.parse_args()
    main(args)

