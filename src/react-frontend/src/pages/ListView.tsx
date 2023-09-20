import Sidebar from "@/components/sidebar";
import Table from "@/components/table/page"

const ListView = () => {
    return (        
    <div className="flex w-full h-full gap-10 bg-gray-900">
        <Sidebar />
        <Table />
    </div>
    );
};

export default ListView;
