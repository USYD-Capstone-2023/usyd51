import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ColumnDef} from "@tanstack/react-table"
import { DataTable } from "./table/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import { ArrowUpDown, MoreHorizontal } from "lucide-react";
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
    { accessorKey: "mac", header: ({ column }) => createSortButton(column, "MAC") },
    { accessorKey: "ip", header: ({ column }) => createSortButton(column, "IP") },
    { accessorKey: "mac_vendor", header: ({ column }) => createSortButton(column, "MAC Vendor") },
    { accessorKey: "os_family", header: ({ column }) => createSortButton(column, "OS Family") },
    { accessorKey: "os_vendor", header: ({ column }) => createSortButton(column, "OS Vendor") },
    { accessorKey: "os_type", header: ({ column }) => createSortButton(column, "OS Type") },
    { accessorKey: "hostname", header: ({ column }) => createSortButton(column, "Hostname") },
    { accessorKey: "parent", header: ({ column }) => createSortButton(column, "Parent") },
    { accessorKey: "ports", header: ({ column }) => createSortButton(column, "Ports") },
]

const createSortButton = (column, label) => (
    <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
        {label}
        <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
);

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
};

export default ListView;
    // return (        

    //     <div className="flex w-full h-full" style={{
    //         height: "95vh",
    //         width: "95%",
    //         marginLeft: "5%",
    //         overflowY: "scroll",
    //         overflowX: "scroll"}}>
    //         <table>
    //             <thead>
    //                 <tr style={{border: "5px solid red"}}>
    //                     <th>MAC</th>
    //                     <th>IP</th>
    //                     <th>MAC Vendor</th>
    //                     <th>OS Family</th>
    //                     <th>OS Vendor</th>
    //                     <th>OS Type</th>
    //                     <th>Hostname</th>
    //                     <th>Parent</th>
    //                     <th>Ports</th>
    //                 </tr>
    //             </thead>
    //             <tbody >
    //                 {networkDevices.map((device, index) => (
    //                     <tr key={index}>
    //                     <td>{device.mac}</td>
    //                     <td>{device.ip}</td>
    //                     <td>{device.mac_vendor}</td>
    //                     <td>{device.os_family}</td>
    //                     <td>{device.os_vendor}</td>
    //                     <td>{device.os_type}</td>
    //                     <td>{device.hostname}</td>
    //                     <td>{device.parent}</td>
    //                     <td>{device.ports}</td>
    //                     </tr>
    //                 ))}
    //             </tbody>
    //     </table>
    //     </div>
    // );