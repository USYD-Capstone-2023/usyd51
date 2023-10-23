import { Handle, Position } from "reactflow";
import { Card, CardContent, CardHeader } from "../ui/card";
import {FileInput} from "lucide-react";

const SimpleNode = ({
  data,
  isConnectable,
  selected,
  targetPosition,
  sourcePosition,
}: {
  data: any;
  isConnectable: boolean;
  selected: boolean;
  targetPosition?: Position;
  sourcePosition?: Position;
}) => {
  const nodeTitle = data.hostname !== "unknown" ? data.hostname : data.ip;

  // want a node to have left/right or top/bottom target/source
  if (targetPosition === Position.Left) {
    sourcePosition = Position.Right;
  }
  else if (sourcePosition === Position.Right) {
    targetPosition = Position.Left;
  }
  if (targetPosition == undefined || sourcePosition == undefined) {
    targetPosition = Position.Top;
    sourcePosition = Position.Bottom;
  }
  
  return (
    <div className="text-updater-node">
      <Handle
        type="target"
        position={targetPosition}
        isConnectable={isConnectable}
      />

      <Card>
        {(data.website !== "unknown" && data.website!== "Not Hosted") && (
          <FileInput style={{ position: "absolute", margin: "3", color: "green", }}></FileInput>
        )}
        <CardHeader style={{ display: 'flex', alignItems: 'center' }}>

        {nodeTitle}

        </CardHeader>
        {selected && (
          <CardContent>
            <div>
              <ul>
                <li>MAC: {data.mac}</li>
                <li>IP: {data.ip}</li>
                <li>MAC Vendor: {data.mac_vendor}</li>
                <li>OS Family: {data.os_family}</li>
                <li>OS Vendor: {data.os_vendor}</li>
                <li>OS Type: {data.os_type}</li>
                <li>Hostname:  {data.hostname}</li>
                <li>Website: {data.website!="Not Hosted" && data.website!="unknown" ? (<button><a href={data.website} target="_blank" style={{color: "blue"}}>{data.website}</a></button>) : (data.website)}</li>
                <li>Parent: {data.parent}</li>
                {data.ports !== undefined && (
                  <li>
                    Ports:{" "}
                    {data.ports.map((port: string, i: number) => (
                      <span key={i}>
                        {port}
                        {i < data.ports.length - 1 ? ", " : ""}
                      </span>
                    ))}
                  </li>
                )}
              </ul>
            </div>
          </CardContent>
        )}
      </Card>
      <Handle
        type="source"
        position={sourcePosition}
        id="a"
        isConnectable={isConnectable}
      />
      <Handle
        type="source"
        position={targetPosition}
        id="b"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default SimpleNode;
