/* eslint-disable react-refresh/only-export-components */
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import Dagre from "dagre";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import ReactFlow, {
  ReactFlowProvider,
  Panel,
  useNodesState,
  useEdgesState,
  useReactFlow,
  Background,
  Controls,
} from "reactflow";
import "reactflow/dist/style.css";
import SimpleNode from "./network/SimpleNode";



type NetworkElement = {
  mac: string;
  ip: string;
  mac_vendor: string;
  os_vendor: string;
  os_type: string;
  hostname: string;
  parent: string;
  ports: string;
};

interface LayoutFlowProps {
  networkID: string | undefined;
}

const nodeWidth = 500;
const nodeHeight = 36;
const maxNum = 10;

function throwCustomError(message: any) {
  const errorEvent = new CustomEvent('customError', {
    detail: {
      message: message
    }
  });
  window.dispatchEvent(errorEvent);
}

async function getAllSnapshots(networkID: any){
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
  try {
    const res = await fetch(databaseUrl + `networks/${networkID}/snapshots`, options);
    if (!res.ok) throwCustomError(res.status + ":" + res.statusText);
    const data = await res.json();
    if (data["status"] === 200) {
      return data["content"];  // return snapshots
    } else {
      throwCustomError(data["status"] + " " + data["message"]);
    }
  } catch (error) {
    throwCustomError("Something has gone wrong");
    return [];
  }
}

const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

