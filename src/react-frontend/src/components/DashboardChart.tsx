import { useEffect, useState } from "react";
import { databaseUrl } from "@/servers";
import {
    LineChart,
    Line,
    Area,
    AreaChart,
    ComposedChart,
    ResponsiveContainer,
    XAxis,
    Tooltip,
    YAxis,
    CartesianGrid,
} from "recharts";

const DashboardChart = () => {
    const [data, setData] = useState([
        { time: "Page A", uv: 400, pv: 2400, amt: 2400 },
    ]);

    useEffect(() => {
        fetch(databaseUrl + "/networks/0/snapshots").then(res => res.json()).then((data) => {
            data.forEach((element: any) => {
                const date = new Date(element.timestamp*1000);
                const hours = date.getHours().toString().padStart(2,'0');
                const minutes = date.getMinutes().toString().padStart(2,'0');
                element.time = hours + ":" + minutes;
            })
            setData(data);
        })
    }, [])






    return (
        <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
                <defs>
                    <linearGradient id="colorUv" x1="0" y1="0" x2="1" y2="0">
                        <stop
                            offset="20%"
                            stopColor="#D2AAEC"
                            stopOpacity={1}
                        />
                        <stop
                            offset="80%"
                            stopColor="#ECBA51"
                            stopOpacity={1}
                        />
                    </linearGradient>
                </defs>
                <Tooltip />
                <CartesianGrid strokeDasharray="3 3" />

                <Area
                    type="monotone"
                    dataKey="n_alive"
                    stroke="#efefef"
                    fill="url(#colorUv)"
                    opacity={1}
                />

                <YAxis
                    label={{
                        value: "Number of Devices",
                        angle: -90,
                        position: "insideLeft",
                    }}
                />

                <XAxis
                    dataKey="time"
                    label={{
                        value: "Timestamp",
                        position: "insideBottom",
                        offset: -4,
                    }}
                />
                <Line
                    type="monotone"
                    dataKey="n_alive"
                    stroke="#efefef"
                    fill="#8884d8"
                />
            </ComposedChart>
        </ResponsiveContainer>
    );
};

export default DashboardChart;
