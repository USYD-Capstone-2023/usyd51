import { useEffect, useState } from "react";
import { Payment, columns } from "./columns";
import { DataTable } from "./data-table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { databaseUrl } from "../../servers.tsx";

// Mock async data fetching function
async function fetchData(): Promise<Payment[]> {
  // Simulate an API call or fetch data from your source
  const authToken = localStorage.getItem("Auth-Token");
  if (authToken == null) {
      console.log("User is logged out!");
      return [];
  }
  const options = {method: "GET", headers: {"Content-Type" : "application/json", "Auth-Token" : authToken, 'Accept': 'application/json'}}
  let retval = fetch(databaseUrl + "networks", options)
    .then((res) => res.json())
    .then((data) => {
      let retval = [];
      for (let network of data) {
        let newNetwork = network;
        newNetwork.encrypted = false;
        newNetwork.status = "OFFLINE";
        newNetwork.lastScanned = new Date("1970-1-1");
        newNetwork.devices = 100;
        retval.push(newNetwork);
      }
      return retval;
    })
    .catch(() => []);

  return retval;

  // return [
  //   {
  //     id: "0",
  //     name: "Home Network",
  //     ssid: "NETGEAR86",
  //     devices: 124,
  //     status: "ONLINE",
  //     lastScanned: new Date("2023-09-17"),
  //     encrypted: true,
  //   },
  //   {
  //     id: "1",
  //     name: "Office Downstairs",
  //     ssid: "TPG_4208",
  //     devices: 28,
  //     status: "ONLINE",
  //     lastScanned: new Date("2023-09-17"),
  //     encrypted: true,
  //   },
  //   {
  //     id: "2",
  //     name: "Office Upstairs",
  //     ssid: "TPG_4209",
  //     devices: 192,
  //     status: "INACTIVE",
  //     lastScanned: new Date("2023-09-17"),
  //     encrypted: true,
  //   },
  // ];
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
