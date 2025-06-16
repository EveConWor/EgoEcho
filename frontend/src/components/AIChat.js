import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';
import toast from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AIChat = () => {
  const navigate = useNavigate();
  const { user, currentMode, trackBehavior } = useApp();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiPersonality, setAiPersonality] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    initializeChat();
    trackBehavior('ai_chat_enter', { mode: currentMode });
  }, [currentMode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = () => {
    const welcomeMessage = currentMode === 'echoverse' 
      ? {
          id: Date.now(),
          type: 'ai',
          content: "Welcome to a space for deep reflection. I'm here to help you explore your inner landscape. What's on your mind today?",
          personality: { empathy: 0.9, wisdom: 0.8 },
          timestamp: new Date()
        }
      : {
          id: Date.now(),
          type: 'ai',
          content: "Ready to push some boundaries? I'm your AI companion for growth and challenge. What are you avoiding that you know you should face?",
          personality: { directness: 0.8, challenge: 0.9 },
          timestamp: new Date()
        };

    setMessages([welcomeMessage]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !user || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/ai/chat?user_id=${user.id}`, {
        message: inputValue,
        mode: currentMode,
        context: {
          conversation_history: messages.slice(-5), // Last 5 messages for context
          personality_state: aiPersonality
        }
      });

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.data.response,
        personality: response.data.personality_traits,
        emotion_tone: response.data.emotion_tone,
        suggestions: response.data.suggestions,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      setAiPersonality(response.data.personality_traits);

      trackBehavior('ai_message_sent', {
        message_length: inputValue.length,
        ai_emotion_tone: response.data.emotion_tone,
        mode: currentMode
      });

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Message failed to send. Try again!');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I'm having trouble connecting right now. Let me try to help anyway - what specific challenge are you facing?",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const MessageBubble = ({ message }) => {
    const isAI = message.type === 'ai';
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex ${isAI ? 'justify-start' : 'justify-end'} mb-4`}
      >
        <div className={`max-w-[80%] ${isAI ? 'mr-12' : 'ml-12'}`}>
          
          {/* Message Content */}
          <div
            className={`p-4 rounded-2xl ${
              isAI
                ? currentMode === 'echoverse'
                  ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30'
                  : 'bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/30'
                : 'bg-white/10 border border-white/20'
            } backdrop-blur-sm`}
          >
            <p className="text-white/90 leading-relaxed">{message.content}</p>
            
            {/* AI Metadata */}
            {isAI && message.emotion_tone && (
              <div className="mt-3 pt-3 border-t border-white/10">
                <div className="flex items-center justify-between text-xs text-white/60">
                  <span>Tone: {message.emotion_tone}</span>
                  <span>{message.timestamp.toLocaleTimeString()}</span>
                </div>
              </div>
            )}
          </div>

          {/* AI Suggestions */}
          {isAI && message.suggestions && message.suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ delay: 0.5 }}
              className="mt-2 flex flex-wrap gap-2"
            >
              {message.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInputValue(suggestion)}
                  className="text-xs px-3 py-1 rounded-full bg-white/10 border border-white/20 text-white/70 hover:bg-white/20 hover:text-white transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </motion.div>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className="min-h-screen flex flex-col text-white">
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-6 border-b ${
          currentMode === 'echoverse'
            ? 'border-purple-500/30 bg-gradient-to-r from-purple-500/10 to-blue-500/10'
            : 'border-red-500/30 bg-gradient-to-r from-red-500/10 to-orange-500/10'
        } backdrop-blur-sm`}
      >
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className={`text-2xl font-bold ${
              currentMode === 'echoverse' ? 'text-gradient' : 'text-gradient-ego'
            }`}>
              {currentMode === 'echoverse' ? '🌌 EchoVerse AI' : '⚡ EgoCore AI'}
            </h1>
            <p className="text-white/70 text-sm">
              {currentMode === 'echoverse' 
                ? 'Your reflective companion for deep exploration'
                : 'Your challenging companion for relentless growth'
              }
            </p>
          </div>
          
          {/* AI Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full animate-pulse ${
                currentMode === 'echoverse' ? 'bg-purple-400' : 'bg-red-400'
              }`} />
              <span className="text-xs text-white/60">AI Active</span>
            </div>
            
            {/* Mode Toggle */}
            <button
              onClick={() => navigate('/')}
              className="btn-secondary text-sm px-4 py-2"
            >
              Switch Mode
            </button>
          </div>
        </div>
      </motion.div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          <AnimatePresence>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </AnimatePresence>
          
          {/* Loading Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start mb-4"
            >
              <div className={`p-4 rounded-2xl ${
                currentMode === 'echoverse'
                  ? 'bg-gradient-to-r from-purple-500/20 to-blue-500/20'
                  : 'bg-gradient-to-r from-red-500/20 to-orange-500/20'
              } backdrop-blur-sm`}>
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    {[...Array(3)].map((_, i) => (
                      <motion.div
                        key={i}
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.2 }}
                        className="w-2 h-2 bg-white/60 rounded-full"
                      />
                    ))}
                  </div>
                  <span className="text-white/60 text-sm">AI is thinking...</span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`p-6 border-t ${
          currentMode === 'echoverse'
            ? 'border-purple-500/30 bg-gradient-to-r from-purple-500/5 to-blue-500/5'
            : 'border-red-500/30 bg-gradient-to-r from-red-500/5 to-orange-500/5'
        } backdrop-blur-sm`}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={currentMode === 'echoverse' 
                  ? "Share your thoughts, reflections, or questions..."
                  : "What challenge are you facing? What growth are you seeking?"
                }
                className="form-input w-full h-20 resize-none"
                disabled={isLoading}
              />
              <div className="flex justify-between items-center mt-2 text-xs text-white/50">
                <span>Press Enter to send, Shift+Enter for new line</span>
                <span>{inputValue.length}/1000</span>
              </div>
            </div>
            
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className={`px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                currentMode === 'echoverse'
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600'
                  : 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600'
              } text-white shadow-lg hover:shadow-xl hover:scale-105`}
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                'Send'
              )}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Navigation */}
      <div className="p-4 text-center border-t border-white/10">
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/')}
            className="btn-secondary text-sm"
          >
            ← Home
          </button>
          <button
            onClick={() => navigate('/profile')}
            className="btn-secondary text-sm"
          >
            View Profile
          </button>
          <button
            onClick={() => navigate(currentMode === 'echoverse' ? '/egocore' : '/echoverse')}
            className="btn-secondary text-sm"
          >
            Switch to {currentMode === 'echoverse' ? 'EgoCore' : 'EchoVerse'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChat;