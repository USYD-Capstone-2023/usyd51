import { Card, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from "react-router-dom";
import { Progress } from "@/components/ui/progress";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "./ui/button";
import DashboardChart from "./DashboardChart";
import { Link } from "react-router-dom";
import { Heart, Search, Plus, Clock } from "lucide-react";
import { databaseUrl, scannerUrl } from "@/servers";
import ShareNetworkDropdown from "./ShareNetworkDropdown";
//import throwCustomError from "./dashboard"

function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
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
  /*      fetch(scannerUrl + "scan/-1", options)
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
      });;*/

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

const NewNetworkButton = (props: any) => {
  const { setNewNetworkId } = props;
  const [loadingBarActive, setLoadingBarActive] = useState(false);
  const [loadingBarProgress, setLoadingBarProgress] = useState({
    label: " ",
    progress: 0,
    total: 100,
  });

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
      fetch(scannerUrl + "daemon/new", options)
      .then((res) => {
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
        .then((data) => {
          if (data["status"] != 200) {
            throwCustomError(data["status"] + " " + data["message"]);
          }
        })
        .catch((error) => {
          throwCustomError("Network Error: Something has gone wrong.");
        });;
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
        fetch(scannerUrl + "daemon/progress", options)
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
            throwCustomError("Network Error: Something has gone wrong.");
          });
      }, 400);
    } else {
      fetch(scannerUrl + "daemon/progress", options)
      .catch(error => {
        // This will be triggered by network errors, including CORS issues
        throwCustomError("Network Error: Something has gone wrong.");
      })
      .then((res) => {
        if (!res) {
          // This block is necessary because the `then` block will still be entered with an undefined `res` even after a network error
          return;
        }
        if (!res.ok) {
          throwCustomError(res.status + ":" + res.statusText);
        }
        return res.json();
      })
      .then((data) => {
        if (!data) {
          // This block is necessary because the `then` block will still be entered with an undefined `data` even after a network error
          return;
        }
        if (data["status"] === 200) {
          if (data["message"] != "Scan finished.") {
            setLoadingBarActive(true);
          }
        }
      })
      .catch((error) => {
        // This will catch any errors thrown in the preceding `then` blocks
        throwCustomError("Network Error: Something has gone wrong.");
      });
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

  useEffect(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }
    const options = {
      method: "GET",
      headers: {
        "Content-Type" : "application/json",
        "Auth-Token" : authToken,
        "Accept" : "application/json",
      },
    };

    fetch(databaseUrl + "daemon/networks", options)
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
          throwCustomError(data["status"] + " " + data["message"]);
        }
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
          throwCustomError(data.status + " " + data.content);
        } else {
          const options = {
            method: "GET",
            headers: {
              "Content-Type" : "application/json",
              "Auth-Token" : authToken,
              "Accept" : "application/json",
            },
          };

          fetch(databaseUrl + "daemon/networks", options)
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
              throwCustomError(data["status"] + " " + data["message"]);
            }
          })
          .catch((error) => {
            throwCustomError("Network Error: Something has gone wrong.");
          });

          setCurrentName("");
          setEditName(false);
        }
      });
  }, [selectedNetworkID, currentName]);

  useEffect(() => {
    if (editName && inputRef.current) {
      inputRef.current.focus();
    }
  }, [editName]);


  const start_scan = () => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }

    const options = {
      method: "POST",
      headers: {
        "Content-Type" : "application/json",
        "Auth-Token" : authToken,
        "Accept" : "application/json",
      },
    };

    fetch(scannerUrl +`daemon/start/${selectedNetworkID}`, options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status != 200) {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      });
  }

  const end_scan = () => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }

    const options = {
      method: "POST",
      headers: {
        "Content-Type" : "application/json",
        "Auth-Token" : authToken,
        "Accept" : "application/json",
      },
    };

    fetch(scannerUrl +`daemon/end`, options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status != 200) {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  }

  const share_with_user = () => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
      throwCustomError("User has been logged out.");
      return;
    }

    const options = {
      method: "POST",
      headers: {
        "Content-Type" : "application/json",
        "Auth-Token" : authToken,
        "Accept" : "application/json",
      },
    };

    fetch(databaseUrl +`daemon/${selectedNetworkID}/share`, options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data.status != 200) {
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  }

  return (
    <div className="w-full flex flex-col justify-center items-center h-full gap-10">
      <div className="h-full flex gap-10 w-full">
        <Card className="w-1/3   opacity-80 rounded-xl">
          <ScrollArea>
            <div>
              <h1 className="text-2xl font-medium leading-none  py-4 px-8">
                Daemon Networks
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
                >
                  {
                    networkListData?.find(
                      (element) => element.id === selectedNetworkID
                    )?.name
                  }
                </span>
              )}
            </div>
            <div className="flex justify-center items-center h-5/6 w-full p-3">
              <DashboardChart networkID={selectedNetworkID} mode={"daemon"}/>
            </div>
          </div>
          <div>
            <Button onClick={start_scan}>
              <CardHeader>
                <CardTitle>Resume Scan</CardTitle>
              </CardHeader>
            </Button>
            <Button onClick={end_scan} style={{margin: 10}}>
              <CardHeader>
                <CardTitle>Pause Scan</CardTitle>
              </CardHeader>
            </Button>
            <Button onClick={share_with_user}>
              <CardHeader>
                <CardTitle>Share To Dashboard</CardTitle>
              </CardHeader>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
