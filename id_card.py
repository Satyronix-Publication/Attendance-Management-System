# id_card.py
# Attendance Management System - CBSE Class 12 Project
# Virtual ID Card Generator

import os
from PIL import Image, ImageDraw, ImageFont
import qrcode

def generate_virtual_id(student_info):
    """
    Generates a virtual ID card image.
    student_info is a dict with keys:
    name, roll, class, section, dob, phone, email, address, parent_contact
    """
    # Create base image
    width, height = 400, 600
    
    # Class-based color
    bg_color = "#1e1040"
    accent_color = "#8b5cf6" if str(student_info.get("class")) == "12" else "#3b82f6"
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_heading = ImageFont.truetype("arialbd.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font_title = ImageFont.load_default()
        font_heading = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Header
    draw.rectangle([0, 0, width, 80], fill=accent_color)
    school_name = "ABC SENIOR SECONDARY SCHOOL"
    draw.text((width/2, 40), school_name, font=font_title, fill="white", anchor="mm")
    
    # Photo placeholder
    photo_size = 120
    px, py = (width - photo_size) // 2, 100
    draw.rectangle([px, py, px+photo_size, py+photo_size], outline="white", width=2)
    draw.text((width/2, py + photo_size/2), "PHOTO", font=font_text, fill="white", anchor="mm")

    # Details
    y = 240
    name = str(student_info.get("name", "Unknown"))
    draw.text((width/2, y), name.upper(), font=font_heading, fill="white", anchor="mm")
    
    y += 40
    details = [
        f"Roll No : {student_info.get('roll', 'N/A')}",
        f"Class   : {student_info.get('class', '')} - {student_info.get('section', '')}",
        f"D.O.B   : {student_info.get('dob', 'N/A')}",
        f"Phone   : {student_info.get('phone', 'N/A')}",
        f"Parent  : {student_info.get('parent_contact', 'N/A')}"
    ]
    
    for line in details:
        draw.text((40, y), line, font=font_text, fill="#e2e8f0")
        y += 30

    # QR Code
    qr_data = f"ID:{student_info.get('roll')}|Name:{name}"
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    
    # Paste QR Code
    img.paste(qr_img, (290, 480))

    # Footer
    draw.text((150, 520), "Virtual ID Card", font=font_small, fill=accent_color)
    draw.text((150, 540), "Valid for 2026-2027", font=font_small, fill="#a8a8b3")

    return img
