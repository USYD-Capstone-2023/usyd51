import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from "react-router-dom";
import { Progress } from "@/components/ui/progress";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "./ui/button";
import DashboardChart from "./DashboardChart";
import { Link } from "react-router-dom";
import { Heart, Search, Plus, Clock, Edit2} from "lucide-react";
import { databaseUrl, scannerUrl } from "@/servers";
import ShareNetworkDropdown from "./ShareNetworkDropdown";

function throwCustomError(message: any) {
  console.log("errorEvent");
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  console.log(errorEvent);
  window.dispatchEvent(errorEvent);
}


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

const NewNetworkButton = (props: any) => {
  const { setNewNetworkId } = props;
  const [loadingBarActive, setLoadingBarActive] = useState(false);
  const [loadingBarProgress, setLoadingBarProgress] = useState({
    label: " ",
    progress: 0,
    total: 100,
  });

  // const [networkId, setNetworkId] = useState(-1);
  const authToken = localStorage.getItem("Auth-Token");
  if (authToken == null) {
    throwCustomError("User has been logged out.");
    return;
  }

  const createNewNetwork = useCallback(() => {
    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept" : "application/json",
      },
    };
    if (!loadingBarActive) {
      setLoadingBarActive(true);
      fetch(scannerUrl + "scan/-1", options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
      .then((data) => {
        if (data["status"] === 200) {
          setNewNetworkId(parseInt(data["content"]));
        } else {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
    }
  }, [loadingBarActive]);

  useEffect(() => {
    let intervalId: string | number | NodeJS.Timeout | undefined;
    const options = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept" : "application/json",
      },
    };
    if (loadingBarActive) {
      intervalId = setInterval(() => {
        fetch(scannerUrl + "progress", options)
        .then((res) => {
          if (!res.ok) {
            throwCustomError(res.status + ":" + res.statusText);
          }
          return res.json();
        })
          .then((data) => {
            if (data["status"] === 200) {
              if (data["message"] == "Scan finished.") {
                setNewNetworkId(0);
                clearInterval(intervalId);
                return;
              }
              setLoadingBarProgress({
                label: data["content"].label,
                total: data["content"].total,
                progress: data["content"].progress,
              });
            } else {
              clearInterval(intervalId);
            }
          })
          .catch((error) => {
            throwCustomError("Scanning server is unreachable. Please check it is running.");
          });
      }, 400);
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
      <>
        <Progress
          className="w-full"
          value={Math.floor(
            (100 * loadingBarProgress.progress) / loadingBarProgress.total
          )}
        ></Progress>
      </>
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
  const navigate = useNavigate();
  const [networkListData, setNetworkListData] = useState([
    { name: "TestName", id: 0 },
  ]);
  const [editName, setEditName] = useState(false);
  const [currentName, setCurrentName] = useState("");
  const [selectedNetworkID, setSelectedNetworkID] = useState<any | null>(null);
  const [userListData, setUserListData] = useState<any>();
  const [newNetworkId, setNewNetworkId] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);

  const NetworkButton = (props: any) => {
    const clickButton = (id: any) => {
      if (selectedNetworkID === id) {
        navigate("/networkView/" + id);
      } else {
        setSelectedNetworkID(id);
      }
    };

    const { name, id } = props;
    const buttonClass =
      selectedNetworkID === id
        ? "bg-gray-700 text-gray-300"
        : "bg-gray-300 text-black";
    return (
      <button onClick={() => clickButton(id)} className={"w-full"}>
        <Card className={`${buttonClass}`}>{name}</Card>
      </button>
    );
  };

  const rescanNetwork = (networkId: number) => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }

    const options = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept": "application/json",
      },
    };

    fetch(scannerUrl + "scan/" + networkId, options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ": " + res.statusText);
        }
        return res.json();
      })
      .then((data) => {
        if (data["status"] === 200) {
          console.log("Rescan initiated successfully");

        } else {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  };

  const shareNetworkWithUser = useCallback(
    (id: number) => {
      const authToken = localStorage.getItem("Auth-Token");
      if (authToken == null) {
        throwCustomError("User has been logged out.");
        return;
      }
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Auth-Token": authToken,
          "Accept": "application/json",
        },
      };

      fetch(databaseUrl + `networks/${selectedNetworkID}/share/${id}`, options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
        .then((data) => {
          if (data.status !== 200) {
            throwCustomError(data["status"] + " " + data["message"]);
          } else {
            update_share_list();
          }
        })
        .catch((error) => {
          throwCustomError("Network Error: Something has gone wrong.");
        });;

    },
    [selectedNetworkID]
  );

  useEffect(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
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

    fetch(databaseUrl + "networks", options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status === 200) {
          let network_list = [];
          for (let network of data["content"]) {
            network_list.push({ name: network.name, id: network.network_id });
          }

          if (network_list.length > 0) {
            setSelectedNetworkID(network_list[0].id);
          }
          setNetworkListData(network_list);
        } else {
          setNetworkListData([]);
          throwCustomError(data.status + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Scanning server is unreachable. Please check it is running.");
      });
  }, [newNetworkId]);

  const handleNewNetworkName = useCallback(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }
    const options = {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Auth-Token": authToken,
        "Accept" : "application/json",
      },
    };

    fetch(
      databaseUrl + `networks/${selectedNetworkID}/rename/${currentName}`,
      options
    )
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status !== 200) {
          //console.log(`${data.status} ${data.content}`);
          throwCustomError(data["status"] + " " + data["message"]);
        } else {
          const options = {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              "Auth-Token": authToken,
              "Accept" : "application/json",
            },
          };

          fetch(databaseUrl + "networks", options)
          .then((res) => {
            if (!res.ok) {
              throwCustomError(res.status + ":" + res.statusText);
            }
            return res.json();
          })
            .then((data) => {
              if (data.status === 200) {
                let network_list = [];
                for (let network of data["content"]) {
                  network_list.push({
                    name: network.name,
                    id: network.network_id,
                  });
                }

                if (network_list.length > 0) {
                  setSelectedNetworkID(network_list[0].id);
                }
                setNetworkListData(network_list);
              } else {
                setNetworkListData([]);
                throwCustomError(data.status + ":" + data.message);
              }
            });
          setCurrentName("");
          setEditName(false);
        }
      })
      .catch((error) => {
        throwCustomError("Something has gone wrong.");
      });
  }, [selectedNetworkID, currentName]);

  useEffect(() => {
    if (editName && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editName]);

  const update_share_list = () => {

    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
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
    if(selectedNetworkID){
      fetch(databaseUrl +`users/${selectedNetworkID}`, options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
        .then((data) => {
          if (data.status === 200) {
            let user_list = [];
            for (let user of data["content"]["unshared"]) {
              user_list.push({
                username: user.username,
                id: user.user_id,
                email: user.email,
              });
            }

            setUserListData(user_list);
          } else {
            setUserListData([]);
            throwCustomError(data["status"] + " " + data["message"]);
          }
        })
        .catch((error) => {
          throwCustomError("Network Error: Something has gone wrong.");
        });
    }
  }

  useEffect(() => {update_share_list();}, [selectedNetworkID]);

  /*<div className="h-1/6 w-full flex items-center justify-center">
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
</div>*/

  return (
    <div className="w-full flex flex-col justify-center items-center h-full gap-10">
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
            
            {editName && (
                <input
                  type="text"
                  ref={inputRef}
                  value={currentName}
                  onChange={(e) => setCurrentName(e.target.value)}
                  onBlur={handleNewNetworkName}
                  style={{ backgroundColor: "transparent" }}
                  maxLength={25}
                />
              )}
              {!editName && (
                <span
                  onClick={() => {
                    setEditName(true);
                    inputRef.current !== null && inputRef.current.focus();
                  }}
                  style={{ display: 'flex', alignItems: 'center' }}>
                  <Edit2 className="w-4 h-4"></Edit2>
                  {
                    networkListData?.find(
                      (element) => element.id === selectedNetworkID
                    )?.name
                  }
                </span>
              )}
            </div>
            <div className="flex justify-center items-center h-5/6 w-full p-3">
              <DashboardChart networkID={selectedNetworkID} />
            </div>
          </div>
          <Button onClick={() => rescanNetwork(selectedNetworkID)}>Rescan</Button>
          <ShareNetworkDropdown
            userList={userListData}
            onSelect={shareNetworkWithUser}
          />
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
