import { FC } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

export const Home: FC = () => {
    const { isAuthenticated, name } = useAuth();
    console.log(isAuthenticated, name);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-4xl font-bold mb-4">Welcome to Performate</h1>
            <p className="text-lg mb-6">Log in to manage tasks with your assistant</p>
            {!isAuthenticated ? (
                <Link
                to="/login"
                className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                Log In
                </Link>
            ) : (
                <h2 className="mt-4">Hello, {name || "buddy"}!</h2>
            )}
        </div>
    );
};
