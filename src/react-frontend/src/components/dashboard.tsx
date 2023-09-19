import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";

const Dashboard = (props: any) => {
    const [networkListData, setNetworkListData] = useState([
        { name: "TestName", id: 0 },
    ]);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/network_names")
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
        <div className="w-full flex flex-col justify-center items-center h-full gap-3">
            <div className="h-1/6 w-full flex items-center justify-center">
                <div className="px-1 w-full h-full flex gap-5 justify-between items-center">
                    <Card className="w-full h-full">
                        <CardHeader>
                            <CardTitle>5/5</CardTitle>
                            <CardDescription>All Networks Live</CardDescription>
                        </CardHeader>
                    </Card>
                    <Card className="w-full h-full">
                        <CardHeader>
                            <CardTitle>178</CardTitle>
                            <CardDescription>Scans Last Week</CardDescription>
                        </CardHeader>
                    </Card>
                    <Card className="w-full h-full">
                        <CardHeader>
                            <CardTitle>190</CardTitle>
                            <CardDescription>New Devices Found</CardDescription>
                        </CardHeader>
                    </Card>
                    <Card className="w-full h-full">
                        <CardHeader>
                            <CardTitle>100%</CardTitle>
                            <CardDescription>Uptime</CardDescription>
                        </CardHeader>
                    </Card>
                </div>
            </div>
            <div className="h-full flex gap-3 w-full pa-3 pl-3">
                <div className="w-1/3  bg-gray-400 opacity-80 rounded-xl p-3">
                    <ScrollArea>
                        <div>
                            <h4 className="mb-4 text-sm font-medium leading-none">
                                Networks
                            </h4>
                            {networkListData.map((network, index) => (
                                <>
                                    <Button key={index}>
                                        <div>{network.name}</div>
                                    </Button>
                                    <Separator />
                                </>
                            ))}
                        </div>
                    </ScrollArea>
                </div>
                <div className="flex flex-col justify-between items-center w-2/3 gap-3 pb-8">
                    <div>Insert Graph here</div>
                    <Card
                        onClick={createNewNetwork}
                        className="drop-shadow-md hover:drop-shadow-xl"
                    >
                        <CardHeader>
                            <CardTitle>Create New Network</CardTitle>
                        </CardHeader>
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
