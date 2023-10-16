// import { useState } from "react";
import "./App.css";
import React, { useState, useEffect } from 'react';

import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Settings from "./pages/Settings";
import NetworkView from "./pages/NetworkView";
import ListView from "./pages/ListView";
import NewNetwork from "./pages/NewNetwork";
import DeviceListView from "./pages/DeviceListView";
import Login from "./pages/LogIn"
import DaemonPage from "./pages/Daemon";
import ErrorNotification from './components/Error'; 

function App() {
    // const [count, setCount] = useState(0);
    const [error, setError] = useState<string | null>(null);

    const clearError = () => {
      setError(null);
    };
  
    useEffect(() => {
      const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
        event.preventDefault(); // Prevents the default browser handling of the rejection
        setError(event.reason?.message || 'An unexpected error occurred');
      };
  
      window.addEventListener('unhandledrejection', handleUnhandledRejection);
      
      // Cleanup: remove the event listener when the component is unmounted
      return () => {
        window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      };
    }, []); // Empty dependency array means this useEffect runs once when component mounts
  

    return (
        <BrowserRouter>
        <ErrorNotification message={error} clearError={clearError} />
            <Routes>
                
                <Route path="/">
                    <Route index element={<Login />} />
                    <Route path="dashboard" element={<Home />} />
                    <Route path="settings" element={<Settings />} />
                    <Route path="listView" element={<ListView />} />
                    <Route path="deviceListView/:networkID" element={<DeviceListView />} />
                    <Route
                        path="networkView/:networkID"
                        element={<NetworkView />}
                    />
                    <Route
                        path="newNetwork/"
                        element={<NewNetwork />}
                    />
                    <Route path="Daemon" element={<DaemonPage />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;
