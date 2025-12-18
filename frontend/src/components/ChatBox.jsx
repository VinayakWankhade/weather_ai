import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../services/api";
import { Send, CloudSun, Loader2, Sparkles, MapPin } from "lucide-react";

export default function ChatBox() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([
        { role: "ai", content: "Hello! I'm your Weather AI. Ask me about the weather in any city!" }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { role: "user", content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setLoading(true);

        try {
            const response = await sendMessage(userMessage.content);
            const aiMessage = { role: "ai", content: response };
            setMessages((prev) => [...prev, aiMessage]);
        } catch (error) {
            console.error(error);
            const errorMessage = { role: "ai", content: `Sorry, I encountered an error: ${error.message || error.response?.data?.detail || "Unknown error"}` };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            handleSend();
        }
    };

    return (
        <div className="w-full h-[600px] flex flex-col rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 shadow-2xl overflow-hidden font-sans">
            {/* Header */}
            <div className="p-6 bg-white/5 border-b border-white/10 flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/20 text-blue-400">
                    <CloudSun size={24} />
                </div>
                <div>
                    <h2 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Weather AI
                    </h2>
                    <p className="text-xs text-slate-400">Powered by LangChain & OpenRouter</p>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`max-w-[80%] p-4 rounded-2xl ${msg.role === "user"
                                ? "bg-blue-600/80 text-white rounded-br-none shadow-lg shadow-blue-900/20"
                                : "bg-slate-800/80 text-slate-200 rounded-bl-none shadow-lg border border-white/5"
                                } backdrop-blur-sm transition-all duration-300 animate-fade-in`}
                        >
                            {msg.role === "ai" && (
                                <div className="flex items-center gap-2 mb-1 text-xs text-blue-400 font-medium">
                                    <Sparkles size={12} /> AI Assistant
                                </div>
                            )}
                            <p className="leading-relaxed">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-800/80 text-slate-200 p-4 rounded-2xl rounded-bl-none border border-white/5 flex items-center gap-2">
                            <Loader2 className="animate-spin text-blue-400" size={16} />
                            <span className="text-sm">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/5 border-t border-white/10 backdrop-blur-sm">
                <div className="flex items-center gap-2 bg-slate-900/50 p-2 rounded-xl border border-white/10 focus-within:border-blue-500/50 transition-colors">
                    <MapPin size={20} className="text-slate-500 ml-2" />
                    <input
                        className="flex-1 bg-transparent border-none outline-none text-white placeholder-slate-500 px-2"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about weather (e.g., Weather in Pune?)"
                        disabled={loading}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="p-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white transition-all shadow-lg hover:shadow-blue-500/25"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