const LayoutFlow = (params: LayoutFlowProps) => {
  const [num, setNum] = useState(0);
  const { networkID } = params;
  const [networkData, setNetworkData] = useState<NetworkElement[]>([]);
  const { fitView } = useReactFlow();

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]); 

  const [allSnapshots, setAllSnapshots] = useState([]);
  const [currSnapshot, setCurrSnapshot] = useState(-1);

  useEffect(() => { 
    const fetchData = async () => {
      try {
        const snapshots = await getAllSnapshots(networkID);
        setAllSnapshots(snapshots);
        setCurrSnapshot(snapshots.length-1)
      } catch (error) {
        console.error("Error fetching snapshots:", error);
      }
    };
    fetchData();
  }, [networkID]);

  //console.log(currSnapshot);  
 
  const getLayoutedElements = useCallback(
    (nodes: any, edges: any, options: any) => {
      const isHorizontal = options.direction === "LR";

      g.setGraph({ rankdir: options.direction });

      edges.forEach((edge: any) => g.setEdge(edge.source, edge.target));
      nodes.forEach((node: any) => g.setNode(node.id, node));

      Dagre.layout(g);

      nodes.forEach((node: any) => {
        node.targetPosition = isHorizontal ? "left" : "top";
        node.sourcePosition = isHorizontal ? "right" : "bottom";

        // We are shifting the dagre node position (anchor=center center) to the top left
        // so it matches the React Flow node anchor point (top left).
        const nodeWithPosition = g.node(node.id);
        node.position = {
          x: nodeWithPosition.x - nodeWidth / 2,
          y: nodeWithPosition.y - nodeHeight / 2,
        };

        return node;
      });

      return { nodes, edges };
    },
    [nodes]
  );

  const onLayout = useCallback(
    (direction: any) => {
      const layouted = getLayoutedElements(nodes, edges, { direction });

      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);

      window.requestAnimationFrame(() => {
        fitView();
      });
    },
    [nodes, edges, setNodes, setEdges, fitView]
  );

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
        "Accept" : "application/json",
      },
    };
    fetch(databaseUrl + `networks/${networkID}/devices`, options)
    .then((res) => {
      if (!res.ok) {
        throwCustomError(res.status + ":" + res.statusText);
      }
      return res.json();
    })
      .then((data) => {
        if (data["status"] === 200) {
          setNetworkData(data["content"]);
        } else {
          setNetworkData([]);
          throwCustomError(data["status"] + " " + data["message"]);
        }
      })
      .catch((error) => {
        throwCustomError("Network Error: Something has gone wrong.");
      });
  }, []);

  useEffect(() => {
    let newNodes = [];
    let newEdges = [];
    if (networkData.length == 0) {
      return;
    }
    for (let device of networkData) {
      let node = {
        id: device.ip,
        data: { ...device },
        position: { x: 100, y: 100 },
        type: "simpleNode",
      };
      newNodes.push(node);
      if (device.parent === "unknown") {
        continue;
      }
      let edge = {
        id: `${device.parent}-${device.ip}`,
        source: device.parent,
        target: device.ip,
      };
      newEdges.push(edge);
    }

    //console.log(newNodes);
    //console.log(newEdges);

    setNodes(newNodes);
    setEdges(newEdges);
  }, [networkData, setEdges, setNodes]);

  useEffect(() => {
    if (nodes.length > 0 && edges.length > 0 && num < maxNum) {
      onLayout("LR");
      onLayout("TB");
      setNum(num + 1);
    }
  }, [nodes, edges, onLayout, num]);

  const nodeTypes = useMemo(() => {
    return { simpleNode: SimpleNode };
  }, []);

  async function getSnapshot(next: boolean) {
    console.log("OLD: ");
    console.log(allSnapshots[currSnapshot]);
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
        "Accept": "application/json",
      },
    };
  
    try {
      if(next){
        if (currSnapshot === allSnapshots.length-1){
          throwCustomError("This is the most recent snapshot");
          return;
        } 
        else{
          setCurrSnapshot(currSnapshot + 1);
        }


      }
      else{
        if (currSnapshot === 0){
          throwCustomError("This is the earliest snapshot");
          return;
        } 
        else{
          setCurrSnapshot(currSnapshot - 1);
        }
      }

      fetch(databaseUrl + `networks/${networkID}/snapshots/${allSnapshots[currSnapshot]["timestamp"]}`, options)
        .then((res) => {
          if (!res.ok) {
            throwCustomError(res.status + ":" + res.statusText);
          }
          return res.json();
        })
          .then((data) => {
            if (data["status"] === 200) {
              setNodes([]);
              setEdges([]);

              let newNetworkData = data["content"];

              let newNodes = [];
              let newEdges = [];
              if (newNetworkData.length == 0) {
                return;
              }
              for (let device of newNetworkData) {
                let node = {
                  id: device.ip,
                  data: { ...device },
                  position: { x: 100, y: 100 },
                  type: "simpleNode",
                };
                newNodes.push(node);
                if (device.parent === "unknown") {
                  continue;
                }
                let edge = {
                  id: `${device.parent}-${device.ip}`,
                  source: device.parent,
                  target: device.ip,
                };
                newEdges.push(edge);
              }
              setNodes(newNodes);
              setEdges(newEdges);
              onLayout("LR");

            } else {
              setNetworkData([]);
              throwCustomError(data["status"] + " " + data["message"]);
            }
          })
          .catch((error) => {
            throwCustomError("Network Error: Something has gone wrong.");
          });
  
    } catch (error) {
      throwCustomError("Snapshot Unavailable.");
    }
    console.log("NEW: ");
    console.log(allSnapshots[currSnapshot]);
    return;

  }
  

  




  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      nodeTypes={nodeTypes}
      onEdgesChange={onEdgesChange}
      fitView
    >
      <Background />
      <Controls />
      <Panel position="top-right">
        <Button onClick={() => onLayout("TB")}>vertical layout</Button>
        <Button onClick={() => onLayout("LR")}>horizontal layout</Button>
        <Button>
          {" "}
          <Link to={"../../DeviceListView/" + networkID}>List View </Link>
        </Button>
      </Panel>
      <Panel position="bottom-right">
        <div className="flex">
          <Button onClick={(event) => {event.preventDefault();getSnapshot(false);}}>Previous Snapshot</Button>
          <p className="bg-primary text-primary-foreground shadow w-10 opacity-80 align-middle inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 ml-5 mr-5">{currSnapshot+1}/{allSnapshots.length}</p>
          <Button onClick={(event) => {event.preventDefault();getSnapshot(true);}}>Next Snapshot</Button>
        </div>
      </Panel>
    </ReactFlow>
  );
};

export default function (params: LayoutFlowProps) {
  const { networkID } = params;
  return (
    <ReactFlowProvider>
      <LayoutFlow networkID={networkID} />
    </ReactFlowProvider>
  );
}
