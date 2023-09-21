import Sidebar from "@/components/sidebar";
import SettingsMenu from "@/components/settingsmenu";
import { Switch } from "@/components/ui/switch"
import { useState, useEffect } from 'react';






const Settings = () => {

    const [ settingsData, setSettingsData ] = useState(
        {"UDP": false, "TCP": false}
    )

    let TCP = settingsData["TCP"];
    let UDP = settingsData["UDP"];

    useEffect(() => {
        fetch("")
            .then((res) => res.json())
            .then((data) => {
                setSettingsData(data);
            })
    }, [TCP, UDP])

    
    return (
        <>
        <div className="flex w-full h-full">
            <Sidebar />
            <SettingsMenu />
        </div>
        </>
    );
};

export default Settings;
