/* eslint-disable react-refresh/only-export-components */
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import Dagre from "dagre";
import React, { useCallback, useEffect, useState } from "react";
import { redirect } from "react-router";
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

import "reactflow/dist/style.css";

const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (nodes: any, edges: any, options: any) => {

  const isHorizontal = options.direction === "LR";

  g.setGraph({ rankdir: options.direction });

  edges.forEach((edge: any) => g.setEdge(edge.source, edge.target));
  nodes.forEach((node: any) => g.setNode(node.id, node));

  Dagre.layout(g);

  nodes.forEach((node: any) => {
    const nodeWithPosition = g.node(node.id);
    node.targetPosition = isHorizontal ? "left" : "top";
    node.sourcePosition = isHorizontal ? "right" : "bottom";

    // We are shifting the dagre node position (anchor=center center) to the top left
    // so it matches the React Flow node anchor point (top left).
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    };

    return node;
  });

  return { nodes, edges };
};

const LayoutFlow = (params: LayoutFlowProps) => {
  const [showReactFlow, setShowReactFlow] = useState(true);
  const [num, setNum] = useState(0);
  const { networkID } = params;
  const [networkData, setNetworkData] = useState<NetworkElement[]>([]);
  const { fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

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

  const toggleReactFlowVisibility = () => {
    setShowReactFlow(!showReactFlow);
  };

  useEffect(() => {
    const authToken = localStorage.getItem("Auth-Token");
    if (authToken == null) {
        console.log("User is logged out!");
        return;
    }
    const options = {method: "GET", headers: {"Content-Type" : "application/json", "Auth-Token" : authToken, 'Accept': 'application/json'}}
    fetch(databaseUrl + `networks/${networkID}/devices`, options)
      .then((res) => (res.json()))
      .then((data) => {

        if (data["status"] === 200) {
          setNetworkData(data["content"]);

        } else {
          setNetworkData([]);
          console.log(data["status"] + " " + data["message"]);
        }
      });
  }, [networkID]);

  useEffect(() => {
    let newNodes = [];
    let newEdges = [];
    if (networkData.length == 0) {
      return;
    }
    for (let device of networkData) {
      let node = {
        id: device.ip,
        data: { label: device.hostname },
        position: { x: 100, y: 100 },
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
            onLayout('LR');
            onLayout('TB');
            setNum(num +1)
    }
  }, [nodes, edges, onLayout, num]);


  return (
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
        <Panel position="top-right">
          <Button onClick={() => onLayout("TB")}>vertical layout</Button>
          <Button onClick={() => onLayout("LR")}>horizontal layout</Button>
          <Button>  <Link to={"../../DeviceListView/" + networkID}>List View </Link></Button>
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
