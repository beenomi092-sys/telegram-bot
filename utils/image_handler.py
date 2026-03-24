import os
from datetime import datetime

def save_image(image_file, user_id, images_folder):
    try:
        if not os.path.exists(images_folder):
            os.makedirs(images_folder)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_{user_id}_{timestamp}.jpg"
        filepath = os.path.join(images_folder, filename)
        
        image_file.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving image: {e}")
        return None
