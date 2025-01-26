import { FC, forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { toast } from "react-toastify";

interface Task {
  id: number;
  title: string;
  created_at: string;
  description: string;
  due_date: string;
  is_completed: boolean;
}

export const Todo: FC = forwardRef<{ fetchTasks: () => void }>((_, ref) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchTasks = async () => {
    setIsLoading(true);
    try {
      const access_token = localStorage.getItem("access");
      const response = await fetch(`${import.meta.env.VITE_API_URL}/main/todo/`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${access_token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch tasks.");
      }

      const data = await response.json();
      setTasks(data);
    } catch (error) {
      toast.error(`${error}`, { position: "top-right" });
    } finally {
      setIsLoading(false);
    }
  };

  useImperativeHandle(ref, () => ({
    fetchTasks,
  }));

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <div className="flex flex-col p-4 h-2/3 w-1/3 overflow-y-auto hide-scrollbar">
      <h2 className="text-3xl font-bold mb-4">ToDo Tasks</h2>
      {isLoading ? (
        <p>Loading tasks...</p>
      ) : tasks.length === 0 ? (
        <p>No tasks found.</p>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="flex p-2 bg-indigo-400 items-center rounded shadow hover:bg-indigo-500 justify-between"
            >
              <p className="text-md text-black mr-1">{task.title}</p>
              <p className="text-xs text-black">
                {new Date(task.created_at).toLocaleString().split(",")[0]}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});
