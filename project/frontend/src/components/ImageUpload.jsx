import React, { useRef, useState } from 'react';

const ImageUpload = ({ onImageLoaded, onImageFile }) => {
  const fileInputRef = useRef(null);
  const [fileName, setFileName] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      onImageFile(file);

      // Show preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreviewUrl(event.target.result);
        onImageLoaded(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">📁 Upload Road Image</h2>
      
      <div
        className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="text-6xl mb-4">📸</div>
        <p className="text-gray-600 mb-2">
          Click to upload or drag and drop
        </p>
        <p className="text-gray-400 text-sm">
          PNG, JPG, JPEG (Max 10MB)
        </p>
        
        {fileName && (
          <div className="mt-4 text-green-600 font-semibold">
            ✓ {fileName}
          </div>
        )}
      </div>

      {previewUrl && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3 text-gray-700">Preview</h3>
          <img
            src={previewUrl}
            alt="Preview"
            className="max-h-64 mx-auto rounded-lg shadow"
          />
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
