import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { projectsAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Plus, Pencil, Trash2, FolderKanban } from 'lucide-react';
import { toast } from 'sonner';
import { formatDate } from '../lib/utils';

export const ProjectsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    location: ''
  });

  useEffect(() => {
    loadProjects();
    // Check if we should open create dialog
    if (location.state?.openCreateDialog) {
      setIsCreateOpen(true);
      // Clear the state
      navigate(location.pathname, { replace: true, state: {} });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

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

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await projectsAPI.create(formData);
      toast.success('Project created successfully');
      setIsCreateOpen(false);
      setFormData({ name: '', description: '', location: '' });
      loadProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleEdit = async (e) => {
    e.preventDefault();
    try {
      await projectsAPI.update(editingProject.id, formData);
      toast.success('Project updated successfully');
      setIsEditOpen(false);
      setEditingProject(null);
      setFormData({ name: '', description: '', location: '' });
      loadProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update project');
    }
  };

  const handleDelete = async (project) => {
    if (!window.confirm(`Delete project "${project.name}"? This will also delete all connections.`)) return;
    
    try {
      await projectsAPI.delete(project.id);
      toast.success('Project deleted successfully');
      loadProjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete project');
    }
  };

  const openEditDialog = (project) => {
    setEditingProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      location: project.location || ''
    });
    setIsEditOpen(true);
  };

  return (
    <div className="p-8" data-testid="projects-page">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-heading font-bold text-slate-900">Projects</h1>
            <p className="text-sm text-slate-600 mt-2">
              Manage your steel connection projects
            </p>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-secondary text-white hover:bg-secondary/90 rounded-sm">
                <Plus size={18} className="mr-2" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <form onSubmit={handleCreate}>
                <DialogHeader>
                  <DialogTitle>Create New Project</DialogTitle>
                  <DialogDescription>
                    Add a new steel connection project to your workspace.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Project Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Office Building Connections"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      placeholder="e.g., Houston, TX"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Project details..."
                      rows={3}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" className="bg-slate-900 text-white hover:bg-slate-800">
                    Create Project
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-600">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-sm p-12 text-center">
            <FolderKanban size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-xl font-heading font-semibold text-slate-900 mb-2">
              No Projects Yet
            </h3>
            <p className="text-slate-600 mb-6">
              Create your first project to start designing connections
            </p>
            <Button
              onClick={() => setIsCreateOpen(true)}
              className="bg-slate-900 text-white hover:bg-slate-800 rounded-sm"
            >
              Create Project
            </Button>
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                      Project Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                      Connections
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-600 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {projects.map((project) => (
                    <tr
                      key={project.id}
                      className="hover:bg-slate-50 cursor-pointer"
                      onClick={() => navigate(`/projects/${project.id}`)}
                    >
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-slate-900">{project.name}</div>
                          {project.description && (
                            <div className="text-xs text-slate-500 mt-1 line-clamp-1">
                              {project.description}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {project.location || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {project.connection_count || 0}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {formatDate(project.created_at)}
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              openEditDialog(project);
                            }}
                            className="text-slate-600 hover:text-slate-900"
                          >
                            <Pencil size={16} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(project);
                            }}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 size={16} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Edit Dialog */}
        <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <form onSubmit={handleEdit}>
              <DialogHeader>
                <DialogTitle>Edit Project</DialogTitle>
                <DialogDescription>
                  Update project details
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="edit-name">Project Name *</Label>
                  <Input
                    id="edit-name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="edit-location">Location</Label>
                  <Input
                    id="edit-location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="edit-description">Description</Label>
                  <Textarea
                    id="edit-description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" className="bg-slate-900 text-white hover:bg-slate-800">
                  Update Project
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-sm">
          <p className="text-xs text-yellow-800">
            <strong>ENGINEERING DISCLAIMER:</strong> This is a design assist tool. All outputs require licensed engineer review and approval. Not for stamped drawings.
          </p>
        </div>
      </div>
    </div>
  );
};