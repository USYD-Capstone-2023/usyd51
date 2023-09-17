import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useEffect, useState } from "react";

const Dashboard = (props: any) => {
    const [networkListData, updateNetworkListData] = useState([
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
                networkListData = network_list;
            });
    }, []);

    let network_list: String[] = [];
    let network_ids: String[] = [];

    fetch("http://127.0.0.1:5000/network_names")
        .then((res) => res.json())
        .then((data) => {
            console.log(data);
            for (let network of data) {
                network_list.push(network.name);
                network_ids.push(network.id);
            }
        });

    return (
        <div className="w-full flex flex-col justify-center items-center h-full gap-3">
            <div className="h-1/6">
                <div className="px-1 flex gap-5 justify-between items-center">
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
            <div className="h-full flex gap-3 ">
                <div>
                    <ScrollArea>
                        <div>
                            <h4 className="mb-4 text-sm font-medium leading-none">
                                Networks
                            </h4>
                            {networkListData.map((network, index) => (
                                <div key={index}>{network.name}</div>
                            ))}
                        </div>
                    </ScrollArea>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
