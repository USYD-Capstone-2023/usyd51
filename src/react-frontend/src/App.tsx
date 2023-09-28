// import { useState } from "react";
import "./App.css";

import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Settings from "./pages/Settings";
import NetworkView from "./pages/NetworkView";
import ListView from "./pages/ListView";
import NewNetwork from "./pages/NewNetwork";

function App() {
    // const [count, setCount] = useState(0);

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/">
                    <Route index element={<Home />} />
                    <Route path="settings" element={<Settings />} />
                    <Route path="listView" element={<ListView />} />
                    <Route
                        path="networkView/:networkID"
                        element={<NetworkView />}
                    />
                    <Route
                        path="newNetwork/"
                        element={<NewNetwork />}
                    />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;