import React, { useEffect, useState } from "react";
import { Payment, columns } from "./columns";
import { DataTable } from "./data-table";

// Mock async data fetching function
async function fetchData(): Promise<Payment[]> {
  // Simulate an API call or fetch data from your source
  return [
    {
      id: "0",
      networkName: "Home Network",
      ssid: "NETGEAR86",
      devices: 124,
      status: "ONLINE",
      lastScanned: new Date("2023-09-17"),
      encrypted: true,
    },
    {
      id: "1",
      networkName: "Office Downstairs",
      ssid: "TPG_4208",
      devices: 28,
      status: "ONLINE",
      lastScanned: new Date("2023-09-17"),
      encrypted: true,
    },
    {
      id: "2",
      networkName: "Office Upstairs",
      ssid: "TPG_4209",
      devices: 192,
      status: "INACTIVE",
      lastScanned: new Date("2023-09-17"),
      encrypted: true,
    },
  ];
}

export default function DemoPage() {
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
    <div className="container mx-auto py-10">
      <DataTable 
        columns={columns} 
        data={data.map((item) => ({
          ...item,
          // Format the date before rendering
          lastScanned: formatDate(item.lastScanned),
        }))} />
    </div>
  );
}
