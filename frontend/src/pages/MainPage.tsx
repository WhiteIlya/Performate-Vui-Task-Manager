import { FC } from "react";
import { Chat } from "../components/Chat";

export const MainPage: FC = () => {
    return (
        <div className="flex h-screen">
            <Chat />
        </div>
    );
};
