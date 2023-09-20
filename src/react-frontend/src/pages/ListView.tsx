import Sidebar from "@/components/sidebar";
import Table from "@/components/table/page";

const ListView = () => {
    return (        
        <div className="flex w-full h-full gap-10">
            <Sidebar />
            <div className="w-full">
                <h1 className="text-2xl font-semibold mb-4 flex justify-start text-gray-900">All Networks</h1>
                <div className="flex justify-start">
                    <Table />
                </div>
            </div>
        </div>
    );
};

export default ListView;
