import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LoginForm({ setLoggedIn }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [mode, setMode] = useState('register');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = mode === 'register' ? 'http://localhost:8000/register' : 'http://localhost:8000/login';

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.detail || 'Something went wrong');

      setMessage(data.message);
      setLoggedIn(true);
      navigate('/insights');
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">
          {mode === 'register' ? 'Register' : 'Login'}
        </h1>
  
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <input
              name="name"
              placeholder="Name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}
          <input
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            name="password"
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition"
          >
            {mode === 'register' ? 'Register' : 'Login'}
          </button>
        </form>
  
        <button
          onClick={() => setMode(mode === 'register' ? 'login' : 'register')}
          className="mt-4 text-blue-600 hover:underline text-sm"
        >
          Switch to {mode === 'register' ? 'Login' : 'Register'}
        </button>
  
        {message && (
          <p className="mt-4 text-sm text-green-600 text-center">{message}</p>
        )}
      </div>
    </div>
  );
  
}

export default LoginForm;
