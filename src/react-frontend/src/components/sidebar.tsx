import { Button } from "@/components/ui/button";
import { DarkMode } from "@/components/DarkModeButton";
import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  Network,
  Cog,
  BarChart2,
  LogOut,
  UserCircle,
} from "lucide-react";

const Sidebar = (props: any) => {
  return (
    <div className="flex justify-between align-center flex-col w-1/8 bg-gray-200 opacity-75 rounded-xl text-gray-900 overflow-hidden">
      <div className="flex flex-col justify-start items-center">
        <Link to="/dashboard">
          <Button className="py-10 text-gray-900 shadow-none">
            <LayoutDashboard></LayoutDashboard>
          </Button>
        </Link>
        <Link to="/ListView">
          <Button className="py-10 text-gray-900 shadow-none">
            <Network></Network>
          </Button>
        </Link>
        <Link to="/Daemon">
          <Button className="py-10 text-gray-900 shadow-none">
            <BarChart2></BarChart2>
          </Button>
        </Link>
        <DarkMode></DarkMode>
      </div>
      <div className="flex flex-col justify-end items-center">
        <Link to="/Settings">
          <Button className="py-10 text-gray-900 shadow-none">
            <Cog></Cog>
          </Button>
        </Link>
        <Link to="/">
          <Button className="py-10 text-gray-900 shadow-none">
            <LogOut></LogOut>
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default Sidebar;
