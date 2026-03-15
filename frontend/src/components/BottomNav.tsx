"use client";

import { usePathname, useRouter } from "next/navigation";
import { Home, CalendarDays, Repeat, BarChart3, User } from "lucide-react";

const tabs = [
  { path: "/", icon: Home, label: "Home" },
  { path: "/planner", icon: CalendarDays, label: "Planner" },
  { path: "/habits", icon: Repeat, label: "Habits" },
  { path: "/progress", icon: BarChart3, label: "Progress" },
  { path: "/profile", icon: User, label: "Profile" },
];

export default function BottomNav() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 z-50">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {tabs.map((tab) => {
          const isActive = pathname === tab.path;
          const Icon = tab.icon;
          return (
            <button
              key={tab.path}
              onClick={() => {
                if (pathname === tab.path) {
                  router.refresh();
                } else {
                  router.push(tab.path);
                }
              }}
              className={`flex flex-col items-center justify-center w-full h-full transition-colors ${
                isActive
                  ? "text-blue-400"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              <Icon size={22} strokeWidth={isActive ? 2.5 : 1.5} />
              <span className="text-[10px] mt-1 font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
