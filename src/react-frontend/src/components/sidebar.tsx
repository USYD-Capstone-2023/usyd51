import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Link } from "react-router-dom";

const Sidebar = (props: any) => {
    return (
        <div className="flex justify-between align-center flex-col w-1/8 bg-gray-200 opacity-75 rounded-xl">
            <div className="flex flex-col justify-start items-center">
                <Link to="/">
                    <Button className="py-10">Home</Button>
                </Link>
                <Link to="/listView">
                    <Button className="py-10">Networks</Button>
                </Link>
                <Link to="/Settings">
                    <Button className="py-10">Settings</Button>
                </Link>

                <Button className="py-10">Analytics</Button>
                <Button className="py-10">Night Mode</Button>
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
