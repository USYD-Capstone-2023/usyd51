import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ColumnDef} from "@tanstack/react-table"
import { DataTable } from "./table/data-table";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import { ArrowUpDown} from "lucide-react";


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
    [key: string]: string;
}

const columnDisplayNames: { [key: string]: string } = {
    mac: "MAC",
    ip: "IP",
    mac_vendor: "MAC Vendor",
    os_family: "OS Family",
    os_vendor: "OS Vendor",
    os_type: "OS Type",
    hostname: "Hostname",
    parent: "Parent",
    ports: "Ports",
};
function throwCustomError(message: any) {
    const errorEvent = new CustomEvent('customError', {
      detail: {
        message: message
      }
    });
    window.dispatchEvent(errorEvent);
  }

let desc = true;

function customSort(rowA: any, rowB: any, columnId: any): number {

    const valueA = rowA.getValue(columnId);
    const valueB = rowB.getValue(columnId);
    console.log(columnId)

    if (columnId === "ports"){
        const isEmptyA = valueA.length === 0;
        const isEmptyB = valueB.length === 0;
        if (isEmptyA && isEmptyB) return 0;
        
        const a = valueA[0];
        const b = valueB[0];

        if (desc == false){
            valueA.sort((a, b) => b - a);
            valueB.sort((a, b) => b - a);
            if (isEmptyA) return 1;
            if (isEmptyB) return -1;
        }
        else{
            valueA.sort((a, b) => a - b);
            valueB.sort((a, b) => a - b);
            if (isEmptyA) return -1;
            if (isEmptyB) return 1;
        }
        if (a > b) return -1;
        if (a < b) return 1;
    }

    if (desc == false){

        if (valueA === 'unknown') return 1;
        if (valueB === 'unknown') return -1;

        if (typeof valueA === 'string' && typeof valueB === 'string') {
            return valueA.localeCompare(valueB);
        }
    }
    else{

        if (valueA === 'unknown') return -1;
        if (valueB === 'unknown') return 1;

        if (typeof valueA === 'string' && typeof valueB === 'string') {
            return valueA.localeCompare(valueB);
        }
    }
    return 0;
}

const createSortButton = (column, label) => (
    <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => {
            desc = column.getIsSorted() === "asc"
            column.toggleSorting(column.getIsSorted() === "asc")
        }}
    >
        {label}
        <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
);
const columns: ColumnDef<NetworkItem>[] = [
    {
        accessorKey: "mac",
        header: ({ column }) => createSortButton(column, "MAC"),
        sortingFn: customSort
    },
    {
        accessorKey: "ip",
        header: ({ column }) => createSortButton(column, "IP"),
    },
    {
        accessorKey: "mac_vendor",
        header: ({ column }) => createSortButton(column, "MAC Vendor"),
        sortingFn: customSort
    },
    {
        accessorKey: "os_family",
        header: ({ column }) => createSortButton(column, "OS Family"),
        sortingFn: customSort
    },
    {
        accessorKey: "os_vendor",
        header: ({ column }) => createSortButton(column, "OS Vendor"),
        sortingFn: customSort
    },
    {
        accessorKey: "os_type",
        header: ({ column }) => createSortButton(column, "OS Type"),
        sortingFn: customSort
    },
    {
        accessorKey: "hostname",
        header: ({ column }) => createSortButton(column, "Hostname"),
        sortingFn: customSort
    },
    {
        accessorKey: "parent",
        header: ({ column }) => createSortButton(column, "Parent"),
    },
    {
        accessorKey: "ports",
        header: ({ column }) => createSortButton(column, "Ports"),
        sortingFn: customSort
    }
]

const ListView = () => {
    const { networkID } = useParams();
    const [ networkDevices, setNetworkDevices] = useState<NetworkItem[]>([]);
    const [filterKeyword, setFilterKeyword] = useState('');
    const [filterColumn, setFilterColumn] = useState('');
    useEffect(() => {
        const authToken = localStorage.getItem("Auth-Token");
        if (authToken == null) {
            console.log("User is logged out!");
            return;
        }
        const options = {method: "GET", headers: {"Content-Type" : "application/json", "Auth-Token" : authToken, 'Accept': 'application/json'}}
        fetch(databaseUrl + `networks/${networkID}/devices`, options)
        .then((res) => {
            if (!res.ok) {
              throwCustomError(res.status + ":" + res.statusText);
            }
            return res.json();
          })
            .then((data) => {
                if (data["status"] === 200) {
                    setNetworkDevices(data["content"]);
                } else {
                    setNetworkDevices([]);
                    throwCustomError(data["status"] + " " + data["message"]);
                }
            })
            .catch((error) => {
                throwCustomError("Network Error: Something has gone wrong.");
              });
        }, []);

    const filteredDevices = networkDevices.filter(device => 
        String(device[filterColumn]).toLowerCase().includes(filterKeyword.toLowerCase())
    );
    
   return (
    <div className="w-full flex flex-col justify-start items-start h-full gap-3 px-3 text-left">
        <Button style={{display: "flex", marginLeft: "auto"}}>
            <Link to={"../../NetworkView/" + networkID}>Map View</Link>
        </Button>

        <ScrollArea className="h-full w-full rounded-xl">
            <Card className="w-full">
            <CardHeader>
            <div className="flex items-center">
                    <CardTitle className="text-left text-2xl mr-4">List View</CardTitle>
                    <select 
                        onChange={e => setFilterColumn(e.target.value)} 
                        value={filterColumn} 
                        className="mr-2 p-2 border rounded"
                        style={{appearance: 'none'}}
                    >
                        <option value="" disabled>Select Filter Type</option> 
                        {Object.keys(networkDevices[0] ?? {}).map(key => 
                            <option value={key} key={key}>{columnDisplayNames[key as keyof typeof columnDisplayNames] || key}</option>
                        )}
                    </select>
                    <input 
                        type="text" 
                        value={filterKeyword} 
                        onChange={e => setFilterKeyword(e.target.value)} 
                        placeholder="Type to filter"
                        className="p-2 border rounded"
                    />
                </div>
            </CardHeader>
                <CardContent>
                    <DataTable columns={columns} data={filteredDevices} />
                </CardContent>
            </Card>
        </ScrollArea>
    </div>
   )
};

export default ListView;