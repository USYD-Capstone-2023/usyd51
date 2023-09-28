import { Card, CardDescription, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { cn } from '@/lib/utils';
import { databaseUrl, scannerUrl } from "@/servers";

const user_id = 0;

const SettingsSwitch = (props: any) => {

    return (
    <div className="flex items-center justify-start space-x-2 w-1/3 p-4 m-0">
        <div className="flex flex-col justify-start items-start">
            <Label>{props.switchName}</Label>
            <Label className="text-xs">{props.desc}</Label>
        </div>
        <Switch checked={props.c} onCheckedChange={(state) => {fetch(`${databaseUrl}/setsetting/${props.settingname}/${state}`).then((res) => res.json()).then((data) => props.onc(data[0] === "true"))}}/>
    </div>
    );
}

const SettingsMenu = (props: any) => {

    const [udpSetting, setUDP ] = useState(false);

    useEffect(() => {
        fetch(`${databaseUrl}/setsetting/udp/get`)
            .then((res) => res.json())
            .then((data) => {
                setUDP(data[0] === "true");
            })
    }, [])

    return (
        <div className="w-full flex flex-col justify-start items-start h-full gap-3 px-3">
            <ScrollArea className="h-full w-full rounded-xl">
            <Card className="w-full">
                <CardHeader>
                    <CardTitle className="text-left text-2xl">Settings</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="h-1/6 w-full flex flex-col items-start justify-start space-y-4">
                        <Card className="w-full">
                            <CardHeader>
                                <CardTitle className="text-left">Network Protocols</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex justify-start items-center flex-wrap">
                                    <SettingsSwitch switchName="UDP" desc="Assistive text" settingname="udp" c={udpSetting} onc={setUDP} />
                                    <SettingsSwitch switchName="TCP"/>
                                    <SettingsSwitch switchName="UDP"/>
                                    <SettingsSwitch switchName="UDP"/>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </CardContent>
            </Card>
            </ScrollArea>
        </div>
    );
};
export default SettingsMenu;
