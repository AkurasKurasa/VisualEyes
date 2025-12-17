import React from 'react';
import { FaPaperPlane } from 'react-icons/fa';

const Chatbot = () => {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#1e1e1e', color: '#fff' }}>
            {/* Messages Area */}
            <div style={{ flex: 1, padding: '20px', overflowY: 'auto' }}>
                <div style={{ marginBottom: '15px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '5px', color: '#4caf50' }}>AI Assistant</div>
                    <div style={{ backgroundColor: '#2d2d2d', padding: '10px', borderRadius: '8px', maxWidth: '80%' }}>
                        Hello! How can I help you with your code today?
                    </div>
                </div>

                <div style={{ marginBottom: '15px', display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '5px', color: '#2196f3' }}>You</div>
                    <div style={{ backgroundColor: '#005a9e', padding: '10px', borderRadius: '8px', maxWidth: '80%' }}>
                        Can you help me fix a bug?
                    </div>
                </div>
            </div>

            {/* Input Area */}
            <div style={{ padding: '15px', borderTop: '1px solid #333', display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    placeholder="Type a message..."
                    style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '4px',
                        border: '1px solid #333',
                        backgroundColor: '#2d2d2d',
                        color: '#fff',
                        outline: 'none'
                    }}
                />
                <button
                    style={{
                        padding: '0 15px',
                        borderRadius: '4px',
                        border: 'none',
                        backgroundColor: '#4caf50',
                        color: '#fff',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                    <FaPaperPlane />
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
