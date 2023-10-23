import {
  Card,
  CardDescription,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { databaseUrl, scannerUrl } from "@/servers";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Filled on load, dont put default values here, they are already set in the db so in the event it
// fails to retrieve the data and resorts to defaults, itll fill the settings with incorrect data
let settings_json = {};

function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  window.dispatchEvent(errorEvent);
}


const SettingsSwitch = (props: any) => {
  return (
    <div className="flex items-center justify-start space-x-2 w-1/3 p-4 m-0">
      <div className="flex flex-col justify-start items-start">
        <Label>{props.switchName}</Label>
        <Label className="text-xs">{props.desc}</Label>
      </div>
      <Switch
        checked={props.c}
        onCheckedChange={(state) => {
          props.onc(state);
          settings_json[`${props.settingname}`] = state;
          const authToken = localStorage.getItem("Auth-Token");
          if (authToken == null) {
            console.log("User is logged out!");
            return;
          }

          const options = {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              "Auth-Token": authToken,
              "Accept" : "application/json",
            },
            body: JSON.stringify(settings_json),
          };
          fetch(`${databaseUrl}settings/set`, options)
          .then((res) => {
            if (!res.ok) {
              throwCustomError(res.status + ":" + res.statusText);
            }
            return res.json();
          })
          .then((data) => {
              if (data["status"] != 200) {
                throwCustomError(data["status"] + " " + data["message"]);
              }
            })
            .catch((error) => {
              throwCustomError("Network Error: Something has gone wrong.");
            });
        }}
      />
    </div>
  );
};

const SettingsMenu = (props: any) => {
  // Retrieves stored settings from database
  useEffect(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      console.log("User is logged out! System is gonna break here");
    } else {
      const options = {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Auth-Token": authToken,
          "Accept" : "application/json",
        },
      };
      fetch(`${databaseUrl}settings`, options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
        .then((data) => {
          if (data["status"] === 200) {
            settings_json = data["content"];
          } else {
            throwCustomError(data["status"] + " " + data["message"]);
            console.log(
              "System will break here, need to figure out what to do if database goes offline or errors"
            );
          }
        })
        .catch((error) => {
          throwCustomError("Network Error: Something has gone wrong.");
        });
    }
  }, []);

  const [udpSetting, setUDP] = useState(settings_json["UDP"]);
  const [tcpSetting, setTCP] = useState(settings_json["TCP"]);
  const [portscanSetting, setPortScan] = useState(settings_json["run_ports"]);
  const [portsSetting, setPorts] = useState(settings_json["ports"]);
  const [osSetting, setOS] = useState(settings_json["run_os"]);
  const [hostnameSetting, setHostname] = useState(
    settings_json["run_hostname"]
  );
  const [macvendorSetting, setMacVendor] = useState(
    settings_json["run_mac_vendor"]
  );
  const [traceSetting, setTrace] = useState(settings_json["run_trace"]);
  const [verttraceSetting, setVertTrace] = useState(
    settings_json["run_vertical_trace"]
  );
  const [defaultviewSetting, setDefaultView] = useState(
    settings_json["defaultView"]
  );

  useEffect(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      console.log("User is logged out!");
      return;
    }

    const options = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept" : "application/json",
      },
    };
    fetch(`${databaseUrl}settings`, options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data["status"] === 200) {
          setUDP(data["content"]["UDP"]);
          setTCP(data["content"]["TCP"]);
          setPortScan(data["content"]["run_ports"]);
          setOS(data["content"]["run_os"]);
          setHostname(data["content"]["run_hostname"]);
          setMacVendor(data["content"]["run_mac_vendor"]);
          setTrace(data["content"]["run_trace"]);
          setVertTrace(data["content"]["run_vertical_trace"]);
          setPorts(data["content"]["ports"]);
        } else {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  }, []);

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
                    <SettingsSwitch
                      switchName="TCP"
                      settingname="TCP"
                      c={tcpSetting}
                      onc={setTCP}
                    />
                    <SettingsSwitch
                      switchName="UDP"
                      settingname="UDP"
                      c={udpSetting}
                      onc={setUDP}
                    />
                  </div>
                </CardContent>
              </Card>
              <Card className="w-full">
                <CardHeader>
                  <CardTitle className="text-left">Scans</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-start items-center flex-wrap">
                    <SettingsSwitch
                      switchName="Port Scan"
                      settingname="run_ports"
                      c={portscanSetting}
                      onc={setPortScan}
                    />
                    <SettingsSwitch
                      switchName="OS Scan"
                      settingname="run_os"
                      c={osSetting}
                      onc={setOS}
                    />
                    <SettingsSwitch
                      switchName="Hostname Scan"
                      settingname="run_hostname"
                      c={hostnameSetting}
                      onc={setHostname}
                    />
                    <SettingsSwitch
                      switchName="MAC Vendor Scan"
                      settingname="run_mac_vendor"
                      c={macvendorSetting}
                      onc={setMacVendor}
                    />
                    <SettingsSwitch
                      switchName="Traceroute"
                      settingname="run_trace"
                      c={traceSetting}
                      onc={setTrace}
                    />
                    <SettingsSwitch
                      switchName="Vertical Traceroute"
                      settingname="run_vertical_trace"
                      c={verttraceSetting}
                      onc={setVertTrace}
                    />
                  </div>
                </CardContent>
              </Card>
              <Card className="w-full">
                <CardHeader>
                  <CardTitle className="text-left">View</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-start items-center flex-wrap">
                    <div className="flex flex-col items-baseline justify-start space-y-2 w-1/3 p-4 m-0">
                      <Label>Default View</Label>
                      <Select
                        defaultValue={defaultviewSetting}
                        onValueChange={(value) => {
                          const authToken = localStorage.getItem("Auth-Token");
                          if (authToken == null) {
                            console.log("User is logged out!");
                            return;
                          }

                          setDefaultView(value);
                          settings_json["defaultView"] = value;
                          const options = {
                            method: "PUT",
                            headers: {
                              "Content-Type": "application/json",
                              "Auth-Token": authToken,
                              "Accept" : "application/json",
                            },
                            body: JSON.stringify(settings_json),
                          };
                          fetch(`${databaseUrl}settings/set`, options).catch((error) => {
                            throwCustomError("Network Error: Something has gone wrong.");
                          });
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder={defaultviewSetting} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Hierarchical">
                            Hierarchical
                          </SelectItem>
                          <SelectItem value="Cluster">Cluster</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
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
