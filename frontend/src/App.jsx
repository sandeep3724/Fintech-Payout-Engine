import { useEffect, useState } from "react";
import API from "./api";
import "./index.css";

const MERCHANT_ID = 1;
const BANK_ACCOUNT_ID = 1;

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const formatMoney = (paise) => {
    return `₹${(paise / 100).toLocaleString("en-IN")}`;
  };

  const loadDashboard = async () => {
    const res = await API.get(`/merchants/${MERCHANT_ID}/dashboard/`);
    setDashboard(res.data);
  };

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(loadDashboard, 3000);
    return () => clearInterval(interval);
  }, []);

  const requestPayout = async (e) => {
    e.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const amountPaise = Number(amount) * 100;

      const res = await API.post(
        "/payouts/",
        {
          merchant_id: MERCHANT_ID,
          bank_account_id: BANK_ACCOUNT_ID,
          amount_paise: amountPaise,
        },
        {
          headers: {
            "Idempotency-Key": crypto.randomUUID(),
          },
        }
      );

      setMessage(`Payout created successfully. Status: ${res.data.status}`);
      setAmount("");
      loadDashboard();
    } catch (error) {
      setMessage(error.response?.data?.error || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (!dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <p className="text-sm text-slate-400">Playto Payout Engine</p>
          <h1 className="text-3xl font-bold">{dashboard.merchant.name}</h1>
          <p className="text-slate-400">{dashboard.merchant.email}</p>
        </div>

        <div className="grid md:grid-cols-2 gap-5 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <p className="text-slate-400 text-sm">Available Balance</p>
            <h2 className="text-4xl font-bold mt-2">
              {formatMoney(dashboard.available_balance_paise)}
            </h2>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <p className="text-slate-400 text-sm">Held Balance</p>
            <h2 className="text-4xl font-bold mt-2">
              {formatMoney(dashboard.held_balance_paise)}
            </h2>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-4">Request Payout</h2>

            <form onSubmit={requestPayout} className="space-y-4">
              <div>
                <label className="text-sm text-slate-400">Amount in ₹</label>
                <input
                  type="number"
                  min="1"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full mt-2 px-4 py-3 rounded-xl bg-slate-950 border border-slate-700 outline-none"
                  placeholder="Enter amount"
                  required
                />
              </div>

              <button
                disabled={loading}
                className="w-full bg-white text-slate-950 py-3 rounded-xl font-semibold disabled:opacity-50"
              >
                {loading ? "Processing..." : "Request Payout"}
              </button>
            </form>

            {message && (
              <p className="mt-4 text-sm text-slate-300 bg-slate-950 p-3 rounded-xl">
                {message}
              </p>
            )}
          </div>

          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-xl font-semibold mb-4">Payout History</h2>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-slate-400">
                  <tr>
                    <th className="text-left py-3">ID</th>
                    <th className="text-left py-3">Amount</th>
                    <th className="text-left py-3">Status</th>
                    <th className="text-left py-3">Attempts</th>
                  </tr>
                </thead>

                <tbody>
                  {dashboard.payouts.map((payout) => (
                    <tr key={payout.id} className="border-t border-slate-800">
                      <td className="py-3">#{payout.id}</td>
                      <td className="py-3">{formatMoney(payout.amount_paise)}</td>
                      <td className="py-3">
                        <span className="px-3 py-1 rounded-full bg-slate-800">
                          {payout.status}
                        </span>
                      </td>
                      <td className="py-3">{payout.attempts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="mt-6 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Ledger Entries</h2>

          <div className="space-y-3">
            {dashboard.ledger_entries.map((entry) => (
              <div
                key={entry.id}
                className="flex items-center justify-between bg-slate-950 rounded-xl p-4"
              >
                <div>
                  <p className="font-medium">{entry.description}</p>
                  <p className="text-sm text-slate-400">{entry.entry_type}</p>
                </div>

                <p className="font-semibold">
                  {entry.entry_type === "credit" ? "+" : "-"}
                  {formatMoney(entry.amount_paise)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}