import { FC } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

export const Home: FC = () => {
    const { isAuthenticated, name } = useAuth();

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-4xl font-bold mb-4">Welcome to PerforMate</h1>
            {!isAuthenticated ? (
                <>
                    <p className="text-lg mb-6">Log in to manage tasks with your assistant</p>
                    <button>
                        <Link
                            to="/login"
                        >
                            Log In
                        </Link>
                    </button>
                </>
            ) : (
                <h2 className="mt-4">Hello, {name || "buddy"}!</h2>
            )}
        </div>
    );
};
