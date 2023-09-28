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
const settings_json = {"user_id" : 0,
"TCP" : false,
"UDP" : false,
"ports" : [],
"run_ports" : false,
"run_os" : false,
"run_hostname" : false,
"run_mac_vendor" : false,
"run_trace" : false,
"run_vertical_trace" : false,
"defaultView" : "Hierarchical",
"defaultNodeColour" : "aaffff",
"defaultEdgeColour" : "ffaaff",
"defaultBackgroundColour" : "ffffaa"}

const SettingsSwitch = (props: any) => {

    return (
    <div className="flex items-center justify-start space-x-2 w-1/3 p-4 m-0">
        <div className="flex flex-col justify-start items-start">
            <Label>{props.switchName}</Label>
            <Label className="text-xs">{props.desc}</Label>
        </div>
        <Switch checked={props.c} onCheckedChange={(state) => {props.onc(state); settings_json[`${props.settingname}`] = state; fetch(`${databaseUrl}/setsettings/${user_id}/set`, {method: 'PUT', mode: 'cors', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(settings_json)})}}/>
    </div>
    );
}

const SettingsMenu = (props: any) => {

    const [udpSetting, setUDP ] = useState(settings_json['UDP']);
    const [tcpSetting, setTCP ] = useState(settings_json["TCP"]);
    const [portscanSetting, setPortScan ] = useState(settings_json["run_ports"]);
    const [osSetting, setOS ] = useState(settings_json["run_os"]);
    const [hostnameSetting, setHostname ] = useState(settings_json["run_hostname"]);
    const [macvendorSetting, setMacVendor ] = useState(settings_json["run_mac_vendor"]);
    const [traceSetting, setTrace ] = useState(settings_json["run_trace"]);
    const [verttraceSetting, setVertTrace ] = useState(settings_json["run_vertical_trace"]);

    useEffect(() => {
        fetch(`${databaseUrl}/getsettings/0`)
            .then((res) => res.json())
            .then((data) => {
                for (let key in data) {
                    settings_json[key] = data[key]
                }
                setUDP(settings_json["UDP"]);
                setTCP(settings_json["TCP"]);
                setPortScan(settings_json["run_ports"]);
                setOS(settings_json["run_os"]);
                setHostname(settings_json["run_hostname"]);
                setMacVendor(settings_json["run_mac_vendor"]);
                setTrace(settings_json["run_trace"]);
                setVertTrace(settings_json["run_vertical_trace"]);

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
                                    <SettingsSwitch switchName="TCP" settingname="TCP" c={tcpSetting} onc={setTCP} />
                                    <SettingsSwitch switchName="UDP" settingname="UDP" c={udpSetting} onc={setUDP} />
                                </div>
                            </CardContent>
                        </Card>
                        <Card className="w-full">
                            <CardHeader>
                                <CardTitle className="text-left">Scans</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex justify-start items-center flex-wrap">
                                    <SettingsSwitch switchName="Port Scan" settingname="run_ports" c={portscanSetting} onc={setPortScan} />
                                    <SettingsSwitch switchName="OS Scan" settingname="run_os" c={osSetting} onc={setOS} />
                                    <SettingsSwitch switchName="Hostname Scan" settingname="run_hostname" c={hostnameSetting} onc={setHostname} />
                                    <SettingsSwitch switchName="MAC Vendor Scan" settingname="run_mac_vendor" c={macvendorSetting} onc={setMacVendor} />
                                    <SettingsSwitch switchName="Traceroute" settingname="run_trace" c={traceSetting} onc={setTrace} />
                                    <SettingsSwitch switchName="Vertical Traceroute" settingname="run_vertical_trace" c={verttraceSetting} onc={setVertTrace} />
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
