# convert_to_yolo.py

import os
import xml.etree.ElementTree as ET

def convert_voc_to_yolo(xml_files, txt_folder, classes):
    os.makedirs(txt_folder, exist_ok=True)
    conversion_log = []

    for xml_file in xml_files:
        # Parse XML content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Image dimensions
        size = root.find("size")
        image_width = int(size.find("width").text)
        image_height = int(size.find("height").text)

        # Prepare the txt file name based on XML file
        txt_filename = os.path.join(txt_folder, os.path.basename(xml_file).replace(".xml", ".txt"))
        with open(txt_filename, "w") as txt_file:
            for obj in root.findall("object"):
                class_name = obj.find("name").text
                if class_name in classes:
                    class_id = classes.index(class_name)

                    # Get bounding box coordinates
                    bndbox = obj.find("bndbox")
                    xmin = float(bndbox.find("xmin").text)
                    ymin = float(bndbox.find("ymin").text)
                    xmax = float(bndbox.find("xmax").text)
                    ymax = float(bndbox.find("ymax").text)

                    # Convert to YOLO format
                    center_x = (xmin + xmax) / 2 / image_width
                    center_y = (ymin + ymax) / 2 / image_height
                    width = (xmax - xmin) / image_width
                    height = (ymax - ymin) / image_height

                    # Write the line to txt file
                    txt_file.write(f"{class_id} {center_x} {center_y} {width} {height}\n")
        conversion_log.append(f"Converted: {os.path.basename(xml_file)} to {os.path.basename(txt_filename)}")

    return conversion_log
