import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from heightmap_to_3d import generate_block_from_heightmap

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/api/generate", methods=["POST"])
def api_generate():
    if "heightmap" not in request.files:
        return jsonify({"error": "No heightmap file provided"}), 400
    heightmap_file = request.files["heightmap"]
    if heightmap_file.filename == "":
        return jsonify({"error": "No heightmap file selected"}), 400

    heightmap_filename = str(uuid.uuid4()) + "_" + heightmap_file.filename
    heightmap_path = os.path.join(UPLOAD_FOLDER, heightmap_filename)
    heightmap_file.save(heightmap_path)

    color_ref_path = None
    if "color_reference" in request.files:
        color_file = request.files["color_reference"]
        if color_file and color_file.filename != "":
            color_filename = str(uuid.uuid4()) + "_" + color_file.filename
            color_ref_path = os.path.join(UPLOAD_FOLDER, color_filename)
            color_file.save(color_ref_path)

    try:
        block_width = float(request.form.get("block_width", 100))
        block_length = float(request.form.get("block_length", 100))
        block_thickness = float(request.form.get("block_thickness", 10))
        depth = float(request.form.get("depth", 5))
        base_height = float(request.form.get("base_height", 0))
        mode = request.form.get("mode", "protrude")
        invert = request.form.get("invert", "false").lower() == "true"
    except Exception:
        return jsonify({"error": "Invalid parameter values"}), 400

    if color_ref_path:
        ext = ".ply"
        file_type = "ply"
    else:
        ext = ".stl"
        file_type = "stl"
    output_filename = str(uuid.uuid4()) + ext
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

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
            color_reference=color_ref_path
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

