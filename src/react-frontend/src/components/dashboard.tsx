import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useCallback, useEffect, useState } from "react";
import { Button } from "./ui/button";
import DashboardChart from "./DashboardChart";
import { Link } from "react-router-dom";
import { Heart, Search, Plus, Clock } from "lucide-react";
import { databaseUrl, scannerUrl } from "@/servers";
import { Progress } from "@radix-ui/react-progress";

const CustomCard = (props: any) => {
  const { title, subtitle, children } = props;
  return (
    <Card className="w-full h-full flex justify-center items-center gap-3 p-10">
      <div className="flex justify-center items-center rounded-full bg-gray-200 w-1/6 aspect-square ">
        {children}
      </div>

      <div className="flex flex-col items-left justify-left w-5/6">
        <CardTitle className="justify-left text-xl text-left">
          {title}
        </CardTitle>
        <CardDescription className=" text-left">{subtitle}</CardDescription>
      </div>
    </Card>
  );
};

const NetworkButton = (props: any) => {
  const { name, id } = props;
  return (
    <Link to={"/networkView/" + id}>
      <Card className="">{name}</Card>
    </Link>
  );
};

const NewNetworkButton = (props: any) => {
  const { setNewNetworkId } = props;
  const [loadingBarActive, setLoadingBarActive] = useState(false);
  const [loadingBarProgress, setLoadingBarProgress] = useState({
    label: " ",
    progress: -1,
    total: -1,
  });

  // const [networkId, setNetworkId] = useState(-1);
  const authToken = localStorage.getItem("Auth-Token");
  if (authToken == null) {
    console.log("User is logged out!");
    return;
  }
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Auth-Token": authToken,
      Accept: "application/json",
    },
  };

  const createNewNetwork = useCallback(() => {
    if (!loadingBarActive) {
      fetch(scannerUrl + "scan/-1", options)
        .then((res) => res.json())
        .then((data) => {
          if (data["status"] === 200) {
            setNewNetworkId(parseInt(data["content"]));
          } else {
            console.log(data["status"] + " " + data["message"]);
          }
        });
      setLoadingBarActive(true);
    }
  }, [loadingBarActive]);

  useEffect(() => {
    let intervalId: string | number | NodeJS.Timeout | undefined;

    if (loadingBarActive) {
      intervalId = setInterval(() => {
        fetch(scannerUrl + "scan/progress", options)
          .then((res) => res.json())
          .then((data) => {
            if (data["status"] === 200) {
              setLoadingBarProgress({
                label: data["label"],
                total: parseInt(data["total"]),
                progress: parseInt(data["progress"]),
              });
            } else {
              console.log(data["status"] + " " + data["message"]);
            }
          });
      }, 100);
    }

    // Cleanup
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [loadingBarActive]);

  let getLoadingBar = useCallback(() => {
    return (
      <Progress
        value={
          Math.floor(100 * loadingBarProgress.progress) /
          loadingBarProgress.total
        }
      ></Progress>
    );
  }, [loadingBarProgress]);

  if (!loadingBarActive) {
    return (
      <Card className="w-full" onClick={createNewNetwork}>
        Create new network
      </Card>
    );
  } else {
    return <Card className="w-full">{getLoadingBar()}</Card>;
  }
};

const Dashboard = (props: any) => {
  const [networkListData, setNetworkListData] = useState([
    { name: "TestName", id: 0 },
  ]);

  const [newNetworkId, setNewNetworkId] = useState(-1);

  useEffect(() => {
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
        Accept: "application/json",
      },
    };

    fetch(databaseUrl + "networks", options)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 200) {
          console.log(data);
          let network_list = [];
          for (let network of data["content"]) {
            network_list.push({ name: network.name, id: network.network_id });
          }

          setNetworkListData(network_list);
        } else {
          setNetworkListData([]);
          console.log(data.status + " " + data["message"]);
        }
      });
  }, [newNetworkId]);

  return (
    <div className="w-full flex flex-col justify-center items-center h-full gap-10">
      <div className="h-1/6 w-full flex items-center justify-center">
        <div className="w-full h-full flex gap-10 justify-between items-center">
          <CustomCard title="5/5" subtitle="All Networks Live">
            <Heart className="text-red-500 fill-current" />
          </CustomCard>
          <CustomCard title="178" subtitle="Scans Last Week">
            <Search />
          </CustomCard>
          <CustomCard title="190" subtitle="New Devices Found">
            <Plus />
          </CustomCard>
          <CustomCard title="100%" subtitle="Uptime">
            <Clock />
          </CustomCard>
        </div>
      </div>
      <div className="h-full flex gap-10 w-full">
        <Card className="w-1/3   opacity-80 rounded-xl">
          <ScrollArea>
            <div>
              <h1 className="text-2xl font-medium leading-none  py-4 px-8">
                Networks
                <Separator />
              </h1>
              <div className="flex justify-center items-center gap-3 flex-col px-8">
                {networkListData.map((network, index) => (
                  <div className="w-full" key={index}>
                    <NetworkButton name={network.name} id={network.id} />
                  </div>
                ))}
                <NewNetworkButton
                  loadingId={-1}
                  setNewNetworkId={setNewNetworkId}
                />
              </div>
            </div>
          </ScrollArea>
        </Card>
        <Card className="flex flex-col justify-between items-center w-2/3 gap-10 pb-8">
          <div className="h-full w-full  rounded-xl">
            <div className="h-1/8 font-medium text-2xl p-8 text-left">
              Home Network
            </div>
            <div className="flex justify-center items-center h-5/6 w-full p-3">
              <DashboardChart />
            </div>
          </div>
          <Button onClick={createNewNetwork}>
            <Link to="/newNetwork">
              <CardHeader>
                <CardTitle>Create New Network</CardTitle>
              </CardHeader>
            </Link>
          </Button>
        </Card>
      </div>
    </div>
  );
};

const createNewNetwork = () => {
  console.log("Make a network");
};

export default Dashboard;
