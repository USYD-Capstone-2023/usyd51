import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Link } from "react-router-dom";
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

"use client"

import * as React from "react"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ModeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}


const Sidebar = (props: any) => {
    return (
        <div className="flex justify-between align-center flex-col w-1/8 bg-gray-200 opacity-75 rounded-xl text-gray-900">
            <div className="flex flex-col justify-start items-center">
                <Link to="/">
                    <Button className="py-10 text-gray-900 shadow-none">Home</Button>
                </Link>
                <Link to="/ListView">
                    <Button className="py-10 text-gray-900 shadow-none">Networks</Button>
                </Link>
                <Link to="/Settings">
                    <Button className="py-10 text-gray-900 shadow-none">Settings</Button>
                </Link>

                <Button className="py-10 shadow-none">Analytics</Button>
                <Button className="py-10 shadow-none">Night Mode</Button>
            </div>
            <div className="flex flex-col justify-end items-center py-5">
                <Avatar className="mb-6">
                    {/* choose a better default */}
                    <AvatarImage src="https://github.com/shadcn.png" />
                    <AvatarFallback>LD</AvatarFallback>
                </Avatar>
                <Button className="mb-6">Exit</Button>
            </div>
        </div>
    );
};

export default Sidebar;
