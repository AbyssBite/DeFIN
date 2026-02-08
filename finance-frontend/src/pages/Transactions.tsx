import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import type { Transaction, TransactionType } from "../types";
import { useNavigate } from "react-router-dom";

export default function Transactions() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [description, setDescription] = useState("");
    const [amount, setAmount] = useState<number | "">("");
    const [trxType, setTrxType] = useState<TransactionType>("inflow");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    // Fetch transactions on load
    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                const response = await axiosClient.get<Transaction[]>("/transactions", {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
                });
                setTransactions(response.data);
            } catch (err: any) {
                if (err.response?.status === 401) {
                    navigate("/login");
                } else {
                    setError("Failed to fetch transactions");
                }
            }
        };

        fetchTransactions();
    }, [navigate]);

    // Add a transaction
    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        try {
            const payload: any = {
                amount: Number(amount),
                trx_type: trxType,
            };

            // Only include description if not empty
            if (description.trim()) {
                payload.description = description.trim();
            }

            const response = await axiosClient.post<Transaction>("/transactions", payload, {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            });

            setTransactions([response.data, ...transactions]);
            setDescription("");
            setAmount("");
            setTrxType("inflow");
        } catch (err: any) {
            const detail = err.response?.data?.detail;
            if (detail) {
                if (Array.isArray(detail)) {
                    setError(detail.map((d: any) => d.msg).join(", "));
                } else if (typeof detail === "string") {
                    setError(detail);
                } else {
                    setError(JSON.stringify(detail));
                }
            } else {
                setError("Failed to add transaction");
            }
        }
    };

    // Delete a transaction
    const handleDelete = async (id: string) => {
        setError("");
        try {
            await axiosClient.delete(`/transactions/${id}`, {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
            });
            setTransactions(transactions.filter((t) => t.id !== id));
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to delete transaction");
        }
    };

    return (
        <div style={{ maxWidth: 600, margin: "2rem auto" }}>
            <h2>Your Transactions</h2>

            {error && <p style={{ color: "red", whiteSpace: "pre-wrap" }}>{error}</p>}

            <form onSubmit={handleAdd} style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
                <input
                    type="text"
                    placeholder="Description (optional)"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
                <input
                    type="number"
                    placeholder="Amount"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value === "" ? "" : parseFloat(e.target.value))}
                    required
                />
                <select
                    value={trxType}
                    onChange={(e) => setTrxType(e.target.value as TransactionType)}
                >
                    <option value="inflow">Inflow</option>
                    <option value="outflow">Outflow</option>
                </select>
                <button type="submit">Add</button>
            </form>

            <ul>
                {transactions.map((trx) => (
                    <li key={trx.id} style={{ marginBottom: "0.5rem" }}>
                        <strong>{trx.trx_type.toUpperCase()}</strong>: {trx.description || "(No description)"} — ${trx.amount.toFixed(2)}{" "}
                        <button onClick={() => handleDelete(trx.id)}>Delete</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
