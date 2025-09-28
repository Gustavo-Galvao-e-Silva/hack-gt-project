"use client";
import React, { useState } from "react";
import axios from "axios";

export default function ChatUI({ concept }) {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const agentId = "weatherAgent";

  const sendMessage = async (text) => {
    setIsLoading(true);
    setMessages((msgs) => [...msgs, { role: "user", content: text }]);
    try {
      const res = await axios.post(`http://localhost:4111/api/agents/${agentId}/generate`,
        {
          messages: [{ role: "user", content: text }],
        }
      );
      
      // Log the full response to understand the structure
      console.log('Full response:', res.data);
      
      // Extract the text from Mastra agent response
      const reply = res.data.text || "No reply";
      
      setMessages((msgs) => [...msgs, { role: "bot", content: reply }]);
    } catch (err) {
      console.error('Error details:', err);
      setMessages((msgs) => [...msgs, { role: "bot", content: "Error: " + err.message }]);
    }
    setIsLoading(false);
  };

  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", width: "400px", height: "500px", overflowY: "scroll" }}>
      {messages.length === 0 && <p>No messages yet. Start typing!</p>}
      {messages.map((msg, i) => (
        <div key={i} style={{ marginBottom: "0.5rem" }}>
          <b>{msg.role}:</b> {msg.content}
        </div>
      ))}
      {isLoading && <p>🤖 Thinking...</p>}
      <input
        style={{ width: "100%", marginTop: "1rem" }}
        placeholder="Type a message..."
        onKeyDown={(e) => {
          if (e.key === "Enter" && e.currentTarget.value.trim() !== "") {
            sendMessage(e.currentTarget.value);
            e.currentTarget.value = "";
          }
        }}
      />
    </div>
  );
}