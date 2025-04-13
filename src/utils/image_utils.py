from PIL import Image
import os

def get_image_dimensions(image_path):
    """
    Return image dimensions (width, height) in pixels.
    """
    with Image.open(image_path) as img:
        return img.size  # (width, height)


def is_supported_image(file_path):
    """
    Check if the image file is of a supported format.
    """
    supported_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
    ext = os.path.splitext(file_path)[1].lower()
    return ext in supported_extensions


def format_size_readable(bytes_size):
    """
    Convert bytes to a human-readable string (e.g., KB, MB).
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"
