import logo from './logo.svg';
import './App.css';
import React, { useState } from 'react';


function App() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');
    setAnswer('');

    try {
      // In development, the browser calls localhost:3000, but the API is on localhost:8000.
      // We need to configure a proxy. For now, we'll hardcode the URL.
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (e) {
      setError('Failed to fetch the answer. Please check if the backend is running.');
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ask a Question to the RAG Engine</h1>
        <form onSubmit={handleQuery}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question here"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Asking...' : 'Ask'}
          </button>
        </form>

        {answer && (
          <div className="answer-section">
            <h2>Answer:</h2>
            <p>{answer}</p>
          </div>
        )}

        {error && (
          <div className="error-section">
            <p>{error}</p>
          </div>
        )}
      </header>
    </div>
  );
}
export default App;
