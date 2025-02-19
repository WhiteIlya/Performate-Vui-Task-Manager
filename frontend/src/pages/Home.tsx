import { FC } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/Authcontext";

export const Home: FC = () => {
    const { isAuthenticated, name } = useAuth();

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <div className="flex flex-col items-center mb-20">
                <h1 className="text-4xl font-bold mb-4">Welcome to PerforMate</h1>
                <p className="text-lg text-gray-300 mb-6">
                    Boost your productivity with a voice-powered assistant that helps you manage tasks efficiently.
                </p>
                <ul className="text-gray-300 text-left list-disc list-inside">
                    <li>🗣️ Add tasks using voice commands</li>
                    <li>⏰ Get smart reminders and notifications</li>
                    <li>🔄 Automatically break down complex tasks</li>
                    <li>🎭 Customize your assistant's tone and personality</li>
                    <li>📊 Track progress and optimize productivity</li>
                </ul>
            </div>
            {!isAuthenticated ? (
                <>
                    <p className="text-lg text-gray-300 mb-6">Log in or Register to manage tasks with your assistant.</p>
                    <div className="flex gap-4">
                        <button>
                            <Link
                                to="/login"
                            >
                                Log In
                            </Link>
                        </button>
                        <button>
                            <Link
                                to="/register"
                            >
                                Register
                            </Link>
                        </button>
                    </div>
                </>
            ) : (
                <>
                    <h2 className="my-4">Hello, {name || "buddy"}!</h2>
                    <button>
                        <Link
                            to="/chat"
                        >
                            Go to Chat
                        </Link>
                    </button>
                </>
            )}
        </div>
    );
};
