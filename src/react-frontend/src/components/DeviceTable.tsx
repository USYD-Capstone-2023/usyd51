import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ColumnDef} from "@tanstack/react-table"
import { DataTable } from "./table/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import ReactFlow, { Panel } from "reactflow";


type NetworkItem = {
    mac: string,
    ip: string,
    mac_vendor: string,
    os_family: string,
    os_vendor: string,
    os_type: string,
    hostname: string,
    parent: string,
    ports: string,
}

const columns: ColumnDef<NetworkItem>[] = [
    {accessorKey: "mac", header: "mac",},
    {accessorKey: "ip", header: "ip",},
    {accessorKey: "mac_vendor", header: "mac_vendor",},
    {accessorKey: "os_family", header: "os_family",},
    {accessorKey: "os_vendor", header: "os_vendor",},
    {accessorKey: "os_type", header: "os_type",},
    {accessorKey: "hostname", header: "hostname",},
    {accessorKey: "parent", header: "parent",},
    {accessorKey: "ports", header: "ports",}
  ]

const ListView = () => {
    const { networkID } = useParams();
    const [ networkDevices, setNetworkDevices] = useState<NetworkItem[]>([]);
    useEffect(() => {
        const authToken = localStorage.getItem("Auth-Token");
        if (authToken == null) {
            console.log("User is logged out!");
            return;
        }
        const options = {method: "GET", headers: {"Content-Type" : "application/json", "Auth-Token" : authToken, 'Accept': 'application/json'}}
        fetch(databaseUrl + `networks/${networkID}/devices`, options)
            .then((res) => (res.json()))
            .then((data) => {
                if (data["status"] === 200) {
                    setNetworkDevices(data["content"]);
                } else {
                    setNetworkDevices([]);
                    console.log(data["status"] + " " + data["message"])
                }
            });
        }, []);
    
   return (
    <div className="w-full flex flex-col justify-start items-start h-full gap-3 px-3 text-left">

        <Button style={{display: "flex", marginLeft: "auto"}}>  <Link to={"../../NetworkView/" + networkID}>Map View </Link></Button>

        <ScrollArea className="h-full w-full rounded-xl">
        <Card className="w-full">
            <CardHeader>
            <CardTitle className="text-left text-2xl">List View</CardTitle>
            </CardHeader>
            <CardContent>
                <DataTable columns={columns} data={networkDevices} />
            </CardContent>
        </Card>
        </ScrollArea>

  </div>

   )







    return (        

        <div className="flex w-full h-full" style={{
            height: "95vh",
            width: "95%",
            marginLeft: "5%",
            overflowY: "scroll",
            overflowX: "scroll"}}>
            <table>
                <thead>
                    <tr style={{border: "5px solid red"}}>
                        <th>MAC</th>
                        <th>IP</th>
                        <th>MAC Vendor</th>
                        <th>OS Family</th>
                        <th>OS Vendor</th>
                        <th>OS Type</th>
                        <th>Hostname</th>
                        <th>Parent</th>
                        <th>Ports</th>
                    </tr>
                </thead>
                <tbody >
                    {networkDevices.map((device, index) => (
                        <tr key={index}>
                        <td>{device.mac}</td>
                        <td>{device.ip}</td>
                        <td>{device.mac_vendor}</td>
                        <td>{device.os_family}</td>
                        <td>{device.os_vendor}</td>
                        <td>{device.os_type}</td>
                        <td>{device.hostname}</td>
                        <td>{device.parent}</td>
                        <td>{device.ports}</td>
                        </tr>
                    ))}
                </tbody>
        </table>
        </div>
    );
};

export default ListView;
