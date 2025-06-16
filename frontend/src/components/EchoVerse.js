import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../App';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const journeySteps = [
  {
    id: 'essence',
    title: 'Essence',
    icon: '🔮',
    description: 'Discover your core identity and authentic self',
    questions: [
      'What makes you uniquely you?',
      'When do you feel most authentic?',
      'What values guide your decisions?',
      'How do you want to be remembered?'
    ]
  },
  {
    id: 'mindscape',
    title: 'Mindscape',
    icon: '🧠',
    description: 'Explore your thoughts, beliefs, and mental patterns',
    questions: [
      'What patterns do you notice in your thinking?',
      'What beliefs shape your worldview?',
      'How do you process complex emotions?',
      'What mental models guide you?'
    ]
  },
  {
    id: 'aesthetic',
    title: 'Aesthetic',
    icon: '🎨',
    description: 'Define your visual identity and style preferences',
    questions: [
      'What colors represent your energy?',
      'What visual styles resonate with you?',
      'How do you express creativity?',
      'What environments inspire you?'
    ]
  },
  {
    id: 'narrative',
    title: 'Narrative',
    icon: '📜',
    description: 'Create your personal story and manifesto',
    questions: [
      'What is your origin story?',
      'What challenges have shaped you?',
      'What is your mission in life?',
      'How do you want your story to unfold?'
    ]
  }
];

const EchoVerse = () => {
  const navigate = useNavigate();
  const { user, updateUserJourney, trackBehavior } = useApp();
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState({});
  const [personalizedPrompt, setPersonalizedPrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    trackBehavior('echoverse_enter', { timestamp: new Date().toISOString() });
    fetchPersonalizedPrompt();
  }, []);

  const fetchPersonalizedPrompt = async () => {
    if (!user) return;
    try {
      const response = await axios.get(`${API}/journey/${user.id}/prompts`, {
        params: { mode: 'echoverse' }
      });
      setPersonalizedPrompt(response.data.prompt);
    } catch (error) {
      console.error('Error fetching prompt:', error);
    }
  };

  const handleResponseChange = (questionIndex, value) => {
    const stepId = journeySteps[currentStep].id;
    setResponses(prev => ({
      ...prev,
      [stepId]: {
        ...prev[stepId],
        [questionIndex]: value
      }
    }));
  };

  const handleStepComplete = async () => {
    if (!user) return;
    
    setIsSubmitting(true);
    try {
      const stepId = journeySteps[currentStep].id;
      const stepResponses = responses[stepId] || {};
      
      await updateUserJourney(stepId, stepResponses);
      
      if (currentStep < journeySteps.length - 1) {
        setCurrentStep(currentStep + 1);
        fetchPersonalizedPrompt();
      } else {
        // Journey complete
        trackBehavior('echoverse_complete', { 
          completion_time: new Date().toISOString(),
          all_responses: responses
        });
        navigate('/profile');
      }
    } catch (error) {
      console.error('Error saving step:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentStepData = journeySteps[currentStep];
  const currentStepResponses = responses[currentStepData.id] || {};
  const isStepComplete = Object.keys(currentStepResponses).length >= currentStepData.questions.length;

  return (
    <div className="min-h-screen flex flex-col justify-center items-center text-white p-6">
      
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl md:text-6xl font-bold text-gradient mb-4">
          🌌 EchoVerse
        </h1>
        <p className="text-white/70 text-lg">
          Journey through the depths of your identity
        </p>
      </motion.div>

      {/* Progress Bar */}
      <motion.div
        initial={{ opacity: 0, scaleX: 0 }}
        animate={{ opacity: 1, scaleX: 1 }}
        className="w-full max-w-2xl mb-8"
      >
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm text-white/60">Progress</span>
          <span className="text-sm text-white/60">
            {currentStep + 1} of {journeySteps.length}
          </span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
            animate={{ width: `${((currentStep + 1) / journeySteps.length) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </motion.div>

      {/* Step Navigation */}
      <div className="flex items-center justify-center space-x-4 mb-8">
        {journeySteps.map((step, index) => (
          <motion.div
            key={step.id}
            className={`flex items-center justify-center w-12 h-12 rounded-full text-xl transition-all ${
              index === currentStep
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white scale-110'
                : index < currentStep
                ? 'bg-green-500 text-white'
                : 'bg-white/10 text-white/50'
            }`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {step.icon}
          </motion.div>
        ))}
      </div>

      {/* Current Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ duration: 0.5 }}
          className="card max-w-2xl w-full"
        >
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">{currentStepData.icon}</div>
            <h2 className="text-3xl font-bold text-gradient mb-2">
              {currentStepData.title}
            </h2>
            <p className="text-white/70">
              {currentStepData.description}
            </p>
          </div>

          {/* Personalized Prompt */}
          {personalizedPrompt && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-lg p-4 mb-6 border border-purple-500/30"
            >
              <div className="text-sm text-purple-300 mb-2">✨ Personalized Reflection</div>
              <p className="text-white/90 italic">{personalizedPrompt}</p>
            </motion.div>
          )}

          {/* Questions */}
          <div className="space-y-6">
            {currentStepData.questions.map((question, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="space-y-2"
              >
                <label className="block text-white/90 font-medium">
                  {question}
                </label>
                <textarea
                  value={currentStepResponses[index] || ''}
                  onChange={(e) => handleResponseChange(index, e.target.value)}
                  className="form-input w-full h-24 resize-none"
                  placeholder="Share your thoughts..."
                />
              </motion.div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex justify-between items-center mt-8">
            <button
              onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
              disabled={currentStep === 0}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <div className="text-center">
              <div className="text-sm text-white/60 mb-1">
                {Object.keys(currentStepResponses).length} of {currentStepData.questions.length} answered
              </div>
              <div className="w-32 bg-white/10 rounded-full h-1">
                <div 
                  className="bg-purple-500 h-1 rounded-full transition-all"
                  style={{ 
                    width: `${(Object.keys(currentStepResponses).length / currentStepData.questions.length) * 100}%` 
                  }}
                />
              </div>
            </div>

            <button
              onClick={handleStepComplete}
              disabled={!isStepComplete || isSubmitting}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </div>
              ) : currentStep === journeySteps.length - 1 ? (
                'Complete Journey'
              ) : (
                'Next Step'
              )}
            </button>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-8 flex space-x-4"
      >
        <button
          onClick={() => navigate('/')}
          className="btn-secondary"
        >
          ← Home
        </button>
        <button
          onClick={() => navigate('/chat')}
          className="btn-secondary"
        >
          Chat with AI
        </button>
      </motion.div>
    </div>
  );
};

export default EchoVerse;