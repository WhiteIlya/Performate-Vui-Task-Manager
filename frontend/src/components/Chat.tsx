import { FC, useState } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { RecordMessage } from "./RecordMessage";

interface ChatProps {
    onTaskAdded: () => void;
}

export const Chat: FC<ChatProps> = ({ onTaskAdded }) => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");

const playAudio = (base64Audio: string) => {
    try {
        const binaryString = atob(base64Audio);
        const binaryData = new Uint8Array(binaryString.length);

        for (let i = 0; i < binaryString.length; i++) {
        binaryData[i] = binaryString.charCodeAt(i);
        }

        const audioBlob = new Blob([binaryData], { type: "audio/mpeg" });
        const audioUrl = URL.createObjectURL(audioBlob);

        const audio = new Audio(audioUrl);
        audio.play();
    } catch (error) {
        toast.error(`Failed to play audio. Error: ${error}`, { position: "top-right" });
    }
  };

  const handleVoiceMessage = async (blobUrl: string) => {
    setIsLoading(true);

    fetch(blobUrl)
      .then((res) => res.blob())
      .then(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "audio.wav");

        const audioURL = URL.createObjectURL(blob);
        const audio = new Audio(audioURL);
        audio.play();

        try {
          const access_token = localStorage.getItem("access");
          const response = await fetch(
            `${import.meta.env.VITE_API_URL}/main/assistant-voice-request/`,
            {
              method: "POST",
              headers: {
                Authorization: `Bearer ${access_token}`,
              },
              body: formData,
            }
          );

          if (!response.ok) {
            throw new Error(`Failed to process voice message. Reason: ${response.statusText}`);
          }

          const data = await response.json();

          setMessages((prev) => [
            ...prev,
            { sender: "user", text: data.input_text },
            { sender: "assistant", text: data.response },
          ]);

          playAudio(data.audio_response);

          onTaskAdded();
        } catch (error) {
          toast.error(`Failed to send voice message: ${error}`, {position: "top-right",});
        } finally {
          setIsLoading(false);
        }
      });

  };


  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: input }]);
    setIsLoading(true);

    try {
      const access_token = localStorage.getItem("access");
      const response = await fetch(`${import.meta.env.VITE_API_URL}/main/assistant-request/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${access_token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error(`Failed to process text message. Reason: ${response.statusText}`);
        
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { sender: "assistant", text: data.response },
      ]);

      onTaskAdded();
    } catch (error) {
        toast.error(`Failed to send message: ${error}`, { position: "top-right" });
    } finally {
        setIsLoading(false);
    }
    setInput("");
  };

  return (
    <div className="flex flex-col h-2/3 w-1/3 bg-indigo-200">
        <div className="flex-1 overflow-y-auto p-4 hide-scrollbar">
            {messages.map((msg, index) => (
            <div
                key={index}
                className={`mb-2 ${
                    msg.sender === "user" ? "text-right" : "text-left"
                }`}
            >
                <div
                className={`inline-block px-4 py-2 rounded ${
                    msg.sender === "user"
                    ? "bg-indigo-400 text-black"
                    : "bg-gray-800 text-white"
                }`}
                >
                {msg.text}
                </div>
            </div>
            ))}
            {isLoading && (
                <div className="text-center text-gray-500 italic mt-4">
                    Processing your message...
                </div>
            )}
        </div>
        <div className="p-6 border-t-2 border-indigo-400">
            <div className="flex items-center space-x-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type a message"
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 placeholder-indigo-500"
                    disabled={isLoading}
                />
                <RecordMessage handleStop={handleVoiceMessage} />
            </div>
            <button
                onClick={sendMessage}
                className="mt-2 w-full"
            >
                Send
            </button>
        </div>
    </div>
  );
};