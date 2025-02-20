# import module
from pdf2image import convert_from_path
import os

# Store Pdf with convert_from_path function
images = convert_from_path('slides\\1-software-udvikling.pdf')

# Create directory if it doesn't exist
output_dir = 'output/screenshots'
if not os.path.exists(output_dir):
  os.makedirs(output_dir)

for i in range(len(images)):
      # Save pages as images in the pdf
    images[i].save(output_dir + '/page_'+ str(i) +'.jpg', 'JPEG')