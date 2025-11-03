function SummaryCard() {
  return (
    <div className="bg-white shadow-lg rounded-xl p-6 w-full max-w-2xl text-gray-800">
      <h2 className="text-2xl font-bold text-blue-700 mb-4">Patient Summary</h2>
      <div className="space-y-2">
        <p><strong>Name:</strong> John Doe</p>
        <p><strong>Age:</strong> 32</p>
        <p><strong>Gender:</strong> Male</p>
        <p><strong>Preliminary Diagnosis:</strong> Possible viral infection.</p>
        <p><strong>Recommendations:</strong> Hydration, rest, and follow-up in 3 days.</p>
      </div>

      <div className="mt-6 text-center">
        <button
          onClick={() => alert("Downloading report...")}
          className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700"
        >
          Download Report
        </button>
      </div>
    </div>
  );
}

export default SummaryCard;
