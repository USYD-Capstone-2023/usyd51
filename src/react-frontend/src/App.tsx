// import { useState } from "react";
import "./App.css";

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";

import Sidebar from "@/components/sidebar";
import Dashboard from "@/components/dashboard";

function App() {
    // const [count, setCount] = useState(0);

    return (
        <div className="flex w-full h-full">
            <Sidebar />
            <Dashboard />
        </div>
    );
}

export default App;
