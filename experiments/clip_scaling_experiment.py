import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import torch
import clip  # OpenAI's CLIP library

def get_likely_labels(image_array: np.ndarray, labels: list[str]) -> list[tuple[str, float]]:
    """
    Identifies the most likely labels for an image using CLIP, sorted by similarity score.

    Parameters:
        image_array (np.ndarray): The input image as a NumPy array (RGB format).
        labels (list[str]): A list of label strings to match against the image.

    Returns:
        list[tuple[str, float]]: A sorted list of tuples containing labels and their similarity scores.
    """
    # Load CLIP model and preprocessing
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Convert the NumPy array to a PIL Image
    image = Image.fromarray(image_array)

    # Preprocess the image for CLIP
    image = preprocess(image).unsqueeze(0).to(device)

    # Tokenize the labels
    text = clip.tokenize(labels).to(device)

    # Encode the image and labels using CLIP
    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

    # Normalize features for cosine similarity
    image_features /= image_features.norm(dim=-1, keepdim=True)
    text_features /= text_features.norm(dim=-1, keepdim=True)

    # Compute similarity scores
    similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

    # Pair each label with its score and sort by descending score
    sorted_labels = sorted(zip(labels, similarity[0].cpu().numpy()), key=lambda x: x[1], reverse=True)

    return sorted_labels

def run_scaling_experiment(image_array: np.ndarray, labels: list[str], min_dim: int, step: int):
    """
    Runs an experiment to test CLIP's labeling accuracy on resized versions of an image.

    Parameters:
        image_array (np.ndarray): The original image as a NumPy array.
        labels (list[str]): A list of label strings for CLIP.
        min_dim (int): The smallest dimension (width or height) to resize the image to.
        step (int): The step size for reducing the image dimensions.

    Returns:
        dict: A dictionary mapping image dimensions to the top label and its score.
    """
    original_height, original_width = image_array.shape[:2]
    results = {}

    for dim in range(min(original_height, original_width), min_dim - 1, -step):
        # Resize image while maintaining aspect ratio
        scaling_factor = dim / max(original_height, original_width)
        new_size = (int(original_width * scaling_factor), int(original_height * scaling_factor))
        resized_image = np.array(Image.fromarray(image_array).resize(new_size, Image.BILINEAR))

        # Get likely labels
        likely_labels = get_likely_labels(resized_image, labels)

        # Store results: top label and its score
        results[dim] = likely_labels[0]  # (label, score)

    return results

if __name__ == "__main__":
    # Load your image as a NumPy array
    image_array = np.array(Image.open("./sheep.png").convert("RGB"))

    # Define labels
    labels = ["cow", "sheep", "landscape"]

    # Run experiment
    results = run_scaling_experiment(image_array, labels, min_dim=32, step=16)

    # Plot results
    dimensions = sorted(results.keys(), reverse=True)
    scores = [results[dim][1] for dim in dimensions]
    top_labels = [results[dim][0] for dim in dimensions]

    plt.figure(figsize=(10, 6))
    plt.plot(dimensions, scores, marker="o")
    plt.title("CLIP Label Accuracy vs Image Dimension")
    plt.xlabel("Image Dimension (min width/height)")
    plt.ylabel("Top Label Score")
    plt.grid()
    for i, label in enumerate(top_labels):
        plt.text(dimensions[i], scores[i], label, fontsize=9, ha="right")
    plt.show()
