"use client"

import {
  Card,
  CardDescription,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { X, ChevronsUpDown } from "lucide-react";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
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
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

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

  // SCAN SETTINGS
  const [udpSetting, setUDP] = useState(settings_json["UDP"]);
  const [tcpSetting, setTCP] = useState(settings_json["TCP"]);
  const [portsSetting, setPorts] = useState([]);
  const [osSetting, setOS] = useState(settings_json["run_os"]);
  const [hostnameSetting, setHostname] = useState(
    settings_json["run_hostname"]
  );
  const [macvendorSetting, setMacVendor] = useState(
    settings_json["run_mac_vendor"]
  );
  const [verttraceSetting, setVertTrace] = useState(
    settings_json["run_vertical_trace"]
  );
  const [defaultviewSetting, setDefaultView] = useState(
    settings_json["defaultView"]
  );

  // DAEMON SETTINGS
  const [d_scanrateSetting, setdScanrate] = useState(settings_json["daemon_scan_rate"]);
  const [d_udpSetting, setdUDP] = useState(settings_json["daemon_UDP"]);
  const [d_tcpSetting, setdTCP] = useState(settings_json["daemon_TCP"]);
  const [d_portsSetting, setdPorts] = useState(settings_json["daemon_ports"]);
  const [d_osSetting, setdOS] = useState(settings_json["daemon_run_os"]);
  const [d_hostnameSetting, setdHostname] = useState(
    settings_json["daemon_run_hostname"]
  );
  const [d_macvendorSetting, setdMacVendor] = useState(
    settings_json["daemon_run_mac_vendor"]
  );
  const [d_verttraceSetting, setdVertTrace] = useState(
    settings_json["daemon_run_vertical_trace"]
  );

  const [ scanIP, setScanIP ] = useState(settings_json["scan_server_ip"]);

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
          setOS(data["content"]["run_os"]);
          setHostname(data["content"]["run_hostname"]);
          setMacVendor(data["content"]["run_mac_vendor"]);
          setVertTrace(data["content"]["run_vertical_trace"]);
          setPorts(data["content"]["ports"]);

          setdScanrate(data["content"]["daemon_scan_rate"]);
          setdUDP(data["content"]["daemon_UDP"]);
          setdTCP(data["content"]["daemon_TCP"]);
          setdOS(data["content"]["daemon_run_os"]);
          setdHostname(data["content"]["daemon_run_hostname"]);
          setdMacVendor(data["content"]["daemon_run_mac_vendor"]);
          setdVertTrace(data["content"]["daemon_run_vertical_trace"]);
          setdPorts(data["content"]["daemon_ports"]);

          setScanIP(data["content"]["scan_server_ip"]);
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
      <ScrollArea className={cn("h-full w-full rounded-xl")}>
        <Card className={cn("w-full")}>
          <CardHeader>
            <CardTitle className={cn("text-left text-2xl")}>Settings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-1/6 w-full flex flex-col items-start justify-start space-y-4">
              <Card className={cn("w-full")}>
                <CardHeader>
                  <CardTitle className={cn("text-left")}>Scan Settings</CardTitle>
                </CardHeader>
                <CardContent>
                
                  <Card>
                    <CardHeader>
                      <CardTitle className={cn("text-left")}>Port Scanning</CardTitle>
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
                      <Popover>
                        <PopoverTrigger asChild className={cn("w-1/3")}><Button className={cn("justify-between")} variant="outline">{"Ports: " + portsSetting.join(', ')}<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0" /></Button></PopoverTrigger>
                        <PopoverContent>
                          <div className="flex flex-col justify-start space-y-1">
                          {portsSetting.map((port) => (
                            <Button key={port} className={cn("justify-between w-full")} variant="outline"
                            onClick={() => {

                              settings_json["ports"].splice(settings_json["ports"].indexOf(port), 1);
                              setPorts([...settings_json["ports"]]);


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

                              fetch(`${databaseUrl}settings/set`, options).then((res) =>
                                res.json().then((data) => {
                                  if (data["status"] != 200) {
                                    console.log(data["status"] + " " + data["message"]);
                                  }
                                })
                              );

                            }}>
                              {port}
                              <X />
                            </Button>
                            ))}

                            <div className="flex w-full max-w-sm items-center space-x-2">
                              <Input id="newport" type="email" placeholder="Enter port #..." />
                              <Button variant="outline" onClick={() => {

                                let val = parseInt(document.getElementById("newport").value);
                                if (Number.isInteger(val)) {
                                  if(val >= 0 && val <= 65535) {
                                    settings_json["ports"].push(val);
                                    setPorts([...settings_json["ports"]]);
                                    document.getElementById("newport").value = '';

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
      
                                    fetch(`${databaseUrl}settings/set`, options).then((res) =>
                                      res.json().then((data) => {
                                        if (data["status"] != 200) {
                                          console.log(data["status"] + " " + data["message"]);
                                        }
                                      })
                                    );
                                    
                                  } else {
                                    throwCustomError("Enter a port between 0 and 65535");
                                  }
                                } else {
                                  throwCustomError("Enter an integer");
                                }
                              }}
                              >
                                Add
                              </Button>
                            </div>

                          </div>
                        </PopoverContent>
                      </Popover>


                      
                    </div>
                    </CardContent>
                  </Card>
                <div className="flex justify-start items-center flex-wrap">
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
                      switchName="Vertical Traceroute"
                      settingname="run_vertical_trace"
                      c={verttraceSetting}
                      onc={setVertTrace}
                    />

                  </div>             
                </CardContent>
              </Card>

              <Card className={cn("w-full")}>
                <CardHeader>
                  <CardTitle className={cn("text-left")}>Daemon Settings</CardTitle>
                </CardHeader>
                <CardContent>
                
                  <Card>
                    <CardHeader>
                      <CardTitle className={cn("text-left")}>Port Scanning</CardTitle>
                    </CardHeader>
                    <CardContent>
                    <div className="flex justify-start items-center flex-wrap">
                      <SettingsSwitch
                        switchName="TCP"
                        settingname="TCP"
                        c={d_tcpSetting}
                        onc={setdTCP}
                      />
                      <SettingsSwitch
                        switchName="UDP"
                        settingname="UDP"
                        c={d_udpSetting}
                        onc={setdUDP}
                      />
                      <Popover>
                        <PopoverTrigger asChild className={cn("w-1/3")}><Button className={cn("justify-between")} variant="outline">{"Ports: " + d_portsSetting.join(', ')}<ChevronsUpDown className="ml-2 h-4 w-4 shrink-0" /></Button></PopoverTrigger>
                        <PopoverContent>
                          <div className="flex flex-col justify-start space-y-1">
                          {d_portsSetting.map((port) => (
                            <Button key={port} className={cn("justify-between w-full")} variant="outline"
                            onClick={() => {

                              settings_json["daemon_ports"].splice(settings_json["daemon_ports"].indexOf(port), 1);
                              setPorts([...settings_json["daemon_ports"]]);


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

                              fetch(`${databaseUrl}settings/set`, options).then((res) =>
                                res.json().then((data) => {
                                  if (data["status"] != 200) {
                                    console.log(data["status"] + " " + data["message"]);
                                  }
                                })
                              );

                            }}>
                              {port}
                              <X />
                            </Button>
                            ))}

                            <div className="flex w-full max-w-sm items-center space-x-2">
                              <Input id="daemon_newport" type="email" placeholder="Enter port #..." />
                              <Button variant="outline" onClick={() => {

                                let val = parseInt(document.getElementById("daemon_newport").value);
                                if (Number.isInteger(val)) {
                                  if(val >= 0 && val <= 65535) {
                                    settings_json["daemon_ports"].push(val);
                                    setdPorts([...settings_json["daemon_ports"]]);
                                    document.getElementById("daemon_newport").value = '';

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
      
                                    fetch(`${databaseUrl}settings/set`, options).then((res) =>
                                      res.json().then((data) => {
                                        if (data["status"] != 200) {
                                          console.log(data["status"] + " " + data["message"]);
                                        }
                                      })
                                    );
                                    
                                  } else {
                                    throwCustomError("Enter a port between 0 and 65535");
                                  }
                                } else {
                                  throwCustomError("Enter an integer");
                                }
                              }}
                              >
                                Add
                              </Button>
                            </div>

                          </div>
                        </PopoverContent>
                      </Popover>


                      
                    </div>
                    </CardContent>
                  </Card>
                <div className="flex justify-start items-center flex-wrap">
                  <SettingsSwitch
                      switchName="OS Scan"
                      settingname="run_os"
                      c={d_osSetting}
                      onc={setdOS}
                    />
                    <SettingsSwitch
                      switchName="Hostname Scan"
                      settingname="run_hostname"
                      c={d_hostnameSetting}
                      onc={setdHostname}
                    />
                    <SettingsSwitch
                      switchName="MAC Vendor Scan"
                      settingname="run_mac_vendor"
                      c={d_macvendorSetting}
                      onc={setdMacVendor}
                    />
                    <SettingsSwitch
                      switchName="Vertical Traceroute"
                      settingname="run_vertical_trace"
                      c={d_verttraceSetting}
                      onc={setdVertTrace}
                    />

                    <div className="flex items-center justify-start space-x-2 w-1/3 p-4 m-0">
                      <Label>Scan Interval</Label>
                      
                      <Input className={cn("w-1/3 text-right")} value={d_scanrateSetting} onChange={(e) => {
                        if (Number.isInteger(parseInt(e.target.value))) {
                          setdScanrate(parseInt(e.target.value));
                          settings_json["daemon_scan_rate"] = parseInt(e.target.value);
                        }
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

                          fetch(`${databaseUrl}settings/set`, options).then((res) =>
                            res.json().then((data) => {
                              if (data["status"] != 200) {
                                console.log(data["status"] + " " + data["message"]);
                              }
                            })
                          );

                        }
                      }
                      />
                      <Label>secs</Label>
                    </div>

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
                        value={defaultviewSetting}
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
                          <SelectItem value="Cluster">
                            Cluster
                          </SelectItem>
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
