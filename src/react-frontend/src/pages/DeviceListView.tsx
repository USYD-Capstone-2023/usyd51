import Sidebar from "@/components/sidebar";
import DeviceTable from "@/components/DeviceTable"


const DeviceListView = () => {
    return (        
        <div className="flex w-full h-full" >
            <Sidebar />
            <DeviceTable />
        </div>
    );
};

export default DeviceListView;
