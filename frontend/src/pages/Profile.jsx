import { useEffect, useState } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";
import PlatformStatCard from "../components/PlatformStatCard";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState({
    full_name: user?.full_name || "",
    codeforces_handle: user?.codeforces_handle || "",
    leetcode_handle: user?.leetcode_handle || "",
    codechef_handle: user?.codechef_handle || "",
    github_username: user?.github_username || "",
  });
  const [saved, setSaved] = useState(false);
  const [stats, setStats] = useState(null);
  const [syncing, setSyncing] = useState(false);

  const loadStats = async (refresh = false) => {
    setSyncing(true);
    try {
      const { data } = await client.get("/api/profile/stats", { params: { refresh } });
      setStats(data);
    } finally {
      setSyncing(false);
    }
  };

  useEffect(() => {
    // Load whatever's cached on mount so the page isn't empty while typing.
    loadStats(false);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const { data } = await client.put("/api/profile", form);
    setUser(data);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    // This is the actual "sync": force a fresh fetch against whatever
    // handles were just saved, bypassing the cache.
    loadStats(true);
  };

  const field = (key, label, placeholder) => (
    <div>
      <label className="block text-sm text-muted mb-1">{label}</label>
      <input
        value={form[key]}
        placeholder={placeholder}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
        className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
      />
    </div>
  );

  const hasAnyHandle = form.codeforces_handle || form.leetcode_handle || form.codechef_handle;

  return (
    <div className="space-y-6 max-w-lg">
      <div>
        <h1 className="text-xl font-semibold">Profile</h1>
        <p className="text-sm text-muted mt-1">
          Link your platform handles so DevPulse can pull your live stats.
        </p>
      </div>

      <form onSubmit={submit} className="card p-5 space-y-4">
        {field("full_name", "Full name")}
        <div className="grid grid-cols-2 gap-3">
          {field("codeforces_handle", "Codeforces handle")}
          {field("leetcode_handle", "LeetCode handle")}
        </div>
        <div className="grid grid-cols-2 gap-3">
          {field("codechef_handle", "CodeChef handle")}
          {field("github_username", "GitHub username")}
        </div>
        <button type="submit" className="text-sm bg-amber text-ink rounded px-4 py-2 font-medium">
          Save & sync
        </button>
        {saved && <span className="text-xs text-signal ml-3">Saved. Syncing stats below...</span>}
      </form>

      {hasAnyHandle && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-medium text-paper">Synced stats</h2>
            <button
              onClick={() => loadStats(true)}
              disabled={syncing}
              className="text-xs font-mono border border-line rounded px-3 py-1.5 text-muted hover:text-paper hover:border-amber disabled:opacity-50"
            >
              {syncing ? "Syncing..." : "Sync now"}
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {form.codeforces_handle && (
              <PlatformStatCard platform="codeforces" stat={stats?.codeforces} loading={syncing && !stats} />
            )}
            {form.leetcode_handle && (
              <PlatformStatCard platform="leetcode" stat={stats?.leetcode} loading={syncing && !stats} />
            )}
            {form.codechef_handle && (
              <PlatformStatCard platform="codechef" stat={stats?.codechef} loading={syncing && !stats} />
            )}
          </div>
          <p className="text-xs text-muted mt-3">
            Stats are cached for a few minutes to avoid hammering each platform — use "Sync now" for a fresh pull.
          </p>
        </div>
      )}

      <div className="card p-5">
        <h2 className="text-sm font-medium text-paper mb-2">What's next</h2>
        <p className="text-sm text-muted">
          Your GitHub username is captured here for the activity-sync feature on the roadmap —
          once wired up, DevPulse will pull commit and PR activity automatically and use it,
          alongside your goals, projects and synced platform stats, to suggest what to focus on next.
        </p>
      </div>
    </div>
  );
}
