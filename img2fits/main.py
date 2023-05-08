import argparse
import os

import numpy as np
from PIL import Image

from astropy.io import fits

from pillow_heif import register_heif_opener


# TODO: Really test all these...
IMAGE_FILE_EXTENSIONS = [
    ".jpg",
    ".heic",
    ".heif",
    ".png",
    ".jpeg",
    # More common image file extensions
    ".bmp",
    ".gif",
]


def main(args: argparse.Namespace):
    """Main program body"""
    register_heif_opener()

    # Convert path to absolute path from relative/user path if necessary
    expanded_path = os.path.expanduser(args.target)
    target_path = os.path.abspath(expanded_path)

    # Check if target is file or directory
    if os.path.isfile(target_path):
        # Convert single file
        # Rather than using output, save to subdir adjacent to file
        convert_img_to_fits(target_path)
    elif os.path.isdir(target_path):
        # Convert all files in directory
        for file in os.listdir(target_path):
            # Check if file is an image
            if file.endswith((".jpg", ".heic", ".heif", ".png", ".jpeg")):
                # Convert image to FITS
                convert_img_to_fits(os.path.join(target_path, file))
    else:
        raise ValueError("Target must be a file or directory")


def convert_img_to_fits(img_file: str):
    """Converts an image file to FITS format"""
    # Preserve image name, minus the extension
    img_relative_filename = os.path.basename(img_file)
    img_base_name = os.path.splitext(img_relative_filename)[0]

    # If output dir is none, save to directory next to img with same base name as file
    img_dir = os.path.dirname(img_file)
    output_dir = os.path.join(img_dir, img_base_name)

    # Open image file
    img = Image.open(img_file)

    # Convert to grayscale
    grayscale_image = img.convert("L")

    # Get RGB channel data
    red, green, blue = img.split()

    # Get pixel data for each channel and grayscale
    grayscale_data = np.array(grayscale_image.getdata())
    red_data = np.array(red.getdata())
    green_data = np.array(green.getdata())
    blue_data = np.array(blue.getdata())

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # For each data, convert to FITS file and save to target output directory,
    # use a zip() to iterate over the data and the channel names for file/subdirectory names
    for data, channel in zip(
        [grayscale_data, red_data, green_data, blue_data],
        ["GRAYSCALE", "RED", "GREEN", "BLUE"],
    ):
        # Convert to numpy array
        data_array = np.array(data)
        # Create FITS file
        fits_file = fits.PrimaryHDU(data_array)
        # Save FITS file
        fits_file.writeto(os.path.join(output_dir, f"{img_base_name}.{channel}.fits"))


def get_args() -> argparse.Namespace:
    """Gets runtime arguments"""
    parser = argparse.ArgumentParser(description="Image to FITS converter")
    # Add argument that takes a file or directory as input
    parser.add_argument("target", help="File or directory to convert", required=True)
    # Parse arguments
    args = parser.parse_args()
    return args


def run_script():
    """Runs the script"""
    run_args = get_args()
    main(run_args)


if __name__ == "__main__":
    run_script()
