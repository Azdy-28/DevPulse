const platformColor = {
  codeforces: "text-signal",
  leetcode: "text-amber",
  codechef: "text-alert",
};

function timeUntil(iso) {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "started";
  const days = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  if (days > 0) return `${days}d ${hours}h`;
  const mins = Math.floor((diff % 3600000) / 60000);
  return `${hours}h ${mins}m`;
}

export default function ContestRow({ contest, onToggleBookmark }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-line last:border-0">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className={`font-mono text-xs uppercase ${platformColor[contest.platform] || "text-muted"}`}>
            {contest.platform}
          </span>
          <a
            href={contest.url}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-paper hover:text-amber truncate"
          >
            {contest.name}
          </a>
        </div>
        <div className="text-xs text-muted mt-1">
          {new Date(contest.start_time).toLocaleString()} · {contest.duration_minutes}min
        </div>
      </div>
      <div className="flex items-center gap-3 shrink-0 ml-4">
        <span className="mono-num text-sm text-muted">{timeUntil(contest.start_time)}</span>
        <button
          onClick={() => onToggleBookmark(contest)}
          className={`text-lg leading-none ${contest.is_bookmarked ? "text-amber" : "text-muted hover:text-paper"}`}
          title={contest.is_bookmarked ? "Remove bookmark" : "Bookmark"}
        >
          {contest.is_bookmarked ? "★" : "☆"}
        </button>
      </div>
    </div>
  );
}
