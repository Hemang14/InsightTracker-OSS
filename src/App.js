import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ProjectDetail from './components/ProjectDetail';
import { ThemeProvider } from '@mui/material/styles';
import theme from './theme'; // Ensure you have this theme file or define a theme object
import './App.css'; // Ensure your CSS file is imported

function App() {
  return (
    <ThemeProvider theme={theme}>
      <div className="App">
        <Router>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/project/:id" element={<ProjectDetail />} />
          </Routes>
        </Router>
      </div>
    </ThemeProvider>
  );
}

export default App;
