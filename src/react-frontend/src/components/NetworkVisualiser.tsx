import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import Dagre from "dagre";
import React, { useCallback, useEffect, useState } from "react";
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
  const { networkID } = params;
  const [networkData, setNetworkData] = useState<NetworkElement[]>([]);
  const { fitView } = useReactFlow();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    fetch(databaseUrl + `/networks/${networkID}/devices`)
      .then((res) => res.json())
      .then((data) => {
        // console.log(data);
        setNetworkData(data);
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

    console.log(newNodes);
    console.log(newEdges);

    setNodes(newNodes);
    setEdges(newEdges);
  }, [networkData]);

  const onLayout = useCallback(
    (direction: any) => {
      const layouted = getLayoutedElements(nodes, edges, { direction });

      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);

      window.requestAnimationFrame(() => {
        fitView();
      });
    },
    [nodes, edges]
  );

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