import { ReactMediaRecorder } from "react-media-recorder";
import RecordIcon from "../icons/RecordIcon.tsx";

type Props = {
  handleStop: any;
};

export const RecordMessage = ({ handleStop }: Props) => {
    return (
        <ReactMediaRecorder
        audio
        onStop={handleStop}
        render={({ status, startRecording, stopRecording }) => (
            <div>
            <button
                onMouseDown={startRecording}
                onMouseUp={stopRecording}
                className="p-2 rounded-full"
            >
                <RecordIcon
                classText={
                    status == "recording"
                    ? "animate-pulse text-red-500"
                    : "text-sky-500"
                }
                />
            </button>
            {/* <p className="mt-2 text-white font-light">{status}</p> */}
            </div>
        )}
        />
    );
};