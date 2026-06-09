"use client";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { usePathname } from "next/navigation";

import { Moon, Sun } from "lucide-react";
import Link from "next/link";
import { useTheme } from "next-themes";
import CoreProjectIcon from "@/icons/coreproject/CoreProject.svg";
import CoreIcon from "@/icons/coreproject/CoreIcon.svg";

export function Navbar() {
  const pathname = usePathname();
  const { setTheme } = useTheme();

  const buttonMapping = {
    dashboard: "/",
    radar: "/radar",
    health: "/health",
  };

  return (
    <div className="mx-2 my-5 grid h-12 grid-cols-3 md:mx-10">
      {/* Left section */}
      <div>
        <div className="flex flex-col items-start justify-center">
          <div className="hidden h-3 w-40 md:block">
            <div className="relative flex h-10 w-[180px] items-center justify-center">
              <div className="dark:bg-background bg-primary absolute inset-0 rounded-md p-2"></div>
              <CoreProjectIcon
                width="150"
                height="25"
                className="absolute inset-0 m-2 inline-grid justify-self-center"
              />
            </div>
          </div>
        </div>
        <div className="flex">
          <div className="block h-3 w-8 md:hidden">
            <CoreIcon />
          </div>
        </div>
      </div>

      {/* Middle section  */}
      <div className="flex items-center justify-center gap-3">
        {Object.entries(buttonMapping).map(([name, link], key) => {
          const isActive = pathname === link;

          if (isActive) {
            return (
              <Button key={key} variant="default">
                <p className="capitalize">{name}</p>
              </Button>
            );
          } else {
            return (
              <Button key={key} variant="outline" asChild>
                <Link href={link}>
                  <p className="capitalize">{name}</p>
                </Link>
              </Button>
            );
          }
        })}
      </div>

      {/*Right section*/}
      <div className="flex items-center justify-end">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="icon">
              <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
              <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={() => {
                setTheme("light");
              }}
            >
              Light
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                setTheme("dark");
              }}
            >
              Dark
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => {
                setTheme("system");
              }}
            >
              System
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
