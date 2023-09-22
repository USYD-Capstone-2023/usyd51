import { useParams } from "react-router-dom";
import NetworkVisualiser from "../components/NetworkVisualiser";
import Sidebar from "@/components/sidebar";

const NetworkView = () => {
  const { networkID } = useParams();

  return (
    <div className="flex w-full h-full">
      <Sidebar />
      <NetworkVisualiser networkID={networkID} />
    </div>
  );
};

export default NetworkView;
