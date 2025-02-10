import { FC, forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { toast } from "react-toastify";
import CalendarIcon from "../icons/CalendarIcon.tsx";

interface SubTask {
    id: number;
    title: string;
    due_date: string;
    is_completed: boolean;
}

interface Task {
    id: number;
    title: string;
    created_at: string;
    description: string;
    due_date: string;
    is_completed: boolean;
    subtasks: SubTask[];
}

export const Todo: FC = forwardRef<{ fetchTasks: () => void }>((_, ref) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editTask, setEditTask] = useState<Task | SubTask| null>(null);
  const [isEditingSubtask, setIsEditingSubtask] = useState(false);

  const completedTasks = tasks.filter((task) => task.is_completed);
  const activeTasks = tasks.filter((task) => !task.is_completed);

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
        throw new Error(`Failed to fetch tasks. Reason: ${response.statusText}`);
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

  const updateTask = async (taskId: number, updates: Partial<Task | SubTask>, isSubtask = false) => {
    try {
      const access_token = localStorage.getItem("access");
      const response = await fetch(`${import.meta.env.VITE_API_URL}/main/tasks/update/`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ task_id: taskId, task_type: isSubtask ? "subtask" : "main_task", ...updates }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update task. Reason: ${response.statusText}`);
      }

      toast.success(isSubtask ? "Subtask updated successfully" : "Task updated successfully", {
        position: "top-right",
      });
      fetchTasks();
    } catch (error) {
      toast.error(`${error}`, { position: "top-right" });
    }
  };

  const handleEditClick = (task: Task | SubTask, isSubtask = false) => {
    setEditTask(task);
    setIsEditingSubtask(isSubtask);
  };

  const handleSaveClick = () => {
    if (editTask) {
      updateTask(
        editTask.id,
        {
            title: editTask.title,
            description: !isEditingSubtask && "description" in editTask ? editTask.description : undefined,
        },
        isEditingSubtask ? true : false,
    );
      setEditTask(null);
      setIsEditingSubtask(false);
    }
  };

  const handleCancelClick = () => {
      setEditTask(null);
      setIsEditingSubtask(false);
  };

  const toggleCompleted = (task: Task | SubTask, isSubtask = false) => {
    updateTask(task.id, { is_completed: !task.is_completed }, isSubtask);
  };

  return (
    <div className="flex flex-col p-4 h-screen w-1/3">
      <h2 className="text-3xl font-bold mb-4">ToDo Tasks</h2>
      {isLoading ? (
        <p>Loading tasks...</p>
      ) : activeTasks.length === 0 && completedTasks.length === 0 ? (
        <p>No tasks found.</p>
      ) : (
        <>
            <div className="space-y-2 h-[60rem] overflow-y-auto hide-scrollbar">
                {activeTasks.map((task) => (
                    <div
                    key={task.id}
                    className="p-2 bg-indigo-400 rounded shadow hover:bg-indigo-500"
                    >
                        {editTask && editTask.id === task.id && !isEditingSubtask ? (
                            <div>
                                <input
                                    type="text"
                                    value={editTask.title}
                                    onChange={(e) =>
                                        setEditTask({ ...editTask, title: e.target.value })
                                    }
                                    className="mb-2 w-full px-2 py-1 border rounded"
                                />
                                <textarea
                                    value={"description" in editTask ? editTask.description : ""}
                                    onChange={(e) =>
                                    setEditTask({ ...editTask, description: e.target.value })
                                    }
                                    className="mb-2 w-full px-2 py-1 border rounded"
                                />
                                <div className="flex space-x-2">
                                    <button onClick={handleSaveClick} className="px-3 p-0.5 rounded">
                                        Save
                                    </button>
                                    <button onClick={handleCancelClick} className="px-3 p-0.5 rounded">
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="flex justify-between items-center">
                                    <input 
                                        type="checkbox"
                                        checked={task.is_completed}
                                        onChange={() => toggleCompleted(task)}
                                        className="mr-2 cursor-pointer"
                                    />
                                    <p className="text-md text-black mr-1 flex-1" onClick={() => handleEditClick(task)}>{task.title}</p>
                                    <p className="text-xs text-black">
                                        {new Date(task.created_at).toLocaleString().split(",")[0]}
                                    </p>
                                </div>
                                {task.due_date && (
                                  <div className="flex items-center ml-5 gap-1">
                                    <CalendarIcon classText="text-black"/>
                                    <p className="text-xs text-black">
                                        {new Date(task.due_date).toLocaleString().split(",")[0]}
                                    </p>
                                  </div>
                                )}
                                {task.subtasks.length > 0 && (
                                    <div className="ml-5 mt-2 space-y-2">
                                        {task.subtasks.map((subtask) => (
                                            <div
                                                key={subtask.id}
                                                className={`p-1 rounded flex ${
                                                    subtask.is_completed
                                                    ? "bg-green-200 text-black line-through"
                                                    : "bg-gray-300 text-black"
                                                }`}
                                            >
                                                <input
                                                    type="checkbox"
                                                    checked={subtask.is_completed}
                                                    onChange={() => toggleCompleted(subtask, true)}
                                                    className="mr-2 cursor-pointer"
                                                />
                                                {editTask && editTask.id === subtask.id && isEditingSubtask ? (
                                                    <>
                                                        <input
                                                            type="text"
                                                            value={editTask.title}
                                                            onChange={(e) => setEditTask({ ...editTask, title: e.target.value })}
                                                            className="bg-gray-300 flex-1 rounded py-1"
                                                        />
                                                        <div className="flex space-x-2">
                                                            <button onClick={handleSaveClick} className="px-1 p-0.5 rounded">
                                                                ok
                                                            </button>
                                                            <button onClick={handleCancelClick} className="px-1 p-0.5 rounded">
                                                                cancel
                                                            </button>
                                                        </div>
                                                    </>
                                                ) : (
                                                  <>
                                                    <p
                                                        onClick={() => handleEditClick(subtask, true)}
                                                        className="flex-1 cursor-pointer"
                                                    >
                                                        {subtask.title}
                                                    </p>
                                                    {subtask.due_date && (
                                                      <div className="flex items-center ml-5 gap-1">
                                                        <CalendarIcon classText="text-black"/>
                                                        <p className="text-xs text-black">
                                                            {new Date(subtask.due_date).toLocaleString().split(",")[0]}
                                                        </p>
                                                      </div>
                                                    )}
                                                  </>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                ))}
            </div>
            <hr className="my-4 border-t-2 border-gray-300" />

            <h2 className="text-2xl font-bold mb-4">Completed Tasks</h2>
            <div className="space-y-2 h-[26rem] overflow-y-auto hide-scrollbar">
                {completedTasks.map((task) => (
                <div
                    key={task.id}
                    className="p-2 bg-gray-500 text-white rounded shadow"
                >
                    <div className="flex justify-between items-center">
                    <input
                        type="checkbox"
                        checked={task.is_completed}
                        onChange={() => toggleCompleted(task)}
                        className="mr-2 cursor-pointer"
                    />
                    <p className="text-md flex-1">{task.title}</p>
                    <p className="text-xs">
                        {new Date(task.created_at).toLocaleString().split(",")[0]}
                    </p>
                    </div>
                </div>
                ))}
            </div>
        </>
      )}
    </div>
  );
});
