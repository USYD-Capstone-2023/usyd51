import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

type NetworkItem = {
    mac: string,
    ip: string,
    mac_vendor: string,
    os_family: string,
    os_vendor: string,
    os_type: string,
    hostname: string,
    parent: string,
    ports: string,
}



const NetworkView = () => {
    const { networkID } = useParams();
    const [ networkDevices, setNetworkDevices] = useState<NetworkItem[]>([]);

    useEffect(() => {
        fetch("http://127.0.0.1:5000/network/" + networkID + "/devices").then((res)=>(res.json())).then((data) => {
            setNetworkDevices(data);
        })
    }, [])


    return <><div>
    <h1>Network View</h1>
    <ul>
        {networkDevices.map((device, index) => (
            <li key={index}>
                <strong>MAC:</strong> {device.mac}<br />
                <strong>IP:</strong> {device.ip}<br />
                <strong>MAC Vendor:</strong> {device.mac_vendor}<br />
                <strong>OS Family:</strong> {device.os_family}<br />
                <strong>OS Vendor:</strong> {device.os_vendor}<br />
                <strong>OS Type:</strong> {device.os_type}<br />
                <strong>Hostname:</strong> {device.hostname}<br />
                <strong>Parent:</strong> {device.parent}<br />
                <strong>Ports:</strong> {device.ports}<br />
                <br></br>
            </li>
        ))}
    </ul>
</div></>;
};

export default NetworkView;
