import React, { useEffect, useRef } from 'react';

const DetectionCanvas = ({ originalImage, detections }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!originalImage || !detections || detections.length === 0) {
      return;
    }

    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      canvas.width = img.width;
      canvas.height = img.height;

      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0);

      // Draw bounding boxes
      detections.forEach((det, idx) => {
        const [x1, y1, x2, y2] = det.bbox;
        const width = x2 - x1;
        const height = y2 - y1;

        // Color based on class
        const color = det.class === 'pothole' ? '#ef4444' : '#f59e0b';
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, width, height);

        // Label
        const label = `${det.class} ${(det.confidence * 100).toFixed(1)}%`;
        const fontSize = 16;
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.fillStyle = color;

        const textWidth = ctx.measureText(label).width;
        const textHeight = fontSize + 8;

        // Background for text
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(x1, y1 - textHeight - 4, textWidth + 8, textHeight + 4);

        // Text
        ctx.fillStyle = 'white';
        ctx.fillText(label, x1 + 4, y1 - 8);
      });
    };

    img.src = originalImage;
  }, [originalImage, detections]);

  if (!originalImage) {
    return (
      <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center text-gray-500">
        No image selected
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <h3 className="text-lg font-semibold mb-3 text-gray-700">🎯 Detection Results</h3>
      <canvas
        ref={canvasRef}
        className="max-w-full h-auto rounded border border-gray-200"
      />
    </div>
  );
};

export default DetectionCanvas;
