const SidebarButton = ({ children, ...props }) => {
  return (
    <button
      {...props}
      className="bg-transparent hover:bg-blue-500 text-blue-700 font-semibold py-2 px-4 border border-blue-500 hover:border-transparent rounded"
    >
      {children}
    </button>
  );
};

export default SidebarButton;
