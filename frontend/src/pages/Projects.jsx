import { useEffect, useState } from "react";
import client from "../api/client";

const statuses = ["planning", "active", "paused", "completed"];

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", tech_stack: "", status: "planning", repo_url: "" });

  const load = async () => {
    const { data } = await client.get("/api/projects");
    setProjects(data);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await client.post("/api/projects", form);
    setForm({ name: "", description: "", tech_stack: "", status: "planning", repo_url: "" });
    setShowForm(false);
    load();
  };

  const updateStatus = async (project, status) => {
    await client.patch(`/api/projects/${project.id}`, { status });
    load();
  };

  const remove = async (id) => {
    await client.delete(`/api/projects/${id}`);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Projects</h1>
          <p className="text-sm text-muted mt-1">What you're building, and where it stands.</p>
        </div>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="text-xs font-mono bg-amber text-ink rounded px-3 py-1.5"
        >
          {showForm ? "Cancel" : "New project"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={submit} className="card p-5 space-y-3">
          <input
            required
            placeholder="Project name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
          />
          <div className="grid grid-cols-2 gap-3">
            <input
              placeholder="Tech stack (comma separated)"
              value={form.tech_stack}
              onChange={(e) => setForm({ ...form, tech_stack: e.target.value })}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
            <input
              placeholder="Repo URL (optional)"
              value={form.repo_url}
              onChange={(e) => setForm({ ...form, repo_url: e.target.value })}
              className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            />
          </div>
          <textarea
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full bg-ink border border-line rounded px-3 py-2 text-sm focus:outline-none focus:border-amber"
            rows={2}
          />
          <button type="submit" className="text-sm bg-amber text-ink rounded px-4 py-2 font-medium">
            Save project
          </button>
        </form>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {projects.length === 0 && !showForm && (
          <p className="text-sm text-muted">No projects yet. Add your first one above.</p>
        )}
        {projects.map((p) => (
          <div key={p.id} className="card p-5">
            <div className="flex items-start justify-between">
              <h3 className="text-sm font-medium text-paper">{p.name}</h3>
              <button onClick={() => remove(p.id)} className="text-xs text-muted hover:text-alert">
                Delete
              </button>
            </div>
            {p.description && <p className="text-sm text-muted mt-2">{p.description}</p>}
            {p.tech_stack && <div className="text-xs font-mono text-muted mt-2">{p.tech_stack}</div>}
            {p.repo_url && (
              <a href={p.repo_url} target="_blank" rel="noreferrer" className="text-xs text-amber hover:underline mt-1 block">
                {p.repo_url}
              </a>
            )}
            <div className="flex gap-1 mt-4">
              {statuses.map((s) => (
                <button
                  key={s}
                  onClick={() => updateStatus(p, s)}
                  className={`text-xs font-mono px-2 py-1 rounded border ${
                    p.status === s ? "border-amber text-amber" : "border-line text-muted hover:text-paper"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
