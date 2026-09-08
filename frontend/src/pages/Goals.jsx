import { useEffect, useState } from "react";
import client from "../api/client";

const statusColor = {
  not_started: "text-muted",
  in_progress: "text-amber",
  completed: "text-signal",
};

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", category: "general", description: "", target_date: "" });

  const load = async () => {
    const { data } = await client.get("/api/goals");
    setGoals(data);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = { ...form, target_date: form.target_date || null };
    await client.post("/api/goals", payload);
    setForm({ title: "", category: "general", description: "", target_date: "" });
    setShowForm(false);
    load();
  };

  const updateProgress = async (goal, progress) => {
    const status = progress >= 100 ? "completed" : progress > 0 ? "in_progress" : "not_started";
    await client.patch(`/api/goals/${goal.id}`, { progress, status });
    load();
  };

  const remove = async (id) => {
    await client.delete(`/api/goals/${id}`);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Goals</h1>
          <p className="text-sm text-muted mt-1">Targets you're working toward — DSA, roadmaps, interview prep.</p>
        </div>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="text-xs font-mono bg-amber text-ink rounded px-3 py-1.5"
        >
          {showForm ? "Cancel" : "New goal"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card p-5 space-y-3">
          <input
            required
            placeholder="Title (e.g. Improve DSA)"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
          />
          <div className="grid grid-cols-2 gap-3">
            <input
              placeholder="Category (e.g. dsa, system-design)"
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
            <input
              type="date"
              value={form.target_date}
              onChange={(e) => setForm({ ...form, target_date: e.target.value })}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>
          <textarea
            placeholder="Description (optional)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            rows={2}
          />
          <button type="submit" className="text-sm bg-amber text-ink rounded px-4 py-2 font-medium">
            Save goal
          </button>
        </form>
      )}

      <div className="space-y-3">
        {goals.length === 0 && !showForm && (
          <p className="text-sm text-muted">No goals yet. Create your first one above.</p>
        )}
        {goals.map((g) => (
          <div key={g.id} className="card p-5">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-medium text-paper">{g.title}</h3>
                  <span className={`text-xs font-mono ${statusColor[g.status]}`}>{g.status}</span>
                </div>
                <div className="text-xs text-muted mt-1">
                  {g.category}
                  {g.target_date ? ` · due ${g.target_date}` : ""}
                </div>
                {g.description && <p className="text-sm text-muted mt-2">{g.description}</p>}
              </div>
              <button onClick={() => remove(g.id)} className="text-xs text-muted hover:text-alert">
                Delete
              </button>
            </div>

            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-muted mb-1">
                <span>Progress</span>
                <span className="mono-num">{g.progress}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={g.progress}
                onChange={(e) => updateProgress(g, Number(e.target.value))}
                className="w-full accent-amber"
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
