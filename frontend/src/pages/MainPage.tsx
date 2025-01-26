import { FC, useRef } from "react";
import { Chat } from "../components/Chat";
import { Todo } from "../components/Todo";

export const MainPage: FC = () => {
    const todoRef = useRef<{ fetchTasks: () => void } | null>(null);
    
    const refreshTasks = () => {
        console.log("Refreshing tasks...");
        if (todoRef.current) {
          todoRef.current.fetchTasks();
        }
      };

    return (
        <div className="flex row h-screen">
            <Chat onTaskAdded={refreshTasks} />
            <Todo ref={todoRef} />
        </div>
    );
};
