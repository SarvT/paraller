import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import LoginForm from './components/LoginForm'; // renamed from App
import InsightsViewer from './components/InsightsViewer';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm setLoggedIn={setLoggedIn} />} />
        <Route
          path="/insights"
          element={loggedIn ? <InsightsViewer /> : <Navigate to="/" />}
        />
      </Routes>
    </Router>
  );
}

export default App;
