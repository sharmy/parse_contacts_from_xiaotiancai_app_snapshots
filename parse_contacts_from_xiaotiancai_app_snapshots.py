"""
批量从小天才APP联系人截图的图片中提取姓名、昵称和手机号
截图使用iphone 15pro，不同手机分辨率不同，需调整文本获取xy区域，例如roi_nickname = image[395:459, 290:800]
生成的csv文件可导入google contacts，再从google contacts导出vcard cvf文件，然后导入iphone/android等手机
"""

import easyocr
import cv2
import pandas as pd
import os
import sys
import traceback

# Initialize EasyOCR reader
# Set the language to 'ch_sim' for simplified Chinese and 'en' for English
reader = easyocr.Reader(['ch_sim', 'en'])

def extract_info_from_image(image_path):
    """
    Extracts name, nickname, and phone number from a single image using EasyOCR.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image at {image_path}")
            return None

        # Define the regions of interest (ROIs) for the text
        # These coordinates should be adjusted based on your specific image template.
        # [y_start, y_end, x_start, x_end]
        roi_nickname = image[395:459, 290:800]
        roi_name = image[470:510, 450:800]
        roi_phone = image[800:1000, 300:1150]
        

        # Use EasyOCR to recognize text in each ROI
        result_name = reader.readtext(roi_name, detail=0, paragraph=True)
        result_nickname = reader.readtext(roi_nickname, detail=0, paragraph=True)
        result_phone = reader.readtext(roi_phone, detail=0, paragraph=True)
        print(f" {image_path}: {result_name}, {result_nickname}, {result_phone}")

        # Extract the first recognized text from each list, if available
        name = result_name[0] if result_name else ''
        phone = result_phone[0] if result_phone else ''
        nickname = result_nickname[0] if result_nickname else ''

        return {
            'file_name': os.path.basename(image_path),
            'name': name,
            'nickname': nickname,
            'phone': phone
        }

    except Exception as e:
        print(Exception, e)
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        exit(1)

        print(f"An error occurred while processing {image_path}: {e}")
        return None

def process_images_in_folder(folder_path, output_csv):
    """
    Processes all images in a folder and saves the extracted data to a CSV file.
    """
    data_list = []
    # Supported image extensions
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    i = 0
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(image_extensions):
            i += 1
            image_path = os.path.join(folder_path, file_name)
            print(f"Processing {i}, {file_name}...")
            extracted_data = extract_info_from_image(image_path)
            if extracted_data:
                data_list.append(extracted_data)

    if not data_list:
        print("No image data extracted. The output CSV will be empty.")
        return

    # Create a DataFrame and save to CSV
    df = pd.DataFrame(data_list)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"\nSuccessfully extracted data and saved to {output_csv}")

# --- Configuration ---
# Set the path to the folder containing your images
# IMAGE_FOLDER = './images'
IMAGE_FOLDER = '/Users/bob/Downloads/contact251015'

# Set the desired name for the output CSV file
OUTPUT_CSV_FILE = 'contact_info.csv'

# --- Run the program ---
# Ensure the folder path is correct before running
process_images_in_folder(IMAGE_FOLDER, OUTPUT_CSV_FILE)