import { useEffect, useState } from "react";
import { Payment, columns } from "./columns";
import { DataTable } from "./data-table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { databaseUrl } from "../../servers.tsx";

async function fetchData(): Promise<Payment[]> {
  const networks = await fetch(databaseUrl + "networks")
    .then(res => res.json())
    .catch(error => {
      console.error("Error fetching networks:", error);
      return [];
    });
  const retval = [];

  for (const network of networks) {
    const devices = await fetch(databaseUrl + `networks/${network.id}/devices`)
      .then(res => res.json())
      .catch(error => {
        console.error("Error fetching devices for network:", network.id, error);
        return [];
      });

    retval.push({
      ...network,
      encrypted: false,
      status: "OFFLINE",
      lastScanned: new Date("1970-1-1"),
      devices: devices.length,
    });
  }
  return retval;
}

export default function Table() {
  const [data, setData] = useState<Payment[]>([]);

  useEffect(() => {
    // Fetch data when the component mounts
    fetchData()
      .then((result) => {
        setData(result);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      });
  }, []);

  // Function to format the date as "dd/mm/yyyy"
  function formatDate(date: Date): string {
    const day = date.getDate().toString().padStart(2, "0");
    const month = (date.getMonth() + 1).toString().padStart(2, "0");
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  }

  return (
    <div className="w-full flex flex-col justify-start items-start h-full gap-3 px-3 text-left">
      <ScrollArea className="h-full w-full rounded-xl">
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-left text-2xl">All Networks</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={data.map((item) => ({
                ...item,
                // Format the date before rendering
                lastScanned: formatDate(item.lastScanned),
              }))}
            />
          </CardContent>
        </Card>
      </ScrollArea>
    </div>
  );
}
