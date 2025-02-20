import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

interface Voice {
    voice_id: string;
    name: string;
    preview_url: string;
    accent: string;
    gender: string;
    age: string;
    description: string;
    use_case: string;
    persona_tone: string;
    interaction_style: string;
    formality_level: string;
    response_length: string;
    paraphrase_variability: string;
    personalized_naming: string;
    emotional_expressiveness: string;
    reminder_frequency: string;
    preferred_reminder_time: string;
    reminder_tone: string;
    voice_feedback_style: string;
    other_preferences: string;
}

interface VoiceFilter {
    accent: string;
    description: string;
    age: string;
    gender: string;
    use_case: string;
}

const personaTones = ["friendly", "professional", "strict", "playful"];
const formalityLevels = ["formal", "neutral", "informal"];
const personaTraits = ["empathetic", "direct", "humorous", "encouraging", "supportive"];
const responseLengths = ["short", "medium", "long"];
const paraphraseVariabilities = ["low", "medium", "high"];
const personalizedNamingOptions = ["use my name", "do not use my name"];
const emotionalExpressivenessLevels = ["low", "moderate", "high"];
const reminderFrequencies = ["low", "medium", "high"];
const preferredReminderTimes = ["morning", "evening", "dynamic"];
const reminderTones = ["motivational", "strict", "playful"];
const progressReportingOptions = ["basic", "detailed", "gamified"];
const interactionStyles = ["coach", "friend", "neutral"];
const voiceFeedbackStyles = ["concise", "detailed"];

const availableVoices: VoiceFilter[] = [
    { accent: "American", description: "expressive", age: "middle-aged", gender: "female", use_case: "social media" },
    { accent: "American", description: "confident", age: "middle-aged", gender: "male", use_case: "social media" },
    { accent: "American", description: "soft", age: "young", gender: "female", use_case: "news" },
    { accent: "American", description: "upbeat", age: "young", gender: "female", use_case: "social media" },
    { accent: "Transatlantic", description: "intense", age: "middle-aged", gender: "male", use_case: "characters" },
    { accent: "American", description: "confident", age: "middle-aged", gender: "non-binary", use_case: "social media" },
    { accent: "American", description: "articulate", age: "young", gender: "male", use_case: "narration" },
    { accent: "Swedish", description: "seductive", age: "young", gender: "female", use_case: "characters" },
    { accent: "British", description: "confident", age: "middle-aged", gender: "female", use_case: "news" },
    { accent: "American", description: "friendly", age: "middle-aged", gender: "female", use_case: "narration" },
    { accent: "American", description: "friendly", age: "young", gender: "male", use_case: "social media" },
    { accent: "American", description: "expressive", age: "young", gender: "female", use_case: "conversational" },
    { accent: "American", description: "friendly", age: "middle-aged", gender: "male", use_case: "conversational" },
    { accent: "American", description: "casual", age: "middle-aged", gender: "male", use_case: "conversational" },
    { accent: "American", description: "deep", age: "middle-aged", gender: "male", use_case: "narration" },
    { accent: "British", description: "authoritative", age: "middle-aged", gender: "male", use_case: "news" },
    { accent: "British", description: "warm", age: "middle-aged", gender: "female", use_case: "narration" },
    { accent: "American", description: "trustworthy", age: "old", gender: "male", use_case: "narration" },
];

