import Dashboard from "@/components/daemonDashboard";
import Sidebar from "@/components/sidebar";

const DaemonPage = () => {
    return (
        <div className="flex w-full h-full gap-10 ">
            <Sidebar />
            <Dashboard />
        </div>
    );
};

export default DaemonPage;
