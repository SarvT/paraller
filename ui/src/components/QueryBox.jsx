import React, { useState } from "react";

const QueryBox = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState(null);
  const [sql, setSql] = useState("");
  const [loading, setLoading] = useState(false);

  const sendQuery = async () => {
    setLoading(true);
    setResponse(null);
    try {
      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data.result || data.error);
      setSql(data.sql);
    } catch (err) {
      setResponse("Failed to connect to server.");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white shadow-lg rounded-lg space-y-6">
      <h3 className="text-2xl font-semibold text-gray-700">Ask a Question</h3>
      <input
        className="w-full p-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. Show top 5 stores with highest availability"
      />
      <button
        className="w-full bg-blue-600 text-white py-3 rounded-lg mt-4 hover:bg-blue-700 focus:outline-none"
        onClick={sendQuery}
        disabled={loading}
      >
        {loading ? "Loading..." : "Ask"}
      </button>

      {sql && (
        <div className="mt-6 bg-gray-100 p-4 rounded-lg">
          <strong className="text-gray-800">SQL Generated:</strong>
          <pre className="mt-2 text-sm text-gray-700">{sql}</pre>
        </div>
      )}

      {response && (
        <div className="mt-6 bg-white p-4 border-2 border-gray-300 rounded-lg">
          <strong className="text-gray-800">Response:</strong>
          <pre className="mt-2 text-sm text-gray-700">{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default QueryBox;
