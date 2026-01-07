import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI, connectionsAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, Plus, Zap, Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { formatDate, getConnectionTypeLabel, getConnectionStatusColor } from '../lib/utils';

export const ProjectDetailPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    connection_type: 'beam_to_column_shear',
    description: ''
  });

  const loadData = useCallback(async () => {
    try {
      const [projectRes, connectionsRes] = await Promise.all([
        projectsAPI.getById(projectId),
        connectionsAPI.getAll(projectId)
      ]);
      setProject(projectRes.data);
      setConnections(connectionsRes.data);
    } catch (error) {
      toast.error('Failed to load project details');
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  }, [projectId, navigate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreateConnection = async (e) => {
    e.preventDefault();
    try {
      const response = await connectionsAPI.create({
        ...formData,
        project_id: projectId,
        parameters: {}
      });
      toast.success('Connection created successfully');
      setIsCreateOpen(false);
      setFormData({ name: '', connection_type: 'beam_to_column_shear', description: '' });
      navigate(`/connections/${response.data.id}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create connection');
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <p className="text-slate-600">Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="project-detail-page">
      <div className="max-w-7xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate('/projects')}
          className="mb-6 text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back to Projects
        </Button>

        <div className="bg-white border border-slate-200 rounded-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-heading font-bold text-slate-900 mb-2">
                {project.name}
              </h1>
              {project.location && (
                <p className="text-sm text-slate-600 mb-2">
                  <span className="font-medium">Location:</span> {project.location}
                </p>
              )}
              {project.description && (
                <p className="text-sm text-slate-600 mb-4">{project.description}</p>
              )}
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span>Created: {formatDate(project.created_at)}</span>
                <span>•</span>
                <span>{project.connection_count || 0} connections</span>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/projects`)}
              className="text-slate-600"
            >
              <Pencil size={16} className="mr-2" />
              Edit Project
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-heading font-bold text-slate-900">Connections</h2>
          <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
            <DialogTrigger asChild>
              <Button className="bg-secondary text-white hover:bg-secondary/90 rounded-sm">
                <Plus size={18} className="mr-2" />
                New Connection
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <form onSubmit={handleCreateConnection}>
                <DialogHeader>
                  <DialogTitle>Create New Connection</DialogTitle>
                  <DialogDescription>
                    Add a new steel connection to this project.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="conn-name">Connection Name *</Label>
                    <Input
                      id="conn-name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., B1-C2 Connection"
                      required
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="conn-type">Connection Type *</Label>
                    <Select
                      value={formData.connection_type}
                      onValueChange={(value) => setFormData({ ...formData, connection_type: value })}
                    >
                      <SelectTrigger id="conn-type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beam_to_column_shear">Beam-to-Column Shear</SelectItem>
                        <SelectItem value="beam_to_beam_shear">Beam-to-Beam Shear</SelectItem>
                        <SelectItem value="single_plate">Single Plate</SelectItem>
                        <SelectItem value="double_angle">Double Angle</SelectItem>
                        <SelectItem value="end_plate">End Plate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="conn-desc">Description</Label>
                    <Input
                      id="conn-desc"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Connection details..."
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="submit" className="bg-slate-900 text-white hover:bg-slate-800">
                    Create Connection
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {connections.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-sm p-12 text-center">
            <Zap size={48} className="mx-auto text-slate-300 mb-4" />
            <h3 className="text-xl font-heading font-semibold text-slate-900 mb-2">
              No Connections Yet
            </h3>
            <p className="text-slate-600 mb-6">
              Add your first connection to this project
            </p>
            <Button
              onClick={() => setIsCreateOpen(true)}
              className="bg-slate-900 text-white hover:bg-slate-800 rounded-sm"
            >
              Create Connection
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {connections.map((connection) => (
              <div
                key={connection.id}
                onClick={() => navigate(`/connections/${connection.id}`)}
                className="bg-white border border-slate-200 rounded-sm p-5 hover:bg-slate-50 cursor-pointer transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-heading font-semibold text-slate-900">
                    {connection.name}
                  </h3>
                  <Badge className={`text-xs ${getConnectionStatusColor(connection.status)}`}>
                    {connection.status}
                  </Badge>
                </div>
                <p className="text-sm text-slate-600 mb-3">
                  {getConnectionTypeLabel(connection.connection_type)}
                </p>
                {connection.description && (
                  <p className="text-xs text-slate-500 mb-3 line-clamp-2">
                    {connection.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Created {formatDate(connection.created_at)}</span>
                  {connection.ai_suggested && (
                    <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                      AI Suggested
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-sm">
          <p className="text-xs text-yellow-800">
            <strong>ENGINEERING DISCLAIMER:</strong> All connections require licensed engineer review and approval before fabrication.
          </p>
        </div>
      </div>
    </div>
  );
};