from multiprocessing import freeze_support
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import os

if __name__ == '__main__':
    freeze_support()

    converter = PdfConverter(
        artifact_dict=create_model_dict(),
    )
    rendered = converter("slides\\1-software-udvikling.pdf")
    text, _, image_map = text_from_rendered(rendered)

    output_folder = "output\\markdown\\"
    os.makedirs(output_folder, exist_ok=True)

    # Save text to a file
    text_file_path = os.path.join(output_folder, "output.md")
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

    # Save images to files
    for image_name, image in image_map.items():
        image_file_path = os.path.join(output_folder, image_name)
        image.save(image_file_path)