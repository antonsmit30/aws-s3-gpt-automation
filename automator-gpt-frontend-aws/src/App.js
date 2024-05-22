import { useState, useEffect } from 'react';
import { BrowserRouter,Routes, Route,Navigate  } from 'react-router-dom'
import ChatComponent from './components/Chat';
import Login from './components/Login';
import userpool from './userpool';


const App = () => {
  useEffect(()=>{
    let user=userpool.getCurrentUser();
      if(user){
        <Navigate to="/chat" replace />
      }
  },[]);
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/chat" element={<ChatComponent />} />
        </Routes>
      </BrowserRouter>

    </div>
  );
}

export default App;