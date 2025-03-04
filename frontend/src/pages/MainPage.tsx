import { FC, useRef } from "react";
import { Chat } from "../components/Chat";
import { Todo } from "../components/Todo";
import { Calendar } from "../components/CalendarView";

export const MainPage: FC = () => {
    const todoRef = useRef<{ fetchTasks: () => void } | null>(null);
    const calendarRef = useRef<{ fetchTasks: () => void } | null>(null);
    
    const refreshTasks = () => {
        if (todoRef.current) {
          todoRef.current.fetchTasks();
        }
        if (calendarRef.current) {
          calendarRef.current.fetchTasks();
      }
      };

    return (
        <div className="flex row h-screen">
            <Chat onTaskAdded={refreshTasks} />
            <Todo ref={todoRef} />
            <Calendar ref={calendarRef} />
        </div>
    );
};
