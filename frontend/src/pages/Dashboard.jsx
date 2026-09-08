import { useEffect, useState } from "react";
import client from "../api/client";
import StatTile from "../components/StatTile";
import ContestRow from "../components/ContestRow";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const { data } = await client.get("/api/dashboard");
      setData(data);
    } catch {
      setError("Could not load dashboard data.");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const toggleBookmark = async (contest) => {
    if (contest.is_bookmarked) {
      const { data: bookmarks } = await client.get("/api/contests/bookmarks");
      const match = bookmarks.find((b) => b.platform === contest.platform && b.external_id === contest.external_id);
      if (match) await client.delete(`/api/contests/bookmarks/${match.id}`);
    } else {
      await client.post("/api/contests/bookmarks", {
        platform: contest.platform,
        external_id: contest.external_id,
        name: contest.name,
        start_time: contest.start_time,
        url: contest.url,
      });
    }
    load();
  };

  if (error) return <div className="text-alert text-sm">{error}</div>;
  if (!data) return <div className="text-muted text-sm">Loading...</div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold">
          Welcome back{data.user.full_name ? `, ${data.user.full_name.split(" ")[0]}` : ""}
        </h1>
        <p className="text-sm text-muted mt-1">Here's where things stand across your platforms.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatTile label="Goals in progress" value={data.stats.goals_in_progress} accent="text-amber" />
        <StatTile label="Goals completed" value={data.stats.goals_completed} accent="text-signal" />
        <StatTile label="Active projects" value={data.stats.active_projects} />
        <StatTile label="Activity (30d)" value={data.stats.activities_last_30_days} />
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 card p-5">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-sm font-medium text-paper">Upcoming contests</h2>
            <span className="text-xs text-muted">Codeforces · LeetCode · CodeChef</span>
          </div>
          {data.upcoming_contests.length === 0 ? (
            <p className="text-sm text-muted py-6">
              No upcoming contests found right now — this refreshes automatically every few minutes.
            </p>
          ) : (
            <div>
              {data.upcoming_contests.map((c) => (
                <ContestRow key={`${c.platform}-${c.external_id}`} contest={c} onToggleBookmark={toggleBookmark} />
              ))}
            </div>
          )}
        </div>

        <div className="card p-5">
          <h2 className="text-sm font-medium text-paper mb-3">Recent activity</h2>
          {data.recent_activity.length === 0 ? (
            <p className="text-sm text-muted">Nothing logged yet. Start tracking from the Goals or Projects page.</p>
          ) : (
            <ul className="space-y-3">
              {data.recent_activity.map((a) => (
                <li key={a.id} className="text-sm">
                  <div className="text-paper">{a.title}</div>
                  <div className="text-xs text-muted">
                    {a.type} · {new Date(a.occurred_at).toLocaleDateString()}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-5">
          <h2 className="text-sm font-medium text-paper mb-3">Goals</h2>
          {data.goals.length === 0 ? (
            <p className="text-sm text-muted">No goals yet. Set one on the Goals page.</p>
          ) : (
            <ul className="space-y-3">
              {data.goals.slice(0, 5).map((g) => (
                <li key={g.id}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-paper">{g.title}</span>
                    <span className="mono-num text-xs text-muted">{g.progress}%</span>
                  </div>
                  <div className="h-1.5 bg-panel2 rounded-full mt-1 overflow-hidden">
                    <div className="h-full bg-amber" style={{ width: `${g.progress}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="card p-5">
          <h2 className="text-sm font-medium text-paper mb-3">Projects</h2>
          {data.projects.length === 0 ? (
            <p className="text-sm text-muted">No projects yet. Add one on the Projects page.</p>
          ) : (
            <ul className="space-y-3">
              {data.projects.slice(0, 5).map((p) => (
                <li key={p.id} className="text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-paper">{p.name}</span>
                    <span className="text-xs font-mono text-muted uppercase">{p.status}</span>
                  </div>
                  {p.tech_stack && <div className="text-xs text-muted mt-0.5">{p.tech_stack}</div>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
