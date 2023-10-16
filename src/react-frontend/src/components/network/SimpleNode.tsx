import { Handle, Position } from "reactflow";
import { Card, CardContent, CardHeader } from "../ui/card";

const SimpleNode = ({
  data,
  isConnectable,
  selected,
}: {
  data: any;
  isConnectable: boolean;
  selected: boolean;
}) => {
  const nodeTitle = data.hostname !== "unknown" ? data.hostname : data.ip;
  return (
    <div className="text-updater-node">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <Card>
        <CardHeader>{nodeTitle}</CardHeader>
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
                <li>Hostname: {data.hostname}</li>
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
        position={Position.Bottom}
        id="a"
        isConnectable={isConnectable}
      />
      <Handle
        type="source"
        position={Position.Top}
        id="b"
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default SimpleNode;
