/* eslint-disable react-refresh/only-export-components */
import { Button } from "@/components/ui/button";
import { databaseUrl } from "@/servers";
import React, { useCallback, useEffect, useRef, useMemo, useState, Component } from "react";
import { Link } from "react-router-dom";
import Tree from 'react-d3-tree';

type NodeData = {
  mac: string;
  ip: string;
  mac_vendor: string;
  os_vendor: string;
  os_type: string;
  hostname: string;
  parent: string;
  ports: string;
}

const renderNodeWithCustomEvents = ({
  nodeDatum,
  toggleNode,
}) => {
  const text = nodeDatum.attributes?.hostname;
  return (
  
  <g>
    <circle r="15" onClick={toggleNode}/>
    {(nodeDatum.__rd3t.collapsed || (!nodeDatum.__rd3t.collapsed && nodeDatum.children.length == 0)) ? (
      <text fill="black" x="20" dy="5" strokeWidth="1">
        {text}
      </text>
    ) : (
      <text fill="black" x={-text.length*10 - 15} dy="5" strokeWidth="1">
        {text}
      </text>
    )}
  </g>
)};

const NetworkTree = (params : any) => {

  const { networkID } = params;
  const separation = {siblings:0.5, nonSiblings:1};

  const {innerWidth: x, innerHeight: y} = window;
  const translate = {x: x/5, y: y/2};
  
  let state = {
    name: "loading",
    children: [],
    attributes: {
      mac: "loading",
      ip: "loading",
      mac_vendor: "loading",
      os_vendor: "loading",
      os_type: "loading",
      hostname: "loading",
      parent: "loading",
      ports: "loading"
    }
  }
  
  const [networkData, setNetworkData] = useState(state);

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
      .then((res) => res.json())
      .then((data) => {
        if (data["status"] === 200) {
          let devices = new Map<string, any>();
          for (let device of data["content"]) {
            
            let dev_obj = {
              name: device["hostname"],
              children: [],
              attributes: {
                mac: device["mac"],
                ip: device["ip"],
                mac_vendor: device["mac_vendor"],
                os_vendor: device["os_vendor"],
                os_type: device["os_type"],
                hostname: device["hostname"],
                parent: device["parent"],
                ports: device["ports"]
              }
            }
            
            devices.set(device["ip"], dev_obj);
          }

          let root = null;
          
          for (let [k, v] of devices) {
            let parent = v.attributes.parent;
            if (devices.has(parent)) {
              devices.get(parent).children.push(v);
            
            } else {
              root = k;
            }
          }

          if (root == null) {
            const empty = {name: "No Devices", attributes: {parent: "0"}, children: []}
            setNetworkData(empty);
            
          } else {
            const rootNode = devices.get(root);
            setNetworkData(rootNode);
          }

        } else {
          const empty = {name: "No Devices", attributes: {parent: "0"}, children: []}
          setNetworkData(empty);
          console.log(data["status"] + " " + data["message"]);
        }
      });
  }, [networkID]);


  return (
    <div className="w-full h-full flex flex-col justify-start items-start h-full gap-3 px-3 text-left">
      <Button style={{display: "flex", marginLeft: "auto"}}>
        <Link to={"../../DeviceListView/" + networkID}>List View </Link>
      </Button>
      <div id="treeWrapper" style={{ width: '100%', height: '100%' }}>
      <Tree 
        data={networkData} 
        hasInteractiveNodes
        renderCustomNodeElement={(rd3tProps) =>
          renderNodeWithCustomEvents({ ...rd3tProps })
        }
        onNodeMouseOver={(...args) => {
          console.log('onNodeMouseOver', args);
        }}
        enableLegacyTransitions={true}
        transitionDuration={500}
        centeringTransitionDuration={800}
        collapsible={true}
        zoomable={true}
        draggable={true}
        separation={separation}
        translate={translate}
        depthFactor={200}
        
        />
    </div>
  </div>)
}


export default function (params: any) {

  const { networkID } = params;
  return (
    <NetworkTree networkID={networkID} />
  );
}