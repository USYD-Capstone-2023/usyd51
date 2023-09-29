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


const ListView = () => {
    const { networkID } = useParams();
    //const networkID = 0;
    const [ networkDevices, setNetworkDevices] = useState<NetworkItem[]>([]);
    useEffect(() => {
        fetch("http://192.168.12.104:5000/networks/" + networkID + "/devices").then((res)=>(res.json())).then((data) => {
            setNetworkDevices(data);
            //console.log(data);
        })
    }, [])

    return (        
        <div className="flex w-full h-full" style={{
            height: "95vh",
            width: "95%",
            marginLeft: "5%",
            overflowY: "scroll",
            overflowX: "scroll"}}>
            <table>
                <thead>
                    <tr style={{border: "5px solid red"}}>
                        <th>MAC</th>
                        <th>IP</th>
                        <th>MAC Vendor</th>
                        <th>OS Family</th>
                        <th>OS Vendor</th>
                        <th>OS Type</th>
                        <th>Hostname</th>
                        <th>Parent</th>
                        <th>Ports</th>
                    </tr>
                </thead>
                <tbody >
                    {networkDevices.map((device, index) => (
                        <tr key={index}>
                        <td>{device.mac}</td>
                        <td>{device.ip}</td>
                        <td>{device.mac_vendor}</td>
                        <td>{device.os_family}</td>
                        <td>{device.os_vendor}</td>
                        <td>{device.os_type}</td>
                        <td>{device.hostname}</td>
                        <td>{device.parent}</td>
                        <td>{device.ports}</td>
                        </tr>
                    ))}
                </tbody>
        </table>
        </div>
    );
};

export default ListView;
