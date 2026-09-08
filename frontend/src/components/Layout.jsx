import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/contests", label: "Contests" },
  { to: "/goals", label: "Goals" },
  { to: "/projects", label: "Projects" },
  { to: "/profile", label: "Profile" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-line bg-panel flex flex-col">
        <div className="px-5 py-6 border-b border-line">
          <div className="font-mono text-lg tracking-tight text-amber">DevPulse</div>
          <div className="text-xs text-muted mt-1">developer command center</div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `block px-3 py-2 rounded text-sm transition-colors ${
                  isActive
                    ? "bg-panel2 text-paper border-l-2 border-amber pl-[10px]"
                    : "text-muted hover:text-paper hover:bg-panel2"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-line">
          <div className="text-sm text-paper truncate">{user?.full_name || user?.email}</div>
          <button
            onClick={handleLogout}
            className="mt-2 text-xs text-muted hover:text-alert transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0 px-8 py-8 max-w-6xl">
        <Outlet />
      </main>
    </div>
  );
}