export const VoiceConfigPage = () => {
    const [filters, setFilters] = useState({
        accent: "",
        gender: "",
        age: "",
        description: "",
        use_case: "",
    });

    const [voices, setVoices] = useState<Voice[]>([]);
    const [selectedVoice, setSelectedVoice] = useState<Voice>();
    const [settings, setSettings] = useState({
        stability: 0.5,
        similarity_boost: 0.8,
        style: 0.0,
        use_speaker_boost: true,
    });
    const [messageSettings, setMessageSettings] = useState({
        persona_tone: "",
        formality_level: "",
        persona_traits: "",
        response_length: "",
        paraphrase_variability: "",
        personalized_naming: "",
        emotional_expressiveness: "",
        reminder_frequency: "",
        preferred_reminder_time: "",
        reminder_tone: "",
        progress_reporting: "",
        interaction_style: "",
        voice_feedback_style: "",
        assistant_name: "",
        other_preferences: ""
    })

    const navigate = useNavigate();

    const getFilteredOptions = (field: keyof VoiceFilter) => {
        return Array.from(
            new Set(
                availableVoices
                    .filter((voice) =>
                        Object.entries(filters)
                            .filter(([key, value]) => key !== field && value)
                            .every(([key, value]) => voice[key as keyof VoiceFilter] === value)
                    )
                    .map((voice) => voice[field])
            )
        );
    };

    const fetchVoices = async () => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/main/voice-selection/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access")}`,
                },
                body: JSON.stringify(filters),
            });

            const data = await response.json();
            if (Array.isArray(data.voices)) {
                setVoices(data.voices);
            } else {
                throw new Error("Invalid response format");
            }
        } catch (error) {
            toast.error("Failed to load voices. Error: " + error);
        }
    };

    const fetchVoiceSettings = async (voice_id: string) => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/main/voice-settings/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access")}`,
                },
                body: JSON.stringify({ voice_id }),
            });
    
            const data = await response.json();
            if (data.stability !== undefined) {
                setSettings(data);
            } else {
                throw new Error("Invalid settings format");
            }
        } catch (error) {
            toast.error("Failed to load voice settings. Error: " + error);
        }
    };

    const handleVoiceSelect = (voice: Voice) => {
        setSelectedVoice(voice);
        fetchVoiceSettings(voice.voice_id);
    };

    const handleChange = (field: string, value: string) => {
        setMessageSettings({ ...messageSettings, [field]: value });
    };

    const handleSave = async () => {
        if (!selectedVoice) {
            toast.error("Please select a voice.");
            return;
        }
    
        const payload = {
            voice_name: messageSettings.assistant_name || selectedVoice.name,
            ...selectedVoice,
            ...settings,
            ...messageSettings
        };
    
        console.log("Saving voice config:", payload);
    
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/main/voice-config/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access")}`,
                },
                body: JSON.stringify(payload),
            });
    
            const responseData = await response.json();
    
            if (response.ok) {
                toast.success("Voice assistant configurations saved!");
                setTimeout(() => navigate("/chat"), 2000);
            } else {
                toast.error(`Failed to save voice: ${responseData.error || "Unknown error"}`);
            }
        } catch (error) {
            toast.error(`Error: ${error}`);
        }
    };

    const fetchUserVoiceConfig = async (
        setSettings: React.Dispatch<React.SetStateAction<typeof settings>>,
        setMessageSettings: React.Dispatch<React.SetStateAction<typeof messageSettings>>
    ) => {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/main/voice-config/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("access")}`,
                },
            });
    
            const data = await response.json();
    
            if (response.ok && data.voice_config) {
    
                setSettings({
                    stability: data.voice_config.stability || 0.5,
                    similarity_boost: data.voice_config.similarity_boost || 0.8,
                    style: data.voice_config.style || 0.0,
                    use_speaker_boost: data.voice_config.use_speaker_boost || true,
                });
    
                setMessageSettings({
                    persona_tone: data.voice_config.persona_tone || "",
                    formality_level: data.voice_config.formality_level || "",
                    persona_traits: data.voice_config.persona_traits || "",
                    response_length: data.voice_config.response_length || "",
                    paraphrase_variability: data.voice_config.paraphrase_variability || "",
                    personalized_naming: data.voice_config.personalized_naming || "",
                    emotional_expressiveness: data.voice_config.emotional_expressiveness || "",
                    reminder_frequency: data.voice_config.reminder_frequency || "",
                    preferred_reminder_time: data.voice_config.preferred_reminder_time || "",
                    reminder_tone: data.voice_config.reminder_tone || "",
                    progress_reporting: data.voice_config.progress_reporting || "",
                    interaction_style: data.voice_config.interaction_style || "",
                    voice_feedback_style: data.voice_config.voice_feedback_style || "",
                    assistant_name: data.voice_config.voice_name || "",
                    other_preferences: data.voice_config.other_preferences || "",
                });
    
                toast.success("Loaded voice configurations!");
            }
        } catch (error) {
            console.error("Error fetching voice config:", error);
            toast.error("Failed to load voice configuration.");
        }
    };

    useEffect(() => {
        fetchUserVoiceConfig(setSettings, setMessageSettings);
    }, []);

    return (
        <div className="container mx-auto p-6 h-screen">
            <h2 className="text-2xl font-bold mb-4">Voice Assistant Configuration</h2>

            <h3 className="text-xl font-bold mb-4">Step 1: Filter Voices</h3>
            <div className="grid grid-cols-2 gap-4">
                {Object.entries(filters).map(([key, value]) => (
                    <select
                        key={key}
                        value={value}
                        onChange={(e) => setFilters({ ...filters, [key]: e.target.value })}
                        className="border border-gray-700 rounded-lg p-2"
                    >
                        <option value="">{`Select ${key}`}</option>
                        {getFilteredOptions(key as keyof VoiceFilter).map((option) => (
                            <option key={option} value={option}>
                                {option.charAt(0).toUpperCase() + option.slice(1)}
                            </option>
                        ))}
                    </select>
                ))}
            </div>

            <button className="mt-4" onClick={fetchVoices}>
                Load Voices
            </button>

            {voices.length > 0 && <h3 className="text-xl font-bold my-4">Step 2: Choose Voice</h3>}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                {voices.map((voice) => (
                    <div key={voice.voice_id} className="p-4 border border-gray-600 rounded-lg flex flex-col">
                        <p className="p-2 font-bold text-indigo-500">{voice.name}</p>
                        <audio controls src={voice.preview_url}></audio>
                        <button className="mt-3 self-end" onClick={() => handleVoiceSelect(voice)}>Select</button>
                    </div>
                ))}
            </div>

            {selectedVoice && (
                <>
                    <div className="mt-6">
                        <h3 className="text-xl font-bold">Step 3: Adjust Voice Settings</h3>
                        <p className="text-gray-600 mb-4">
                            Fine-tune the voice parameters to achieve the desired sound or leave default values.
                        </p>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="flex flex-col">
                                <div className="flex gap-4 text-indigo-500 font-bold">
                                    <label title="Higher stability makes the voice sound more predictable and controlled. Lower stability adds more variation and unpredictability.">
                                        Stability
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={settings.stability}
                                        onChange={(e) => setSettings({ ...settings, stability: parseFloat(e.target.value) })}
                                    />
                                    <span>{settings.stability}</span>
                                </div>
                                <p className="text-sm text-gray-500">
                                    Lower values make the voice more dynamic and expressive, while higher values make it more monotone and controlled.
                                </p>
                            </div>

                            <div className="flex flex-col">
                                <div className="flex gap-4 text-indigo-500 font-bold">
                                    <label title="Higher similarity makes the voice closer to the original source. Lower similarity introduces more variation.">
                                        Similarity Boost
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={settings.similarity_boost}
                                        onChange={(e) => setSettings({ ...settings, similarity_boost: parseFloat(e.target.value) })}
                                    />
                                    <span>{settings.similarity_boost}</span>
                                </div>
                                <p className="text-sm text-gray-500">
                                    Higher values make the voice more similar to the original sample, but may reduce natural variation.
                                </p>
                            </div>

                            <div className="flex flex-col">
                                <div className="flex gap-4 text-indigo-500 font-bold">
                                    <label title="Adjusts the expressiveness of the voice. Higher values make the voice sound more dramatic.">
                                        Style
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={settings.style}
                                        onChange={(e) => setSettings({ ...settings, style: parseFloat(e.target.value) })}
                                    />
                                    <span>{settings.style}</span>
                                </div>
                                <p className="text-sm text-gray-500">
                                    Lower values sound neutral and professional, while higher values add dramatic emotion and expressiveness.
                                </p>
                            </div>

                            <div className="flex flex-col">
                                <div className="flex gap-4 text-indigo-500 font-bold">
                                    <label title="Enables volume and clarity enhancements. Useful for ensuring the voice is more audible in noisy environments.">
                                        Use Speaker Boost
                                    </label>
                                    <input
                                        type="checkbox"
                                        checked={settings.use_speaker_boost}
                                        onChange={(e) => setSettings({ ...settings, use_speaker_boost: e.target.checked })}
                                    />
                                </div>
                                <p className="text-sm text-gray-500">
                                    <b>Enabled:</b> Louder, clearer voice with consistent tone.<br />
                                    <b>Disabled:</b> More natural and nuanced intonation.
                                </p>
                            </div>
                        </div>
                    </div>

                    <h3 className="text-xl font-bold my-4">Step 4: Assistant Configuration</h3>
                    <div className="grid grid-cols-2 gap-4">
                        {[
                            { label: "Persona Tone", field: "persona_tone", options: personaTones },
                            { label: "Formality Level", field: "formality_level", options: formalityLevels },
                            { label: "Persona Traits", field: "persona_traits", options: personaTraits },
                            { label: "Response Length", field: "response_length", options: responseLengths },
                            { label: "Paraphrase Variability", field: "paraphrase_variability", options: paraphraseVariabilities },
                            { label: "Personalized Naming", field: "personalized_naming", options: personalizedNamingOptions },
                            { label: "Emotional Expressiveness", field: "emotional_expressiveness", options: emotionalExpressivenessLevels },
                            { label: "Reminder Frequency", field: "reminder_frequency", options: reminderFrequencies },
                            { label: "Preferred Reminder Time", field: "preferred_reminder_time", options: preferredReminderTimes },
                            { label: "Reminder Tone", field: "reminder_tone", options: reminderTones },
                            { label: "Progress Reporting", field: "progress_reporting", options: progressReportingOptions },
                            { label: "Interaction Style", field: "interaction_style", options: interactionStyles },
                            { label: "Voice Feedback Style", field: "voice_feedback_style", options: voiceFeedbackStyles }
                        ].map(({ label, field, options }) => (
                            <div key={field} className="flex flex-col">
                                <label className="font-bold text-indigo-500 mb-1">{label}</label>
                                <select
                                    value={messageSettings[field]}
                                    onChange={(e) => handleChange(field, e.target.value)}
                                    className="border rounded-lg p-2 border-gray-700"
                                >
                                    <option value="">{`Select ${label}`}</option>
                                    {options.map((option) => (
                                        <option key={option} value={option}>{option.charAt(0).toUpperCase() + option.slice(1)}</option>
                                    ))}
                                </select>
                            </div>
                        ))}
                        <div className="flex flex-col">
                            <label className="font-bold text-indigo-500 mb-1">Assistant Name</label>
                            <input
                                type="text"
                                value={messageSettings.assistant_name}
                                onChange={(e) => handleChange("assistant_name", e.target.value)}
                                className="border border-gray-700 rounded-lg p-2"
                            />
                        </div>
                        <div className="col-span-2 flex flex-col">
                            <label className="font-bold text-indigo-500 mb-1">Other Preferences</label>
                            <textarea
                                value={messageSettings.other_preferences}
                                onChange={(e) => handleChange("other_preferences", e.target.value)}
                                className="border border-gray-700 rounded-lg p-2 h-20"
                                placeholder="E.g., I want more humor, provide fun facts, etc."
                            />
                        </div>
                    </div>
                    
                    <button className="mt-4 mb-20" onClick={handleSave}>
                        Save Configuration
                    </button>
            </>
            )}
        </div>
    );
};
