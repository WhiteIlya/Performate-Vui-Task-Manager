import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

export const Navbar: React.FC = () => {
  const { isAuthenticated, logout, name } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="bg-gray-800 text-white w-full">
      <div className="mx-auto flex items-center justify-between px-4 py-3">
        <Link className="text-2xl font-bold text-left" to="/">
          PerforMate - Voice Task Manager
        </Link>
        <div className="flex space-x-4">
          {!isAuthenticated ? (
            <>
              <div>
                <button >
                    <Link to="/login">
                        Log In
                    </Link>
                </button>
              </div>
              <div>
                <button >
                    <Link to="/register">
                        Register
                    </Link>
                </button>
              </div>
            </>
          ) : (
            <div className="flex space-x-4 items-center">
              <div>
                <span className="text-xl">Hello, {name || "buddy"}!</span>
              </div>
              <div>
                <button >
                    <Link to="/chat">
                        Chat
                    </Link>
                </button>
              </div>
              <div>
                <button
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
