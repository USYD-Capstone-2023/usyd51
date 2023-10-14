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

const createSortableColumn = (accessorKey: keyof Payment, label: string): ColumnDef<Payment> => ({
  accessorKey,
  header: ({ column }) => (
    <Button
      className="shadow-none bg-transparent border-0"
      variant="ghost"
      onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
    >
      {label}
      <ArrowUpDown className="ml-2 h-4 w-4" />
    </Button>
  ),
});


export const columns: ColumnDef<Payment>[] = [
  createSortableColumn("name", "Network Name"),
  createSortableColumn("ssid", "SSID"),
  createSortableColumn("n_alive", "Alive Devices"),
  createSortableColumn("status", "Status"),
  createSortableColumn("lastScanned", "Last Scanned")
];