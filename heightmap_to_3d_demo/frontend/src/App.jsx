import React, { useState, useEffect } from "react";
import axios from "axios";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader";
import { PLYLoader } from "three/examples/jsm/loaders/PLYLoader";

function ModelViewer({ fileUrl, fileType }) {
  const [geometry, setGeometry] = useState(null);

  useEffect(() => {
    if (!fileUrl) return;
    setGeometry(null); // reset previous geometry

    if (fileType === "stl") {
      const loader = new STLLoader();
      loader.load(fileUrl, (geom) => {
        setGeometry(geom);
      });
    } else if (fileType === "ply") {
      const loader = new PLYLoader();
      loader.load(fileUrl, (geom) => {
        geom.computeVertexNormals();
        setGeometry(geom);
      });
    }
  }, [fileUrl, fileType]);

  if (!geometry) {
    return (
      <div className="flex items-center justify-center h-full text-lg font-medium">
        Loading model...
      </div>
    );
  }

  return (
    <Canvas className="w-full h-full" camera={{ position: [150, 150, 150], fov: 75 }}>
      <ambientLight intensity={0.5} />
      <directionalLight intensity={0.5} position={[0, 0, 100]} />
      <mesh geometry={geometry}>
        {fileType === "ply" ? (
          <meshStandardMaterial vertexColors={!!geometry.attributes.color} />
        ) : (
          <meshStandardMaterial color="lightgray" />
        )}
      </mesh>
      <OrbitControls />
    </Canvas>
  );
}

function App() {
  // The only file needed is a png image
  const [image, setImage] = useState(null);

  // Model parameters
  const [blockWidth, setBlockWidth] = useState(100);
  const [blockLength, setBlockLength] = useState(100);
  const [blockThickness, setBlockThickness] = useState(10);
  const [depth, setDepth] = useState(5);
  const [baseHeight, setBaseHeight] = useState(0);
  const [mode, setMode] = useState("protrude");
  const [invert, setInvert] = useState(false);

  // Resulting file
  const [resultUrl, setResultUrl] = useState("");
  const [resultFileType, setResultFileType] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResultUrl("");

    if (!image) {
      console.error("No image selected");
      setLoading(false);
      return;
    }

    // Build the form data
    const formData = new FormData();
    // We'll call this "color_image" on the backend
    formData.append("color_image", image);

    formData.append("block_width", blockWidth);
    formData.append("block_length", blockLength);
    formData.append("block_thickness", blockThickness);
    formData.append("depth", depth);
    formData.append("base_height", baseHeight);
    formData.append("mode", mode);
    formData.append("invert", invert ? "true" : "false");

    try {
      // Post to your /api/generate endpoint
      const response = await axios.post("http://127.0.0.1:5000/api/generate", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResultUrl(response.data.fileUrl);
      setResultFileType(response.data.fileType);
    } catch (error) {
      console.error("Error generating model:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Page Header */}
      <header className="text-center mb-8">
        <h1 className="text-4xl font-bold">Image to 3D</h1>
      </header>

      {/* Main Content */}
      <main className="space-y-8">
        {/* Form Container */}
        <div className="bg-gray-100 dark:bg-gray-800 p-6 rounded-lg shadow">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Single file input for PNG */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                Image (png)
              </label>
              <input
                type="file"
                accept="image/png"
                required
                onChange={(e) => setImage(e.target.files[0])}
                className="mt-1 block w-full text-sm text-gray-900 bg-white dark:bg-gray-700 
                           border border-gray-300 dark:border-gray-600 rounded-md cursor-pointer"
              />
            </div>

            {/* Two-column grid for numeric inputs */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Block Width (mm)
                </label>
                <input
                  type="number"
                  value={blockWidth}
                  onChange={(e) => setBlockWidth(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Block Length (mm)
                </label>
                <input
                  type="number"
                  value={blockLength}
                  onChange={(e) => setBlockLength(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Block Thickness (mm)
                </label>
                <input
                  type="number"
                  value={blockThickness}
                  onChange={(e) => setBlockThickness(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Depth (mm)
                </label>
                <input
                  type="number"
                  value={depth}
                  onChange={(e) => setDepth(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Base Height (mm)
                </label>
                <input
                  type="number"
                  value={baseHeight}
                  onChange={(e) => setBaseHeight(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                  Mode
                </label>
                <select
                  value={mode}
                  onChange={(e) => setMode(e.target.value)}
                  className="mt-1 block w-full p-2 border border-gray-300 rounded-md 
                             focus:outline-none dark:bg-gray-700 dark:border-gray-600"
                >
                  <option value="protrude">Protrude</option>
                  <option value="carve">Carve</option>
                </select>
              </div>
            </div>

            {/* Invert heightmap checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="invert"
                checked={invert}
                onChange={(e) => setInvert(e.target.checked)}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <label
                htmlFor="invert"
                className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                Invert Heightmap
              </label>
            </div>

            {/* Generate button */}
            <div>
              <button
                type="submit"
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-md 
                           transition disabled:opacity-50"
                disabled={loading}
              >
                {loading ? "Generating..." : "Generate Model"}
              </button>
            </div>
          </form>

          {/* Loading spinner */}
          {loading && (
            <div className="flex items-center justify-center mt-4">
              <svg
                className="animate-spin h-6 w-6 text-blue-600"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                ></path>
              </svg>
              <span className="ml-2 text-lg">Generating model...</span>
            </div>
          )}
        </div>

        {/* If we have a result, show it */}
        {resultUrl && (
          <div className="bg-white dark:bg-gray-700 p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-200">
              Generated Model
            </h2>
            <p className="mb-4">
              <a
                href={resultUrl}
                download
                className="text-blue-600 hover:underline font-medium"
              >
                Download Model
              </a>
            </p>
            <div className="mt-4 h-96 border border-gray-300 rounded overflow-hidden">
              <ModelViewer fileUrl={resultUrl} fileType={resultFileType} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center mt-8 text-gray-600 dark:text-gray-400 text-sm">
        © 2025 Joshua Yin
      </footer>
    </div>
  );
}

export default App;

