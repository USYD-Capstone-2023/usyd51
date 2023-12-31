import { useCallback, useEffect, useState } from "react";
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

const timeFormat = {
  day: "numeric",
  month: "numeric",
  year: "numeric",
  hour: "numeric",
  minute: "numeric",
};
function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  window.dispatchEvent(errorEvent);
}


const DashboardChart = ({ networkID, mode="normal" }) => {
  const [data, setData] = useState([
    { time: "Page A", uv: 400, pv: 2400, amt: 2400 },
  ]);

  useEffect(() => {
    if (networkID == null) {
      return;
    }
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      console.log("User is logged out!");
      return;
    }
    const options = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept" : "application/json",
      },
    };

    let url;
    if (mode == "daemon") {
      url = databaseUrl + "daemon/networks/"
    } else {
      url = databaseUrl + "networks/"
    }

    fetch(url + networkID + "/snapshots", options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status === 200) {
          console.log(data["content"]);
          data["content"].forEach((element: any) => {
            const date = new Date(element.timestamp * 1000);
            const hours = date.getHours().toString().padStart(2, "0");
            const minutes = date.getMinutes().toString().padStart(2, "0");
            element.time = hours + ":" + minutes;
          });
          data["content"].sort((a: any, b: any) => a.timestamp - b.timestamp);
          setData(data["content"]);
        } else {
          setData([]);
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  }, [networkID]);

  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data}>
        <defs>
          <linearGradient id="colorUv" x1="0" y1="0" x2="1" y2="0">
            <stop offset="20%" stopColor="#D2AAEC" stopOpacity={1} />
            <stop offset="80%" stopColor="#ECBA51" stopOpacity={1} />
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

        <YAxis
          label={{
            value: "Number of Devices",
            angle: -90,
            position: "insideLeft",
          }}
        />

        <XAxis
          dataKey="time"
          name="Time"
          tickFormatter={(timestamp) => {
            return timestamp;
          }}
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
