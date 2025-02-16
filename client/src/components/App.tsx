import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import React from 'react'

import ProjectList from './Projects/list'
import ProjectShow from './Projects/show'
import PaperShow from './Papers/show'

const App: React.FC = () => {
  return (
    <div className="container">
      <div style={ { marginBottom: '20px' } }></div>
      <nav>
        <a href='/'>Home</a>
      </nav>
      <Router>
        <Routes>
          <Route path="/" element={<ProjectList />} />
          <Route path="/projects/show/:name" element={<ProjectShow />} />
          <Route path="/papers/show/:id" element={<PaperShow />} />
        </Routes>
      </Router>
    </div>
  );
};

export default App