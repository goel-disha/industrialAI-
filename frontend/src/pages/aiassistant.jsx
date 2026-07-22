import { useState } from "react";
import api from "../api/api";
import "../styles/aiassistant.css";

export default function AIAssistant() {
    

    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: "Hello! I'm your IndustrialAI Assistant. Ask me anything about the machine."
        }
    ]);

    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);

    async function send() {

        if (!question.trim()) return;

        const userMessage = {
            role: "user",
            content: question
        };

        setMessages(prev => [...prev, userMessage]);

        setLoading(true);

        try {

            const res = await api.post("/chat", {
                message: question
            });

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: res.data.response
                }
            ]);

        } catch {

            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "Unable to connect to AI."
                }
            ]);

        }

        setQuestion("");

        setLoading(false);

    }

    return (

        <div className="chat-page">

            <h1>IndustrialAI Assistant</h1>

            <div className="chat-box">

                {messages.map((msg, index) => (

                    <div
                        key={index}
                        className={
                            msg.role === "user"
                                ? "user-message"
                                : "bot-message"
                        }
                    >

                        <b>

                            {msg.role === "user"
                                ? "You"
                                : "AI"}

                        </b>

                        <br />

                        {msg.content}

                    </div>

                ))}

                {loading &&

                    <div className="bot-message">

                        Thinking...

                    </div>

                }

            </div>

            <div className="chat-input">

                <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask about machine..."
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            send();
                        }
                    }}
                />

                <button onClick={send}>

                    Send

                </button>

            </div>

        </div>

    );

}