import Sidebar from "@/components/sidebar";
import Table from "@/components/table/page";

const ListView = () => {
    return (        
        <div className="flex w-full h-full dark:bg-black" >
            <Sidebar />
            <Table />
        </div>
    );
};

export default ListView;
