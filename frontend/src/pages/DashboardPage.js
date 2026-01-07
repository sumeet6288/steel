import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Plus, FolderKanban } from 'lucide-react';
import { toast } from 'sonner';
import { formatDate } from '../lib/utils';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.getAll();
      setProjects(response.data);
    } catch (error) {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8" data-testid="dashboard-page">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-heading font-bold text-slate-900">Dashboard</h1>
            <p className="text-sm text-slate-600 mt-2">
              Manage your steel connection projects
            </p>
          </div>
          <Button
            onClick={() => navigate('/projects', { state: { openCreateDialog: true } })}
            className="bg-secondary text-white hover:bg-secondary/90 rounded-sm"
            data-testid="create-project-button"
          >
            <Plus size={18} className="mr-2" />
            New Project
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-600">Loading...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-sm p-12 text-center" data-testid="empty-state">
            <FolderKanban size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-xl font-heading font-semibold text-slate-900 mb-2">
              No Projects Yet
            </h3>
            <p className="text-slate-600 mb-6">
              Create your first project to start designing connections
            </p>
            <Button
              onClick={() => navigate('/projects', { state: { openCreateDialog: true } })}
              className="bg-slate-900 text-white hover:bg-slate-800 rounded-sm"
            >
              Create Project
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => navigate(`/projects/${project.id}`)}
                className="bg-white border border-slate-200 rounded-sm p-6 hover:bg-slate-50 cursor-pointer shadow-sm"
                data-testid={`project-card-${project.id}`}
              >
                <h3 className="text-xl font-heading font-semibold text-slate-900 mb-2">
                  {project.name}
                </h3>
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                  {project.description || 'No description'}
                </p>
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>{project.connection_count || 0} connections</span>
                  <span>{formatDate(project.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-sm">
          <p className="text-xs text-yellow-800">
            <strong>ENGINEERING DISCLAIMER:</strong> This is a design assist tool. All outputs require licensed engineer review and approval. Not for stamped drawings.
          </p>
        </div>
      </div>
    </div>
  );
};