import { useEffect, useState } from "react";
import { Payment, columns } from "./columns";
import { DataTable } from "./data-table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { databaseUrl } from "../../servers.tsx";

function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  window.dispatchEvent(errorEvent);
}

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
  .catch((error) => {
    throwCustomError("Network Error: Something has gone wrong.");
  })
  .then((res) => {
    if (!res.ok) {
      throwCustomError(res.status + ":" + res.statusText);
    }
    return res.json();
  })
    .then((data) => {

      if (data["status"] === 200) {
        let retval = [];
        for (let network of data["content"]) {
          let newNetwork = network;
          newNetwork.encrypted = false;
          newNetwork.status = "OFFLINE";
          newNetwork.lastScanned = new Date(newNetwork.timestamp * 1000).toLocaleString();
          retval.push(newNetwork);
        }
        return retval;

      } else {
        return [];
      }
    });
  
  return retval;
}
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


export default function Table() {
  const [data, setData] = useState<Payment[]>([]);

  useEffect(() => {
    // Fetch data when the component mounts
    fetchData()
      .then((result) => {
        setData(result);
      })
      .catch((error) => {
        throwCustomError("Error fetching data:", error);
      });
  }, []);

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
              data={data.map((item) => ({...item}))}
            />
          </CardContent>
        </Card>
      </ScrollArea>
    </div>
  );
}
