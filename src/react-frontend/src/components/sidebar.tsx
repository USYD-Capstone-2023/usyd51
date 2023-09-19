import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Link } from "react-router-dom";

const Sidebar = (props: any) => {
    return (
        <div className="flex justify-between items-center flex-col w-1/8 bg-gray-500 opacity-75 rounded-xl">
            <div className="flex flex-col justify-start items-center">
                <Link to="/">
                    <Button>Home</Button>
                </Link>
                <Link to="/listView">
                    <Button>Networks</Button>
                </Link>
                <Link to="/Settings">
                    <Button>Settings</Button>
                </Link>

                <Button>Analytics</Button>
                <Button>Night Mode</Button>
            </div>
            <div className="flex flex-col justify-end items-center py-5">
                <Avatar>
                    {/* choose a better default */}
                    <AvatarImage src="https://github.com/shadcn.png" />
                    <AvatarFallback>LD</AvatarFallback>
                </Avatar>
                <Button>Exit</Button>
            </div>
        </div>
    );
};

export default Sidebar;
