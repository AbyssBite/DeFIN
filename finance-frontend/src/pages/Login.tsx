import { useState } from "react";
import axiosClient from "../api/axiosClient";
import { useNavigate } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(""); // reset previous errors

        try {
            // FastAPI Users expects application/x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append("grant_type", "password"); // required
            formData.append("username", email);        // your email/login
            formData.append("password", password);

            const response = await axiosClient.post("/auth/jwt/login", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            // store JWT token
            const token = response.data.access_token;
            localStorage.setItem("token", token);

            // navigate to transactions page
            navigate("/transactions");
        } catch (err: any) {
            // handle validation and other errors
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
                setError("Login failed");
            }
        }
    };

    return (
        <div style={{ maxWidth: 400, margin: "2rem auto" }}>
            <h2>Login</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "1rem" }}>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>
                <div style={{ marginBottom: "1rem" }}>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: "100%", padding: "0.5rem" }}
                    />
                </div>
                {error && <p style={{ color: "red", whiteSpace: "pre-wrap" }}>{error}</p>}
                <button type="submit" style={{ padding: "0.5rem 1rem" }}>
                    Login
                </button>
            </form>
        </div>
    );
}
