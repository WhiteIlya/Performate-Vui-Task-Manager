import { FC, forwardRef, useEffect, useImperativeHandle, useState } from "react";
import { toast } from "react-toastify";

interface Task {
    id: number;
    title: string;
    due_date: string;
    is_completed: boolean;
}

export const Calendar: FC = forwardRef<{ fetchTasks: () => void }>((_, ref) => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [selectedDate, setSelectedDate] = useState<string | null>(null);
    
    const fetchTasks = async () => {
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
            const tasksWithDates = data.filter((task: Task) => task.due_date);
            setTasks(tasksWithDates);
        } catch (error) {
            toast.error(`${error}`, { position: "top-right" });
        }
    };

    useImperativeHandle(ref, () => ({
        fetchTasks,
    }));

    useEffect(() => {
        fetchTasks();
    }, []);

    const groupedTasks = tasks.reduce((acc, task) => {
        const date = new Date(task.due_date).toLocaleDateString();
        if (!acc[date]) acc[date] = [];
        acc[date].push(task);
        return acc;
    }, {} as Record<string, Task[]>);

    const today = new Date();
    
    const generateMonthDays = (monthOffset = 0) => {
        const firstDay = new Date(today.getFullYear(), today.getMonth() + monthOffset, 1);
        const lastDay = new Date(today.getFullYear(), today.getMonth() + monthOffset + 1, 0);

        const days = [];
        for (let i = 1; i <= lastDay.getDate(); i++) {
            days.push(new Date(today.getFullYear(), today.getMonth() + monthOffset, i));
        }

        const emptyCells = new Array(firstDay.getDay()).fill(null);
        return [...emptyCells, ...days];
    };

    const currentMonthDays = generateMonthDays(0);
    const nextMonthDays = generateMonthDays(1);

    return (
        <div className="p-4 h-screen w-1/3 border-l border-gray-700 bg-gray-900 text-white">
            <h2 className="text-2xl font-bold mb-4 text-center">Calendar</h2>

            {[currentMonthDays, nextMonthDays].map((monthDays, index) => (
                <div key={index} className="mb-6">
                    <h3 className="text-lg font-semibold text-center mb-2">
                        {new Date(today.getFullYear(), today.getMonth() + index, 1).toLocaleString('en-US', { month: 'long', year: 'numeric' })}
                    </h3>
                    
                    <div className="grid grid-cols-7 gap-2 text-center text-gray-400">
                        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                            <div key={day} className="font-bold">{day}</div>
                        ))}
                        {monthDays.map((day, i) => {
                            if (day === null) {
                                return <div key={i} className="p-2"></div>;
                            }
                            const dateStr = day.toLocaleDateString();
                            const hasTask = groupedTasks[dateStr]?.length > 0;
                            const isToday = day.toDateString() === today.toDateString();

                            return (
                                <div
                                    key={dateStr}
                                    className={`p-2 rounded-lg cursor-pointer ${
                                        hasTask ? "bg-indigo-500 text-white" : "bg-gray-800"
                                    } ${selectedDate === dateStr ? "ring-2 ring-indigo-300" : ""}
                                    ${isToday ? "ring-2 ring-yellow-300" : ""}`}
                                    onClick={() => setSelectedDate(dateStr)}
                                >
                                    {day.getDate()}
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}

            {selectedDate && groupedTasks[selectedDate] && (
                <div className="mt-4 p-4 bg-gray-800 rounded-lg">
                    <h3 className="text-lg font-bold mb-2">Tasks on {selectedDate}</h3>
                    <ul>
                        {groupedTasks[selectedDate].map((task) => (
                            <li key={task.id} className="p-2 bg-indigo-600 rounded mb-2">
                                {task.title}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
});
