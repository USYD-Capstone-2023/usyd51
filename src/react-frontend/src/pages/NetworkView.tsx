import { useParams } from "react-router-dom";

const NetworkView = () => {
    const { networkID } = useParams();
    console.log("Test" + networkID);
    return <div className="text-black">Name: {networkID}</div>;
};

export default NetworkView;
