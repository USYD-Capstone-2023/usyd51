import { useParams } from "react-router-dom";

const NetworkView = () => {
    const { networkID } = useParams();
    return <>Name: {networkID}</>;
};

export default NetworkView;
