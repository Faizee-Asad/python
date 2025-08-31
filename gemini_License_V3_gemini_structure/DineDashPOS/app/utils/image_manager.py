import os
from PIL import Image, ImageTk

class ImageManager:
    """Handles saving, loading, and managing product images."""

    @staticmethod
    def get_images_dir():
        """Returns the dedicated directory for storing product images."""
        home_dir = os.path.expanduser("~")
        images_dir = os.path.join(home_dir, "DineDashPOS", "images")
        os.makedirs(images_dir, exist_ok=True)
        return images_dir
    
    @staticmethod
    def save_product_image(product_id, source_path):
        """Saves, resizes, and converts a product image to JPEG."""
        if not os.path.exists(source_path):
            return None
        
        images_dir = ImageManager.get_images_dir()
        file_ext = os.path.splitext(source_path)[1].lower()
        if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return None
        
        filename = f"product_{product_id}.jpg" # Standardize to .jpg
        destination = os.path.join(images_dir, filename)
        
        try:
            with Image.open(source_path) as img:
                img = img.convert('RGB')
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(destination, 'JPEG', quality=85)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    @staticmethod
    def get_product_image(image_filename, size=(150, 150)):
        """Loads a product image or returns a placeholder if not found."""
        image_path = os.path.join(ImageManager.get_images_dir(), image_filename) if image_filename else ""
        
        try:
            if os.path.exists(image_path):
                with Image.open(image_path) as img:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {image_filename}: {e}")
            
        # Return a placeholder image if the original is not found or fails to load
        placeholder = Image.new('RGB', size, color='#21262d')
        return ImageTk.PhotoImage(placeholder)
