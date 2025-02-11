import { FC, useEffect, useState } from "react";

interface Notification {
    id: number;
    is_read: boolean;
    task_title: string;
    message: string;
    created_at: string;
}

export const Notifications: FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/main/notifications/`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
    })
      .then((res) => res.json())
      .then((data: Notification[]) => {
        setNotifications(data);
      })
      .catch((err) => console.error("Error fetching notifications:", err));
  }, []);

  const markAsRead = async (notificationId: number) => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/main/notifications/`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ notification_id: notificationId }),
      });

      setNotifications((prevNotifications) =>
        prevNotifications.map((notif) =>
          notif.id === notificationId ? { ...notif, is_read: true } : notif
        )
      );
    } catch (error) {
      console.error("Error marking notification as read:", error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 h-screen">
      <h1 className="text-2xl font-bold mb-4">🔔 Notifications</h1>
      {notifications.length === 0 ? (
        <p>No notifications yet.</p>
      ) : (
        <div className="divide-y divide-slate-950">
          {notifications.map((notif) => (
            <div key={notif.id} onClick={() => markAsRead(notif.id)} className={`p-4 ${notif.is_read ? "bg-gray-400" : "bg-indigo-400"}`}>
              <p className="text-slate-950">{notif.task_title}</p>
              <span className="text-sm text-slate-950">{new Date(notif.created_at).toLocaleString().split(",")[0]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
