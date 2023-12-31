import Dashboard from "@/components/dashboard";
import Sidebar from "@/components/sidebar";

const Home = () => {
    return (
        <div className="flex w-full h-full gap-10 ">
            <Sidebar />
            <Dashboard />
        </div>
    );
};

export default Home;
