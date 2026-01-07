import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { auditAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { FileText, Sparkles, CheckCircle2, Upload, Download, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import { formatDateTime } from '../lib/utils';

const ACTION_ICONS = {
  CREATE_CONNECTION: CheckCircle2,
  UPDATE_CONNECTION: CheckCircle2,
  VALIDATE_CONNECTION: CheckCircle2,
  RULE_CHECK: AlertTriangle,
  AI_REDLINE: Sparkles,
  USER_APPROVAL: CheckCircle2,
  EXPORT_TEKLA: Download,
};

const ACTION_LABELS = {
  CREATE_CONNECTION: 'Created Connection',
  UPDATE_CONNECTION: 'Updated Connection',
  VALIDATE_CONNECTION: 'Validated Connection',
  RULE_CHECK: 'Rule Check',
  AI_REDLINE: 'AI Redline Interpretation',
  USER_APPROVAL: 'User Approval',
  EXPORT_TEKLA: 'Exported to Tekla',
};

const ACTION_COLORS = {
  CREATE_CONNECTION: 'text-green-700 bg-green-50 border-green-200',
  UPDATE_CONNECTION: 'text-blue-700 bg-blue-50 border-blue-200',
  VALIDATE_CONNECTION: 'text-purple-700 bg-purple-50 border-purple-200',
  RULE_CHECK: 'text-yellow-700 bg-yellow-50 border-yellow-200',
  AI_REDLINE: 'text-purple-700 bg-purple-50 border-purple-200',
  USER_APPROVAL: 'text-green-700 bg-green-50 border-green-200',
  EXPORT_TEKLA: 'text-blue-700 bg-blue-50 border-blue-200',
};

export const AuditLogPage = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(50);

  useEffect(() => {
    loadAuditLogs();
  }, [limit]);

  const loadAuditLogs = async () => {
    try {
      const response = await auditAPI.getMyActivity(limit);
      setLogs(response.data);
    } catch (error) {
      toast.error('Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action) => {
    const Icon = ACTION_ICONS[action] || FileText;
    return Icon;
  };

  const getActionLabel = (action) => {
    return ACTION_LABELS[action] || action;
  };

  const getActionColor = (action) => {
    return ACTION_COLORS[action] || 'text-slate-700 bg-slate-50 border-slate-200';
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <p className="text-slate-600">Loading audit logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="audit-log-page">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-heading font-bold text-slate-900">Audit Log</h1>
          <p className="text-sm text-slate-600 mt-2">
            Complete activity history and compliance tracking
          </p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Activity History</CardTitle>
                <CardDescription>
                  All actions performed on connections and projects
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-600">Show:</span>
                <select
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  className="text-sm border border-slate-200 rounded-sm px-2 py-1"
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
                <span className="text-xs text-slate-600">entries</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {logs.length === 0 ? (
              <div className="text-center py-12">
                <FileText size={48} className="mx-auto text-slate-300 mb-4" />
                <h3 className="text-xl font-heading font-semibold text-slate-900 mb-2">
                  No Audit Logs Yet
                </h3>
                <p className="text-slate-600">
                  Activity logs will appear here as you work on connections
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[180px]">Timestamp</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Connection</TableHead>
                      <TableHead>Details</TableHead>
                      <TableHead className="text-center w-[100px]">AI Involved</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.map((log) => {
                      const Icon = getActionIcon(log.action);
                      return (
                        <TableRow key={log.id} className="hover:bg-slate-50">
                          <TableCell className="text-xs text-slate-600">
                            {formatDateTime(log.timestamp)}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Icon size={16} className="text-slate-400" />
                              <Badge className={`text-xs ${getActionColor(log.action)}`}>
                                {getActionLabel(log.action)}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell>
                            {log.connection_id ? (
                              <Button
                                variant="link"
                                size="sm"
                                onClick={() => navigate(`/connections/${log.connection_id}`)}
                                className="text-blue-600 hover:text-blue-700 p-0 h-auto"
                              >
                                View Connection
                              </Button>
                            ) : (
                              <span className="text-xs text-slate-400">-</span>
                            )}
                          </TableCell>
                          <TableCell>
                            {log.details && Object.keys(log.details).length > 0 ? (
                              <div className="text-xs text-slate-600 max-w-md">
                                {renderDetails(log.details)}
                              </div>
                            ) : (
                              <span className="text-xs text-slate-400">-</span>
                            )}
                          </TableCell>
                          <TableCell className="text-center">
                            {log.ai_involved ? (
                              <Badge className="text-xs bg-purple-50 text-purple-700 border-purple-200">
                                <Sparkles size={12} className="mr-1" />
                                AI
                              </Badge>
                            ) : (
                              <span className="text-xs text-slate-400">-</span>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-600">Total Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{logs.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-600">AI-Assisted Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-700">
                {logs.filter(log => log.ai_involved).length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-600">Validation Checks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-700">
                {logs.filter(log => log.action === 'VALIDATE_CONNECTION' || log.action === 'RULE_CHECK').length}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-sm">
          <p className="text-xs text-blue-800">
            <strong>COMPLIANCE NOTE:</strong> All audit logs are permanently recorded for traceability and regulatory compliance. Logs include timestamps, user actions, and AI assistance indicators.
          </p>
        </div>
      </div>
    </div>
  );
};

// Helper function to render log details
function renderDetails(details) {
  if (typeof details === 'string') {
    return details;
  }

  const importantKeys = ['connection_type', 'is_valid', 'rule_result', 'ai_confidence', 'export_format', 'human_approved'];
  const entries = Object.entries(details)
    .filter(([key]) => importantKeys.includes(key))
    .slice(0, 3);

  if (entries.length === 0) {
    return JSON.stringify(details).slice(0, 100);
  }

  return (
    <div className="space-y-1">
      {entries.map(([key, value]) => (
        <div key={key}>
          <span className="font-medium">{key.replace(/_/g, ' ')}:</span>{' '}
          <span>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</span>
        </div>
      ))}
    </div>
  );
}
