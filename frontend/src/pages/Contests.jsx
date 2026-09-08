import { useEffect, useState } from "react";
import client from "../api/client";
import ContestRow from "../components/ContestRow";

export default function Contests() {
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const load = async (refresh = false) => {
    setLoading(true);
    const { data } = await client.get("/api/contests", { params: { refresh } });
    setContests(data);
    setLoading(false);
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

  const visible = contests.filter((c) => filter === "all" || c.platform === filter);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Contests</h1>
          <p className="text-sm text-muted mt-1">Aggregated across Codeforces, LeetCode and CodeChef.</p>
        </div>
        <button
          onClick={() => load(true)}
          className="text-xs font-mono border border-line rounded px-3 py-1.5 text-muted hover:text-paper hover:border-amber"
        >
          Refresh now
        </button>
      </div>

      <div className="flex gap-2">
        {["all", "codeforces", "leetcode", "codechef"].map((p) => (
          <button
            key={p}
            onClick={() => setFilter(p)}
            className={`text-xs font-mono px-3 py-1.5 rounded border ${
              filter === p ? "border-amber text-amber" : "border-line text-muted hover:text-paper"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      <div className="card p-5">
        {loading ? (
          <p className="text-sm text-muted py-6">Loading...</p>
        ) : visible.length === 0 ? (
          <p className="text-sm text-muted py-6">
            No contests found for this filter. External platforms may be rate-limiting or
            temporarily unreachable — try "Refresh now" in a minute.
          </p>
        ) : (
          visible.map((c) => (
            <ContestRow key={`${c.platform}-${c.external_id}`} contest={c} onToggleBookmark={toggleBookmark} />
          ))
        )}
      </div>
    </div>
  );
}
