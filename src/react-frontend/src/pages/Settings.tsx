import Sidebar from "@/components/sidebar";
import SettingsMenu from "@/components/settingsmenu";
import { Switch } from "@/components/ui/switch"
import { useState, useEffect } from 'react';
import { databaseUrl, scannerUrl } from "@/servers";

const Settings = () => {

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
