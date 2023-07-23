"""
This script contains the code to both check the current accessibility of a PDF according to the WCAG standard
using VeraPDF, as well as the the conversion to Markdown using `pdf2html` and our xml converter.
"""

import io
import os
import PIL
import PyPDF2
import subprocess
import pytesseract
from glob import glob
from bs4 import BeautifulSoup
from mdutils.mdutils import MdUtils
from pdf2image import convert_from_path

PIL.Image.MAX_IMAGE_PIXELS = None


def find_paragraph_fontsize(font_sizes, row_font_size, num_char):
	size_count = {x: 0 for x in font_sizes}
	for i in range(len(num_char)):
		size_count[row_font_size[i]] += num_char[i]

	return int(max(size_count, key=size_count.get))


# Convenience function for conversion to PNG for Tesseract operations
def convert_pdf_to_png(input_pdf_path: str):
	# Checking if it is a pdf file
	if not input_pdf_path.lower().endswith('.pdf'):
		raise FileNotFoundError

	# Load the image
	images = convert_from_path(input_pdf_path)
	return images


class PDFConverter:
	"""
	Class to convert in input PDF file to a more accessible markdown version uses pdf2html
	and our own conversion algorithm.
	"""
	def __init__(self):
		pass

	def upgrade_pdf_OCR(self, input_pdf_file: str, output_pdf_file: str):
		"""
		This function takes as input a PDF, OCRs it with Tesseract
		and writes the output back to a pdf file.
		"""

		input_png_images = convert_pdf_to_png(input_pdf_file)
		raw_output_pages = [pytesseract.image_to_pdf_or_hocr(input_png, extension='pdf') for input_png in
							input_png_images]

		# overwrite the original pdf file with the new one

		merger = PyPDF2.PdfMerger()
		for raw_page in raw_output_pages:
			merger.append(io.BytesIO(raw_page))
		merger.write(output_pdf_file)

	def convert_PDF_to_XML(self, input_pdf_path: str, output_xml_path: str):

		# Call pdftohtml on the upgraded PDF
		subprocess.call(['pdftohtml', '-q', '-c', '-xml',
						 '-hidden', input_pdf_path])

		# we don't need the png files that are created, so we will remove them using glob
		input_filename = os.path.splitext(os.path.split(input_pdf_path)[-1])[0]
		output_png_files = glob(os.path.join("/".join(input_pdf_path.split('/')[:-1]), '%s-?_?.??g' % input_filename))
		for file in output_png_files:
			os.remove(file)

		# pdftohtml doesn't really support giving an output filename, so rename
		# the one that is created instead.
		pdf_to_html_file = os.path.splitext(input_pdf_path)[0] + '.xml'
		os.rename(pdf_to_html_file, output_xml_path)

		return None

	def convert_XML_to_markdown(self, input_xml_file: str, output_markdown_file: str):

		markdown_out = MdUtils(file_name=os.path.splitext(output_markdown_file)[0])

		# Parse XML document
		with open(input_xml_file) as f:
			soup = BeautifulSoup(f, features='xml')

		# Get all the fonts
		fonts = soup.find_all("fontspec")
		font_ids = []
		font_sizes = []
		num_char = []
		row_font_size = []

		# Loop through fonts and get id and size
		for font in fonts:
			font_ids.append(font["id"])
			font_sizes.append(font["size"])

		# Calc num of characters per row
		texts = soup.find_all("text")
		for text in texts:
			try:
				num_char.append(len(text.string))
				row_font_size.append(font_sizes[int(text['font'])])
			except:
				pass

		# Find paragraph font
		p_size = find_paragraph_fontsize(font_sizes, row_font_size, num_char)

		# Get fontsizes
		ogFonts = soup.find_all("fontspec")
		ogFont_sizes = []
		for ogFont in ogFonts:
			ogFont_sizes.append(ogFont["size"])

		# Set variables
		p_string = str()
		datum = str()
		start_indent = True
		diff_marge = 7

		# Get all pages
		pages = soup.find_all("page")

		# Loop through pages
		for page in pages:

			# Get all text rows
			texts = page.find_all("text")
			page_width = int(page['width'])

			# Loop through each row
			for i in range(len(texts)):

				# Get current row information
				top = int(texts[i]["top"])
				left = int(texts[i]["left"])
				width = int(texts[i]["width"])
				height = int(texts[i]['height'])
				string = str(texts[i].contents[0])

				# Skip left aligned text
				if left > (0.50 * page_width):
					continue

				# If last row
				if i + 1 == len(texts):
					p_string = p_string + string
					markdown_out.new_paragraph(p_string)
					continue

				# Get prev row information
				prev_top = int(texts[i - 1]["top"])
				prev_height = int(texts[i - 1]['height'])

				# Get next row information
				next_top = int(texts[i + 1]["top"])

				# If on same row
				if prev_top == top:
					p_string += string

				# Check if 'betreft', 'datum' or 'geachte'
				if string[:6] == 'Datum ':
					datum = string
					continue

				if string[:8] == 'Betreft ':
					markdown_out.new_header(level=1, title=string, add_table_of_contents='n')
					if datum:
						markdown_out.new_header(level=6, title=datum, add_table_of_contents='n')
					continue

				if string[:8] == 'Geachte ':
					markdown_out.new_paragraph(string)
					continue

				# Check space between top position previous row
				if (top - (prev_top + prev_height)) >= diff_marge:  # space between current and previous row (new paragraph)
					if width < 450:
						markdown_out.new_header(level=2, title=string, add_table_of_contents='n')

					elif (next_top - (
							top + height)) < diff_marge:  # no space between current and next row (paragraph continues)
						p_string += string

					else:  # space between current and next row (paragraph ends)
						p_string += string
						markdown_out.new_paragraph(p_string)  # insert p block
						p_string = str()
						continue

				if (top - (
						prev_top + prev_height)) < diff_marge:  # no space between current and previous row (paragraph continues)
					if (next_top - (
							top + height)) < diff_marge:  # no space between current and next row (paragraph continues)
						p_string += string

					else:  # space between current and next row (paragraph ends)
						p_string += string
						markdown_out.new_paragraph(p_string)  # insert p block
						p_string = str()
						continue

		# Create markdown output of the file
		markdown_out.create_md_file()