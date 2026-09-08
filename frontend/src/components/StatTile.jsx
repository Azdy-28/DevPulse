export default function StatTile({ label, value, accent = "text-paper" }) {
  return (
    <div className="card px-4 py-3">
      <div className={`mono-num text-2xl font-semibold ${accent}`}>{value}</div>
      <div className="text-xs text-muted mt-1">{label}</div>
    </div>
  );
}
