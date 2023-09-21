import { Button } from "@/components/ui/button";
import { DarkMode } from "@/components/DarkModeButton";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Link } from "react-router-dom";
import { LayoutDashboard, Network, Cog, BarChart2, LogOut, UserCircle} from "lucide-react"

const Sidebar = (props: any) => {
    return (
        <div className="flex justify-between align-center flex-col w-1/8 bg-gray-200 opacity-75 rounded-xl text-gray-900">
            <div className="flex flex-col justify-start items-center">
                <Link to="/">
                    <Button className="py-10 text-gray-900 shadow-none">
                        <LayoutDashboard></LayoutDashboard>
                    </Button>
                </Link>
                <Link to="/ListView">
                    <Button className="py-10 text-gray-900 shadow-none"><Network></Network></Button>
                </Link>
                <Link to="/Settings">
                    <Button className="py-10 text-gray-900 shadow-none"><Cog></Cog></Button>
                </Link>

                <Button className="py-10 text-gray-900 shadow-none"><BarChart2></BarChart2></Button>
                <DarkMode></DarkMode>
            </div>
            <div className="flex flex-col justify-end items-center py-5">
                <Button className="py-10 text-gray-900 shadow-none"><UserCircle></UserCircle></Button>
                <Button className="py-10 text-gray-900 shadow-none"><LogOut></LogOut></Button>
            </div>
        </div>
    );
};

export default Sidebar;
