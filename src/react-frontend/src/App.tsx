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
import AlertNotification from './components/Alert'; 

function App() {
    // const [count, setCount] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [Alert, setAlert] = useState<string | null>(null);

    const clearError = () => {
      setError(null);
    };

    const clearAlert = () => {
        setAlert(null);
    };

    
  
    useEffect(() => {


        const handleCustomError = (event: CustomEvent) => {
            // event.detail contains the details of the error
            const { detail } = event;
          
            let errorMessage = 'An unexpected error occurred';
          
            if (detail && detail.message) {
              errorMessage = detail.message;
            }
            setError(errorMessage);
          };
        

        window.addEventListener('customError', handleCustomError);
        


        const handleCustomAlert = (event: CustomEvent) => {
            // event.detail contains the details of the Alert
            const { detail } = event;
          
            let AlertMessage = 'Alert!';
          
            if (detail && detail.message) {
              AlertMessage = detail.message;
            }
            setAlert(AlertMessage);
          };
        

        window.addEventListener('customAlert', handleCustomAlert);
        

                  // Cleanup: remove the event listeners when the component is unmounted
        return () => {
            window.removeEventListener('customError', handleCustomError);
            window.removeEventListener('customAlert', handleCustomAlert);
        };

    }, []); 
  

    return (
        <BrowserRouter>
        <AlertNotification message={Alert} clearAlert={clearAlert} />
        <ErrorNotification message={error} clearError={clearError} />
            <Routes>
                
                <Route path="/">
                    <Route index element={<Login />} />
                    <Route path="dashboard" element={<Home />} />
                    <Route path="settings" element={<Settings />} />
                    <Route path="listView" element={<ListView />} />
                    <Route path="deviceListView/:networkID/:snapshot" element={<DeviceListView />} />
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
