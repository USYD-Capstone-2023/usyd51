import { databaseUrl } from "@/servers";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";

const ShareNetworkDropdown = ({
  userList,
  onSelect,
}: {
  userList: any;
  onSelect: (id: number) => void;
}) => {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">Share</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuLabel>Share network</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {userList?.map((user: any, index: number) => {
          return (
            <DropdownMenuItem onSelect={() => onSelect(user.id)} key={index}>
              {user.username}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default ShareNetworkDropdown;
