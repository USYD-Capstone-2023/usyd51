"use client";

import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, MoreHorizontal } from "lucide-react"; // Sorting
import { Button } from "@/components/ui/button";

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
  id: string;
  gateway_mac: string;
  name: string;
  ssid: string;
  devices?: number;
  status: "INACTIVE" | "OFFLINE" | "ONLINE" | "ERROR";
  lastScanned?: Date;
  encrypted: boolean;
};

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          className="shadow-none bg-transparent border-0"
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Network Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
  },
  {
    accessorKey: "ssid",
    header: ({ column }) => (
      <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        SSID
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  {
    accessorKey: "n_alive",
    header: ({ column }) => (
      <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Alive Devices
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  {
    accessorKey: "status",
    header: ({ column }) => (
      <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Status
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
  },
  {
    accessorKey: "lastScanned",
    header: ({ column }) => (
      <Button
        className="shadow-none bg-transparent border-0"
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Last Scanned
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    )
  }
];
