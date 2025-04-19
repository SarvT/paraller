import React from "react";
import QueryBox from "./QueryBox"; // Adjust path if needed

const InsightsViewer = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h2 className="text-3xl font-semibold text-center text-gray-800">Explore Your Insights</h2>
      <QueryBox />
    </div>
  );
};

export default InsightsViewer;
