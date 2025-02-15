import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/Authcontext";
import { toast } from "react-toastify";

export const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          toast.error("Invalid email or password. Please try again.", { position: "top-right" });
        } else {
          toast.error(`Something went wrong. Please try again later. (${response.statusText})`, { position: "top-right" });
        }
      } else{
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        
        await login(data.access)
  
        navigate("/");
      }
    } catch (error) {
      toast.error(`Network error. Please try again. Error: ${error}`, { position: "top-right" });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <form
        onSubmit={handleLogin}
        className="bg-indigo-400 p-6 rounded shadow-md w-80"
      >
        <h2 className="text-2xl font-bold mb-5 text-gray-800">Log In</h2>
        <div className="mb-4">
          <label className="block mb-1 text-gray-800">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 text-gray-800">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            required
          />
        </div>
        <button type="submit" className="w-full">
          Log In
        </button>
      </form>
    </div>
  );
};

