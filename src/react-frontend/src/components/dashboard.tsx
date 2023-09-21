import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import DashboardChart from "./DashboardChart";
import { Link } from "react-router-dom";
import { Heart, Search, Plus, Clock } from "lucide-react"

const CustomCard = (props: any) => {
    const { title, subtitle } = props;
    return (
        <Card className="bg-gray-300 w-full h-full flex justify-center items-center">
            <div className="flex flex-col items-left justify-left w-3/5">
                <CardTitle className="text-gray-500 justify-left text-xl text-left">
                    {title}
                </CardTitle>
                <CardDescription className="text-gray-400 text-left">
                    {subtitle}
                </CardDescription>
            </div>
        </Card>
    );
};

const NetworkButton = (props: any) => {
    const { name, id } = props;
    return <Link to={'/networkView/' + id}>
        <Card className="bg-gray-500 hover:drop-shadow-xl">{name}</Card>
    </Link>
};

const Dashboard = (props: any) => {
    const [networkListData, setNetworkListData] = useState([
        { name: "TestName", id: 0 },
    ]);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/networks")
            .then((res) => res.json())
            .then((data) => {
                let network_list = [];
                for (let network of data) {
                    network_list.push({ name: network.name, id: network.id });
                }

                // for (let i = 0; i < 50; i++) {
                //     network_list.push({ name: "test", id: i });
                // }
                setNetworkListData(network_list);
            });
    }, []);

    return (
        <div className="w-full flex flex-col justify-center items-center h-full gap-10">
            <div className="h-1/6 w-full flex items-center justify-center">
                <div className="w-full h-full flex gap-10 justify-between items-center">
                    <CustomCard title="5/5" subtitle="All Networks Live" />
                    <CustomCard title="178" subtitle="Scans Last Week" />
                    <CustomCard title="190" subtitle="New Devices Found" />
                    <CustomCard title="100%" subtitle="Uptime" />
                </div>
            </div>
            <div className="h-full flex gap-10 w-full">
                <div className="w-1/3  bg-gray-200 opacity-80 rounded-xl">
                    <ScrollArea>
                        <div>
                            <h1 className="text-2xl font-medium leading-none text-gray-500 py-4 px-8">
                                Networks
                                <Separator />
                            </h1>
                            <div className="flex justify-center items-center gap-3 flex-col px-8">
                                {networkListData.map((network, index) => (
                                    <div className="w-full" key={index}>
                                        <NetworkButton name={network.name} id={network.id} />
                                        
                                    </div>
                                ))}
                            </div>
                        </div>
                    </ScrollArea>
                </div>
                <div className="flex flex-col justify-between items-center w-2/3 gap-10 pb-8">
                    <div className="h-full w-full bg-white rounded-xl">
                        <div className="h-1/8 text-gray-400 font-medium text-2xl p-8 text-left">
                            Home Network
                        </div>
                        <div className="flex justify-center items-center h-5/6 w-full p-3">
                            <DashboardChart />
                        </div>
                    </div>
                    <Card
                        onClick={createNewNetwork}
                        className="bg-gray-300 drop-shadow-md hover:drop-shadow-xl"
                    >
                        <Link to="/newNetwork">
                        <CardHeader>
                            <CardTitle>Create New Network</CardTitle>
                        </CardHeader>
                        </Link>
                        
                    </Card>
                </div>
            </div>
        </div>
    );
};

const createNewNetwork = () => {
    console.log("Make a network");
};

export default Dashboard;
