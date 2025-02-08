import { useState, useEffect } from 'react';

export default function AdminDashboard() {
  const [disputeData, setDisputeData] = useState(null);

  useEffect(() => {
    const fetchDisputeData = async () => {
      const data = {
        summary: "Dispute regarding product delivery timeline and condition",
        userA: {
          messages: ["Product arrived damaged", "Requesting full refund"],
          riskScore: "Low",
        },
        userB: {
          messages: ["Damage must have occurred during shipping", "Offering partial refund"],
          riskScore: "Low",
        },
        aiRecommendations: [
          "Review shipping insurance coverage",
          "Verify product condition photos",
          "Consider split liability resolution"
        ]
      };
      setDisputeData(data);
    };

    fetchDisputeData();
  }, []);

  if (!disputeData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-blue-50 to-cyan-50 flex items-center justify-center">
        <div className="text-xl gradient-text font-medium">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-blue-50 to-cyan-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-6xl font-semibold gradient-text mb-2 tracking-tight hover:tracking-wide transition-all duration-300">
            Mediator Dashboard
          </h1>
          <div className="h-1 w-40 bg-gradient-to-r from-violet-500 via-blue-500 to-cyan-500 mx-auto rounded-full"></div>
        </div>
        
        {/* AI Summary */}
        <div className="card-shine bg-gradient-to-br from-white/90 to-white/70 backdrop-blur-lg rounded-2xl shadow-lg p-8 border border-white/20 transition-all duration-300 hover:shadow-xl hover:shadow-blue-100/50 hover:translate-y-[-2px]">
          <h2 className="text-2xl font-semibold gradient-text mb-4">AI-Generated Summary</h2>
          <p className="text-slate-700 leading-relaxed font-light text-lg">{disputeData.summary}</p>
        </div>

        {/* User Panels */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* User A Panel */}
          <div className="card-shine bg-gradient-to-br from-white/90 to-white/70 backdrop-blur-lg rounded-2xl shadow-lg p-8 border border-white/20 transition-all duration-300 hover:shadow-xl hover:shadow-blue-100/50 hover:translate-y-[-2px]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold gradient-text">User A</h2>
              <span className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                disputeData.userA.riskScore === 'Low' 
                  ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 text-emerald-700 border border-emerald-200 hover:shadow-lg hover:shadow-emerald-100/50' 
                  : 'bg-gradient-to-r from-red-500/10 to-rose-500/10 text-rose-700 border border-rose-200 hover:shadow-lg hover:shadow-rose-100/50'
              }`}>
                Risk: {disputeData.userA.riskScore}
              </span>
            </div>
            <div className="space-y-4">
              {disputeData.userA.messages.map((msg, index) => (
                <div 
                  key={index} 
                  className="p-4 bg-gradient-to-r from-blue-50 to-violet-50 rounded-xl text-slate-700 border border-white/40 hover:shadow-md hover:translate-x-1 transition-all duration-300 font-light"
                >
                  {msg}
                </div>
              ))}
            </div>
          </div>

          {/* User B Panel */}
          <div className="card-shine bg-gradient-to-br from-white/90 to-white/70 backdrop-blur-lg rounded-2xl shadow-lg p-8 border border-white/20 transition-all duration-300 hover:shadow-xl hover:shadow-blue-100/50 hover:translate-y-[-2px]">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold gradient-text">User B</h2>
              <span className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
                disputeData.userB.riskScore === 'Low' 
                  ? 'bg-gradient-to-r from-emerald-500/10 to-green-500/10 text-emerald-700 border border-emerald-200 hover:shadow-lg hover:shadow-emerald-100/50' 
                  : 'bg-gradient-to-r from-red-500/10 to-rose-500/10 text-rose-700 border border-rose-200 hover:shadow-lg hover:shadow-rose-100/50'
              }`}>
                Risk: {disputeData.userB.riskScore}
              </span>
            </div>
            <div className="space-y-4">
              {disputeData.userB.messages.map((msg, index) => (
                <div 
                  key={index} 
                  className="p-4 bg-gradient-to-r from-blue-50 to-violet-50 rounded-xl text-slate-700 border border-white/40 hover:shadow-md hover:translate-x-1 transition-all duration-300 font-light"
                >
                  {msg}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* AI Recommendations */}
        <div className="card-shine bg-gradient-to-br from-white/90 to-white/70 backdrop-blur-lg rounded-2xl shadow-lg p-8 border border-white/20 transition-all duration-300 hover:shadow-xl hover:shadow-blue-100/50 hover:translate-y-[-2px]">
          <h2 className="text-2xl font-semibold gradient-text mb-6">AI-Recommended Next Steps</h2>
          <ul className="space-y-4">
            {disputeData.aiRecommendations.map((rec, index) => (
              <li 
                key={index} 
                className="flex items-center text-slate-700 hover:translate-x-2 transition-all duration-300 font-light text-lg group"
              >
                <div className="w-2 h-2 bg-gradient-to-r from-violet-500 to-blue-500 rounded-full mr-4 group-hover:scale-150 transition-transform duration-300"></div>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}