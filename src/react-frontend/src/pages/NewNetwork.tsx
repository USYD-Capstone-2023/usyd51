import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

type NetworkElement = {
    mac: string,
    ip: string,
    mac_vendor: string,
    os_family: string,
    os_vendor: string,
    os_type: string,
    hostname: string,
    parent: string,
    ports: string[]
}
    


export default function NewNetwork() {

    const [ networkId, setNetworkId ] = useState(-1)

    useEffect(() => {
        fetch("http://127.0.0.1:5000/scan/-1").then(res => res.text()).then((id) => {
            setNetworkId(parseInt(id));
        }
        )
    })



    return (<div>{networkId !== -1 && <Link to={"/networkView/"+networkId}>
    <Button className="py-10 text-gray-900 shadow-none">View Network</Button>
</Link>}</div>)
}