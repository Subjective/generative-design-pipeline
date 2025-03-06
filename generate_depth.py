import torch
from PIL import Image
import argparse
import numpy as np
from zoedepth.utils.misc import colorize

# Load ZoeDepth model using Torch Hub
repo = "isl-org/ZoeDepth"
model_zoe_n = torch.hub.load(repo, "ZoeD_N", pretrained=True)

# Set the device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model_zoe_n = model_zoe_n.to(DEVICE)

def get_grayscale_depth(image_path, output_path):
    """
    Get the grayscale depth of an image, invert it, and save it to a file.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the inverted grayscale depth image.
    """
    # Load the image
    image = Image.open(image_path).convert("RGB")
    
    # Infer depth using ZoeDepth model
    depth_tensor = model_zoe_n.infer_pil(image, output_type="tensor")
    
    # Colorize the depth map in grayscale
    grayscale_depth = colorize(depth_tensor, cmap="gray")
    
    # Invert the grayscale depth
    inverted_depth = 255 - grayscale_depth  # Invert grayscale values

    # Save the inverted grayscale depth image
    Image.fromarray(inverted_depth[:, :, :3]).save(output_path)
    print(f"Inverted grayscale depth image saved at {output_path}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate inverted grayscale depth map from an image.")
    parser.add_argument("input_path", type=str, help="Path to the input image.")
    parser.add_argument("output_path", type=str, help="Path to save the inverted grayscale depth image.")
    args = parser.parse_args()

    # Run the function with provided arguments
    get_grayscale_depth(args.input_path, args.output_path)
