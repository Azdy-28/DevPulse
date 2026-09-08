const platformLabel = {
  codeforces: "Codeforces",
  leetcode: "LeetCode",
  codechef: "CodeChef",
};

export default function PlatformStatCard({ platform, stat, loading }) {
  if (!stat && !loading) return null;

  return (
    <div className="card p-4">
      <div className="text-xs font-mono uppercase text-muted mb-2">{platformLabel[platform]}</div>
      {loading ? (
        <div className="text-sm text-muted">Syncing...</div>
      ) : stat.error ? (
        <div className="text-sm text-alert">{stat.error}</div>
      ) : (
        <div className="space-y-1">
          <div className="text-sm text-paper">@{stat.handle}</div>
          <div className="flex gap-4 mt-2">
            {stat.rating != null && (
              <div>
                <div className="mono-num text-lg text-amber">{stat.rating}</div>
                <div className="text-xs text-muted">rating</div>
              </div>
            )}
            {stat.rank != null && (
              <div>
                <div className="mono-num text-lg text-signal">{stat.rank}</div>
                <div className="text-xs text-muted">rank</div>
              </div>
            )}
            {stat.solved != null && (
              <div>
                <div className="mono-num text-lg text-paper">{stat.solved}</div>
                <div className="text-xs text-muted">solved</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
