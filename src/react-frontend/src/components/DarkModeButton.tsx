import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/theme-provider";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useEffect } from "react";

export function DarkMode() {
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    const usingDark = (event: any) => {
      const newColorScheme = event.matches ? "dark" : "light";
      setTheme(newColorScheme);
    };
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", usingDark);

    return window
      .matchMedia("(prefers-color-scheme: dark)")
      .removeEventListener("change", usingDark);
  }, []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button className="py-10">
          <Sun className="rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-gray-900" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-white" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          onClick={() => setTheme("light")}
          className={theme === "light" ? "light-active" : ""}
        >
          Light
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme("dark")}
          className={theme === "dark" ? "dark-active" : ""}
        >
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme("system")}
          className={theme === "system" ? "system-active" : ""}
        >
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
