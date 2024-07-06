import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [parameters, setParameters] = useState(['']);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleParameterChange = (index, value) => {
    const newParameters = [...parameters];
    newParameters[index] = value;
    setParameters(newParameters);
  };

  const handleAddParameter = () => {
    setParameters([...parameters, '']);
  };

  const handleGetAnswer = async () => {
    try {
      const response = await axios.post('http://localhost:5000/get_research_answer', {
        parameters,
        question
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error getting answer:', error);
    }
  };

  return (
    <div className="App">
      <h1>Research Assistant</h1>
      <div className="input-section">
        {parameters.map((param, index) => (
          <div key={index}>
            <input
              type="text"
              placeholder={`Parameter ${index + 1}`}
              value={param}
              onChange={(e) => handleParameterChange(index, e.target.value)}
            />
          </div>
        ))}
        <button onClick={handleAddParameter}>Add Parameter</button>
      </div>
      <div className="input-section">
        <input
          type="text"
          placeholder="Enter your question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={handleGetAnswer}>Get Answer</button>
      </div>
      <div className="answer-section">
        <h2>Answer</h2>
        <div className="answer-content" dangerouslySetInnerHTML={{ __html: answer }} />
      </div>
    </div>
  );
}

export default App;
