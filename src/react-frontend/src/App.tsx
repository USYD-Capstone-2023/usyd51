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
        //setError(event.reason?.message || 'An unexpected error occurred');
        const { reason } = event;

        let errorMessage = 'An unexpected error occurred';
      
        if (reason instanceof Error) {
          console.log(event);
          
          if (reason.message === 'Failed to fetch') {
            if (reason.stack === "TypeError: Failed to fetch\n    at http://localhost:5173/src/components/dashboard.tsx:92:7\n    at HTMLUnknownElement.callCallback2 (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:3674:22)\n    at Object.invokeGuardedCallbackDev (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:3699:24)\n    at invokeGuardedCallback (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:3733:39)\n    at invokeGuardedCallbackAndCatchFirstError (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:3736:33)\n    at executeDispatch (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:7016:11)\n    at processDispatchQueueItemsInOrder (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:7036:15)\n    at processDispatchQueue (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:7045:13)\n    at dispatchEventsForPlugins (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:7053:11)\n    at http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:7177:20"){
                errorMessage = "Failed to connect to the scanning server. Please check your connection and ensure the server is running."
            }
            else if (reason.stack === "TypeError: Failed to fetch\n    at http://localhost:5173/src/components/dashboard.tsx:131:7\n    at commitHookEffectListMount (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:16904:34)\n    at commitPassiveMountOnFiber (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:18152:19)\n    at commitPassiveMountEffects_complete (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:18125:17)\n    at commitPassiveMountEffects_begin (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:18115:15)\n    at commitPassiveMountEffects (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:18105:11)\n    at flushPassiveEffectsImpl (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:19486:11)\n    at flushPassiveEffects (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:19443:22)\n    at performSyncWorkOnRoot (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:18864:11)\n    at flushSyncCallbacks (http://localhost:5173/node_modules/.vite/deps/chunk-GYWC62UC.js?v=65bd87eb:9135:30)"){
                errorMessage = "Failed to connect to the database server. Please check your connection and ensure the server is running."
            }
            else{
                errorMessage = 'Failed to connect to the server. Please check your connection and ensure the server is running.';
            }
          } else {
            errorMessage = reason.message;
          }
          //errorMessage += ` - Stack Trace:\n${reason.stack}`;
        }
        
        setError(errorMessage);
      };
  
      window.addEventListener('unhandledrejection', handleUnhandledRejection);
      
      // Cleanup: remove the event listener when the component is unmounted
      return () => {
        window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      };
    }, []); 
  

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
