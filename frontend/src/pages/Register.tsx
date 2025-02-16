import React, { FC, useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

export const Register: FC = () => {
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    password2: "",
  });
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.password2) {
        toast.error("Passwords do not match.", { position: "top-right" });
        return;
    }

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/users/register/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        const data = await response.json();
  
        if (response.ok) {
          
          localStorage.setItem("access", data.access);
          localStorage.setItem("refresh", data.refresh);
  
          login(data.access);

          toast.success("Registration successful! Redirecting...", { position: "top-right" });
  
          setTimeout(() => navigate("/voice-config"), 2000);
      } else {
        if (data && typeof data === "object") {
            Object.keys(data).forEach((key) => {
              const errorMessage = Array.isArray(data[key]) ? data[key][0] : data[key];
              toast.error(`${key}: ${errorMessage}`, { position: "top-right" });
            });
          } else {
            toast.error("Registration failed. Please try again.", { position: "top-right" });
          }
      }
    } catch (error) {
      toast.error(`Network error. Please try again. Error: ${error}`, { position: "top-right" });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
        <form onSubmit={handleSubmit} className="bg-indigo-400 p-6 rounded shadow-md w-80">
            <h2 className="text-2xl font-bold mb-5 text-gray-800">Register</h2>
            <div className="mb-4">
                <label className="block text-gray-800">First Name</label>
                <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded mt-1"
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-800">Last Name</label>
                <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded mt-1"
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-800">Email</label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded mt-1"
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-800">Password</label>
                <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded mt-1"
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-800">Confirm Password</label>
                <input
                    type="password"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    required
                    className="w-full p-2 border border-gray-300 rounded mt-1"
                />
            </div>
            <button type="submit" className="w-full">
                Register
            </button>
        </form>
    </div>
  );
};