import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from heightmap_to_3d import generate_block_from_heightmap
from generate_depth import get_grayscale_depth  # ZoeDepth-based function

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/api/generate", methods=["POST"])
def api_generate():
    # 1) Check if "color_image" is in the request
    if "color_image" not in request.files:
        return jsonify({"error": "No color_image file provided"}), 400

    color_image_file = request.files["color_image"]
    if color_image_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # 2) Save the color image
    color_image_filename = str(uuid.uuid4()) + "_" + color_image_file.filename
    color_image_path = os.path.join(UPLOAD_FOLDER, color_image_filename)
    color_image_file.save(color_image_path)

    # 3) Generate a grayscale depth image (heightmap) from the color image
    heightmap_filename = "depth_" + color_image_filename
    heightmap_path = os.path.join(UPLOAD_FOLDER, heightmap_filename)
    try:
        get_grayscale_depth(color_image_path, heightmap_path)
    except Exception as e:
        return jsonify({"error": f"Error generating heightmap: {str(e)}"}), 500

    # 4) Retrieve numeric parameters from form data
    try:
        block_width = float(request.form.get("block_width", 100))
        block_length = float(request.form.get("block_length", 100))
        block_thickness = float(request.form.get("block_thickness", 10))
        depth = float(request.form.get("depth", 5))
        base_height = float(request.form.get("base_height", 0))
        mode = request.form.get("mode", "protrude")
        invert = request.form.get("invert", "false").lower() == "true"
    except ValueError:
        return jsonify({"error": "Invalid parameter values"}), 400

    # 5) We'll output a .ply file so color can be used
    file_type = "ply"
    output_filename = str(uuid.uuid4()) + ".ply"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # 6) Generate the 3D model using the new heightmap and the original color image as reference
    try:
        generate_block_from_heightmap(
            heightmap_path=heightmap_path,
            output_path=output_path,
            block_width=block_width,
            block_length=block_length,
            block_thickness=block_thickness,
            depth=depth,
            base_height=base_height,
            mode=mode,
            invert=invert,
            color_reference=color_image_path  # so the .ply includes color
        )
    except Exception as e:
        return jsonify({"error": f"Error generating model: {str(e)}"}), 500

    file_url = request.host_url + "outputs/" + output_filename
    return jsonify({"fileUrl": file_url, "fileType": file_type})

@app.route("/outputs/<filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)

