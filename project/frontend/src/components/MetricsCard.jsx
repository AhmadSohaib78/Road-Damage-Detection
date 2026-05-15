import React from 'react';

const MetricsCard = ({ statistics, inferenceTime }) => {
  if (!statistics) return null;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'minor':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'moderate':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'severe':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Total Detections */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="text-3xl font-bold text-blue-600">
          {statistics.total_detections}
        </div>
        <p className="text-gray-600 text-sm mt-2">Total Detections</p>
      </div>

      {/* Potholes */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="text-3xl font-bold text-red-600">
          {statistics.pothole_count}
        </div>
        <p className="text-gray-600 text-sm mt-2">Potholes</p>
      </div>

      {/* Cracks */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <div className="text-3xl font-bold text-amber-600">
          {statistics.crack_count}
        </div>
        <p className="text-gray-600 text-sm mt-2">Cracks</p>
      </div>

      {/* Avg Confidence */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="text-3xl font-bold text-green-600">
          {(statistics.average_confidence * 100).toFixed(1)}%
        </div>
        <p className="text-gray-600 text-sm mt-2">Avg Confidence</p>
      </div>

      {/* Inference Time */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <div className="text-3xl font-bold text-purple-600">
          {inferenceTime?.toFixed(1)}ms
        </div>
        <p className="text-gray-600 text-sm mt-2">Inference Time</p>
      </div>

      {/* Severity Distribution */}
      <div className="lg:col-span-3 bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h4 className="font-semibold text-gray-700 mb-3">Severity Distribution</h4>
        <div className="grid grid-cols-3 gap-2">
          {['minor', 'moderate', 'severe'].map((sev) => (
            <div
              key={sev}
              className={`rounded p-3 text-center border ${getSeverityColor(sev)}`}
            >
              <div className="font-bold text-lg">
                {statistics.severity_distribution[sev]}
              </div>
              <div className="text-xs capitalize">{sev}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MetricsCard;
