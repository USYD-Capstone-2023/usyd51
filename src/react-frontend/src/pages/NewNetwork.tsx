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
function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  window.dispatchEvent(errorEvent);
}


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
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data["status"] === 200) {
          setNetworkId(parseInt(data["content"]));
        } else {
          throwCustomError(data["status"] + " " + data["message"]);
        }})
        .catch((error) => {
          throwCustomError("Network Error: Something has gone wrong.");
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
