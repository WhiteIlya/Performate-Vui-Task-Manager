import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

interface Notification {
  id: number;
  is_read: boolean;
}

export const Navbar: React.FC = () => {
  const { isAuthenticated, logout, name } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      fetch(`${import.meta.env.VITE_API_URL}/main/notifications/`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
      })
        .then((res) => res.json())
        .then((data: Notification[]) => {
          const unread = data.filter((notif) => !notif.is_read).length;
          setUnreadCount(unread);
        })
        .catch((err) => console.error("Error fetching notifications:", err));
    }
  }, [isAuthenticated]);

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
              <button >
                  <Link to="/login">
                      Log In
                  </Link>
              </button>
              <button >
                  <Link to="/register">
                      Register
                  </Link>
              </button>
            </>
          ) : (
            <div className="flex space-x-4 items-center">
              <span className="text-xl">Hello, {name || "buddy"}!</span>
              <button >
                  <Link to="/chat">
                      Chat
                  </Link>
              </button>
              <button className="relative">
                <Link to="/notifications">
                  🔔 Notifications
                  {unreadCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold">
                      {unreadCount}
                    </span>
                  )}
                </Link>
              </button>
              <button
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
