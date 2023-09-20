"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, MoreHorizontal } from "lucide-react" // Sorting
import { Button } from "@/components/ui/button";

// This type is used to define the shape of our data.
// You can use a Zod schema here if you want.
export type Payment = {
  id: string
  networkName: string
  ssid: string
  devices: number
  status: "INACTIVE" | "OFFLINE" | "ONLINE" | "ERROR"
  lastScanned: Date
  encrypted: boolean
}

export const columns: ColumnDef<Payment>[] = [
  {
    accessorKey: "networkName",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Network Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      )
    },
  },
  {
    accessorKey: "ssid",
    header: "SSID",
  },
  {
    accessorKey: "devices",
    header: "Devices",
  },
  {
    accessorKey: "status",
    header: "Status",
  },
  {
    accessorKey: "lastScanned",
    header: "Last Scanned",
  },
  {
    accessorKey: "encrypted",
    header: "Encrypted",
  },
]
