import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { scannerUrl } from "@/servers";

type NetworkElement = {
  mac: string;
  ip: string;
  mac_vendor: string;
  os_family: string;
  os_vendor: string;
  os_type: string;
  hostname: string;
  parent: string;
  ports: string[];
};

export default function NewNetwork() {
  const [networkId, setNetworkId] = useState(-1);

  useEffect(() => {

    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
        console.log("User is logged out!");
        return;
    }
    const options = {method: "POST", headers: {"Content-Type" : "application/json", "Auth-Token" : authToken, 'Accept': 'application/json'}}

    fetch(scannerUrl + "scan/-1", options)
      .then((res) => {
        if (res.status === 200) {
          return res.json();

        } else {
          console.log("Error");
          return {};
        }})
      .then((id) => {
        console.log(id);
        setNetworkId(parseInt(id));
      });
  }, []);

  return (
    <div>
      {networkId !== -1 && (
        <Link to={"/networkView/" + networkId}>
          <Button className="py-10 text-gray-900 shadow-none">
            View Network
          </Button>
        </Link>
      )}
    </div>
  );
}
