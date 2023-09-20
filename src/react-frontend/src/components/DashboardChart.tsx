import { useState } from "react";
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
        { name: "Page A", uv: 400, pv: 2400, amt: 2400 },
        { name: "Page B", uv: 500, pv: 2400, amt: 2400 },
        { name: "Page C", uv: 350, pv: 2400, amt: 2400 },
        { name: "Page C", uv: 310, pv: 2400, amt: 2400 },
        { name: "Page C", uv: 320, pv: 2400, amt: 2400 },
        { name: "Page C", uv: 350, pv: 2400, amt: 2400 },
    ]);
    return (
        <div className="bg-white rounded-xl w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data}>
                    <defs>
                        <linearGradient
                            id="colorUv"
                            x1="0"
                            y1="0"
                            x2="1"
                            y2="0"
                        >
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
                        dataKey="uv"
                        stroke="#efefef"
                        fill="url(#colorUv)"
                        opacity={1}
                    />
                    <Line
                        type="monotone"
                        dataKey="uv"
                        stroke="#efefef"
                        fill="#8884d8"
                    />

                    <YAxis />

                    <XAxis dataKey="name" />
                </ComposedChart>
            </ResponsiveContainer>
        </div>
    );
};

export default DashboardChart;
