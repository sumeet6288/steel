import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { connectionsAPI, redlinesAPI, aiAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowLeft, CheckCircle2, XCircle, AlertTriangle, Upload, Download, Sparkles, FileText } from 'lucide-react';
import { toast } from 'sonner';
import { formatDateTime, getConnectionTypeLabel, getConnectionStatusColor, getRuleStatusColor } from '../lib/utils';

export const ConnectionDesignerPage = () => {
  const { connectionId } = useParams();
  const navigate = useNavigate();
  const [connection, setConnection] = useState(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [redlines, setRedlines] = useState([]);
  const [parameters, setParameters] = useState({});
  const [validationResults, setValidationResults] = useState(null);
  const [uploadingRedline, setUploadingRedline] = useState(false);
  const [interpretingRedline, setInterpretingRedline] = useState(null);

  const loadConnection = useCallback(async () => {
    try {
      const response = await connectionsAPI.getById(connectionId);
      setConnection(response.data);
      setParameters(response.data.parameters || {});
      if (response.data.validation_results) {
        setValidationResults(response.data.validation_results);
      }
    } catch (error) {
      toast.error('Failed to load connection');
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  }, [connectionId, navigate]);

  const loadRedlines = useCallback(async () => {
    try {
      const response = await redlinesAPI.getByConnection(connectionId);
      setRedlines(response.data);
    } catch (error) {
      console.error('Failed to load redlines:', error);
    }
  }, [connectionId]);

  useEffect(() => {
    loadConnection();
    loadRedlines();
  }, [loadConnection, loadRedlines]);

  const handleParameterChange = (key, value) => {
    setParameters({ ...parameters, [key]: value });
  };

  const handleSaveParameters = async () => {
    try {
      const response = await connectionsAPI.update(connectionId, { parameters });
      toast.success('Parameters saved successfully ✓');
      // Reload to get updated connection data
      await loadConnection();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Failed to save parameters';
      toast.error(errorMsg);
      console.error('Save parameters error:', error);
    }
  };

  const handleValidate = async () => {
    setValidating(true);
    try {
      const response = await connectionsAPI.validate(connectionId);
      
      // The backend returns {status, rule_validation, geometry_validation, geometry}
      const validationData = response.data;
      
      // Set validation results properly
      setValidationResults(validationData);
      
      if (validationData.status === 'validated') {
        toast.success('Connection validated successfully! ✓');
      } else if (validationData.status === 'failed') {
        const failedChecks = validationData.rule_validation?.checks?.filter(c => c.status === 'FAIL').length || 0;
        toast.error(`Validation failed: ${failedChecks} rule(s) not met`);
      } else {
        toast.warning('Validation completed with warnings');
      }
      
      // Reload connection to get updated status and geometry
      await loadConnection();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Validation failed';
      toast.error(errorMsg);
      console.error('Validation error:', error);
    } finally {
      setValidating(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const response = await connectionsAPI.exportTekla(connectionId);
      
      // Create downloadable file
      const teklaData = response.data.tekla_export || response.data;
      const blob = new Blob([JSON.stringify(teklaData, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${connection.name.replace(/\s+/g, '_')}_tekla_export.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      toast.success('Exported to Tekla format ✓');
      await loadConnection();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Export failed';
      toast.error(errorMsg);
      console.error('Export error:', error);
    } finally {
      setExporting(false);
    }
  };

  const handleRedlineUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingRedline(true);
    try {
      const response = await redlinesAPI.upload(connectionId, file);
      toast.success('Redline uploaded successfully ✓');
      await loadRedlines();
      
      // Auto-interpret after upload
      if (response.data && response.data.redline_id) {
        await handleInterpretRedline(response.data.redline_id);
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Failed to upload redline';
      toast.error(errorMsg);
      console.error('Redline upload error:', error);
    } finally {
      setUploadingRedline(false);
    }
  };

  const handleInterpretRedline = async (redlineId) => {
    setInterpretingRedline(redlineId);
    try {
      const response = await redlinesAPI.interpret(redlineId);
      toast.success('AI interpretation complete ✓');
      await loadRedlines();
      
      // Show AI suggestions
      if (response.data && response.data.ai_extraction && response.data.ai_extraction.parameters) {
        const paramCount = Object.keys(response.data.ai_extraction.parameters).length;
        if (paramCount > 0) {
          toast.info(`AI suggested ${paramCount} parameter change(s). Review in Redlines tab.`);
        }
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'AI interpretation failed';
      toast.error(errorMsg);
      console.error('AI interpretation error:', error);
    } finally {
      setInterpretingRedline(null);
    }
  };

  const handleApproveRedline = async (redlineId, suggestedParams) => {
    try {
      await redlinesAPI.approve(redlineId, suggestedParams);
      toast.success('Changes approved and applied to connection ✓');
      await loadConnection();
      await loadRedlines();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || 'Failed to apply changes';
      toast.error(errorMsg);
      console.error('Approve redline error:', error);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <p className="text-slate-600">Loading connection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="connection-designer-page">
      <div className="max-w-7xl mx-auto">
        <Button
          variant="ghost"
          onClick={() => navigate(`/projects/${connection.project_id}`)}
          className="mb-6 text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back to Project
        </Button>

        {/* Header */}
        <div className="bg-white border border-slate-200 rounded-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-heading font-bold text-slate-900">
                  {connection.name}
                </h1>
                <Badge className={`${getConnectionStatusColor(connection.status)}`}>
                  {connection.status}
                </Badge>
                {connection.ai_suggested && (
                  <Badge className="bg-purple-50 text-purple-700 border-purple-200">
                    <Sparkles size={12} className="mr-1" />
                    AI Suggested
                  </Badge>
                )}
              </div>
              <p className="text-sm text-slate-600 mb-2">
                {getConnectionTypeLabel(connection.connection_type)}
              </p>
              {connection.description && (
                <p className="text-sm text-slate-500">{connection.description}</p>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleValidate}
                disabled={validating}
                className="bg-blue-600 text-white hover:bg-blue-700"
              >
                <CheckCircle2 size={18} className="mr-2" />
                {validating ? 'Validating...' : 'Validate'}
              </Button>
              <Button
                onClick={handleExport}
                disabled={exporting || connection.status !== 'validated'}
                className="bg-green-600 text-white hover:bg-green-700"
              >
                <Download size={18} className="mr-2" />
                {exporting ? 'Exporting...' : 'Export Tekla'}
              </Button>
            </div>
          </div>
        </div>

        <Tabs defaultValue="parameters" className="space-y-6">
          <TabsList>
            <TabsTrigger value="parameters">Parameters</TabsTrigger>
            <TabsTrigger value="validation">Validation Results</TabsTrigger>
            <TabsTrigger value="redlines">
              Redlines
              {redlines.length > 0 && (
                <Badge className="ml-2 bg-blue-100 text-blue-700">{redlines.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="geometry">Geometry</TabsTrigger>
          </TabsList>

          {/* Parameters Tab */}
          <TabsContent value="parameters">
            <Card>
              <CardHeader>
                <CardTitle>Connection Parameters</CardTitle>
                <CardDescription>
                  Enter the design parameters for this {getConnectionTypeLabel(connection.connection_type)} connection. All fields marked with * are required.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {getParameterFields(connection.connection_type).map((field) => (
                    <div key={field.key} className="grid gap-2">
                      <Label htmlFor={field.key} className="text-sm font-medium">
                        {field.label}
                        {field.required && <span className="text-red-500 ml-1">*</span>}
                      </Label>
                      <Input
                        id={field.key}
                        type="number"
                        step={field.step || '0.1'}
                        value={parameters[field.key] || ''}
                        onChange={(e) => handleParameterChange(field.key, parseFloat(e.target.value) || '')}
                        placeholder={field.placeholder}
                        className={`${!parameters[field.key] && field.required ? 'border-orange-300' : ''}`}
                      />
                      <div className="flex items-center justify-between">
                        {field.unit && (
                          <span className="text-xs text-slate-500">{field.unit}</span>
                        )}
                        {!parameters[field.key] && field.required && (
                          <span className="text-xs text-orange-600">Required field</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Parameter validation status */}
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-sm">
                  <div className="text-xs text-blue-800">
                    <strong>💡 Tip:</strong> Fill in all required parameters (*) before running validation. AISC 360-16 checks require complete parameter sets.
                  </div>
                </div>

                <div className="mt-6 flex items-center justify-between">
                  <div className="text-xs text-slate-600">
                    {Object.keys(parameters).length} parameter(s) entered
                  </div>
                  <Button 
                    onClick={handleSaveParameters} 
                    className="bg-slate-900 text-white hover:bg-slate-800"
                    disabled={Object.keys(parameters).length === 0}
                  >
                    <CheckCircle2 size={16} className="mr-2" />
                    Save Parameters
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Validation Results Tab */}
          <TabsContent value="validation">
            <Card>
              <CardHeader>
                <CardTitle>Validation Results</CardTitle>
                <CardDescription>
                  AISC 360-16 rule checks and validation status
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!validationResults ? (
                  <Alert className="bg-slate-50 border-slate-200">
                    <AlertTriangle className="h-4 w-4 text-slate-600" />
                    <AlertDescription className="text-slate-700">
                      Connection has not been validated yet. Click &quot;Validate&quot; button above to run AISC 360-16 checks.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="space-y-4">
                    {/* Overall Status */}
                    <div className={`p-4 rounded-sm border ${
                      validationResults.status === 'validated' 
                        ? 'bg-green-50 border-green-200' 
                        : validationResults.status === 'failed'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-orange-50 border-orange-200'
                    }`}>
                      <div className="flex items-center gap-2 mb-2">
                        {validationResults.status === 'validated' ? (
                          <CheckCircle2 className="text-green-700" size={20} />
                        ) : (
                          <XCircle className="text-red-700" size={20} />
                        )}
                        <span className="font-semibold text-sm">
                          {validationResults.status === 'validated' 
                            ? 'Connection Validated - Meets AISC 360-16 Requirements' 
                            : 'Validation Failed - Does Not Meet Requirements'}
                        </span>
                      </div>
                      {validationResults.rule_validation?.summary && (
                        <p className="text-sm text-slate-700 mt-2">{validationResults.rule_validation.summary}</p>
                      )}
                    </div>

                    {/* Rule Checks */}
                    {validationResults.rule_validation?.checks && validationResults.rule_validation.checks.length > 0 && (
                      <div className="space-y-3">
                        <h3 className="font-semibold text-sm text-slate-900 mb-3">
                          AISC 360-16 Rule Checks ({validationResults.rule_validation.checks.length} total)
                        </h3>
                        {validationResults.rule_validation.checks.map((check, idx) => (
                          <div
                            key={idx}
                            className={`p-3 rounded-sm border text-sm ${getRuleStatusColor(check.status)}`}
                          >
                            <div className="flex items-start justify-between mb-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-medium">{check.rule_name}</span>
                                  <Badge className={`text-xs ${
                                    check.status === 'PASS' ? 'bg-green-100 text-green-700' :
                                    check.status === 'FAIL' ? 'bg-red-100 text-red-700' :
                                    'bg-orange-100 text-orange-700'
                                  }`}>
                                    {check.status}
                                  </Badge>
                                </div>
                                <div className="text-xs mt-1 text-slate-600">{check.message}</div>
                                {check.code_reference && (
                                  <div className="text-xs mt-1 font-mono text-slate-500">
                                    📖 {check.code_reference}
                                  </div>
                                )}
                                {(check.calculated_value !== undefined && check.limit_value !== undefined) && (
                                  <div className="text-xs mt-2 flex gap-4">
                                    <span>Calculated: <strong>{check.calculated_value.toFixed(2)}</strong></span>
                                    <span>Limit: <strong>{check.limit_value.toFixed(2)}</strong></span>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Geometry Validation */}
                    {validationResults.geometry_validation && (
                      <div className="p-4 bg-slate-50 border border-slate-200 rounded-sm">
                        <h3 className="font-semibold text-sm text-slate-900 mb-2">Geometry Validation</h3>
                        <div className="text-sm text-slate-700">
                          <div className="flex items-center gap-2 mb-2">
                            {validationResults.geometry_validation.is_valid ? (
                              <CheckCircle2 className="text-green-600" size={16} />
                            ) : (
                              <XCircle className="text-red-600" size={16} />
                            )}
                            <span>
                              {validationResults.geometry_validation.is_valid 
                                ? 'Geometry is valid' 
                                : 'Geometry has issues'}
                            </span>
                          </div>
                          {validationResults.geometry_validation.issues?.length > 0 && (
                            <div className="mt-2">
                              <strong className="text-xs">Issues:</strong>
                              <ul className="list-disc list-inside text-xs mt-1">
                                {validationResults.geometry_validation.issues.map((issue, i) => (
                                  <li key={i} className="text-red-700">{issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {validationResults.geometry_validation.warnings?.length > 0 && (
                            <div className="mt-2">
                              <strong className="text-xs">Warnings:</strong>
                              <ul className="list-disc list-inside text-xs mt-1">
                                {validationResults.geometry_validation.warnings.map((warning, i) => (
                                  <li key={i} className="text-orange-700">{warning}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Redlines Tab */}
          <TabsContent value="redlines">
            <Card>
              <CardHeader>
                <CardTitle>Redline Markups</CardTitle>
                <CardDescription>
                  Upload redline drawings for AI interpretation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6">
                  <Label
                    htmlFor="redline-upload"
                    className="flex items-center justify-center w-full h-32 border-2 border-dashed border-slate-300 rounded-sm hover:border-slate-400 cursor-pointer bg-slate-50 hover:bg-slate-100 transition-colors"
                  >
                    {uploadingRedline ? (
                      <span className="text-sm text-slate-600">Uploading...</span>
                    ) : (
                      <div className="text-center">
                        <Upload className="mx-auto mb-2 text-slate-400" size={32} />
                        <span className="text-sm text-slate-600">
                          Click to upload redline drawing
                        </span>
                        <span className="text-xs text-slate-500 block mt-1">
                          PDF, PNG, JPG supported
                        </span>
                      </div>
                    )}
                  </Label>
                  <input
                    id="redline-upload"
                    type="file"
                    className="hidden"
                    accept="image/*,.pdf"
                    onChange={handleRedlineUpload}
                    disabled={uploadingRedline}
                  />
                </div>

                {redlines.length === 0 ? (
                  <Alert>
                    <FileText className="h-4 w-4" />
                    <AlertDescription>
                      No redlines uploaded yet. Upload a marked-up drawing for AI interpretation.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="space-y-4">
                    {redlines.map((redline) => (
                      <div key={redline.id} className="border border-slate-200 rounded-sm p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <div className="font-medium text-sm">{redline.file_name}</div>
                            <div className="text-xs text-slate-500 mt-1">
                              Uploaded {formatDateTime(redline.created_at)}
                            </div>
                          </div>
                          <Badge className={getConnectionStatusColor(redline.status)}>
                            {redline.status}
                          </Badge>
                        </div>

                        {redline.ai_extraction && (
                          <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-sm">
                            <div className="flex items-center gap-2 mb-2">
                              <Sparkles className="text-purple-700" size={16} />
                              <span className="font-semibold text-sm text-purple-900">
                                AI Interpretation
                              </span>
                              <Badge className="ml-auto text-xs">
                                {Math.round(redline.ai_extraction.confidence * 100)}% confidence
                              </Badge>
                            </div>
                            <div className="text-sm text-purple-900 mb-2">
                              <strong>Intent:</strong> {redline.ai_extraction.intent}
                            </div>
                            {redline.ai_extraction.reasoning && (
                              <div className="text-xs text-purple-800 mb-3">
                                {redline.ai_extraction.reasoning}
                              </div>
                            )}
                            {Object.keys(redline.ai_extraction.parameters).length > 0 && (
                              <div className="mb-3">
                                <div className="text-xs font-medium text-purple-900 mb-2">
                                  Suggested Parameter Changes:
                                </div>
                                <div className="bg-white rounded p-2 text-xs">
                                  {Object.entries(redline.ai_extraction.parameters).map(([key, value]) => (
                                    <div key={key} className="flex justify-between py-1">
                                      <span className="font-medium">{key}:</span>
                                      <span>{value}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            {redline.status === 'extracted' && (
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  onClick={() => handleApproveRedline(redline.id, redline.ai_extraction.parameters)}
                                  className="bg-green-600 text-white hover:bg-green-700"
                                >
                                  Approve & Apply
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="text-slate-600"
                                >
                                  Reject
                                </Button>
                              </div>
                            )}
                          </div>
                        )}

                        {redline.status === 'uploaded' && (
                          <Button
                            size="sm"
                            onClick={() => handleInterpretRedline(redline.id)}
                            disabled={interpretingRedline === redline.id}
                            className="mt-3"
                          >
                            <Sparkles size={16} className="mr-2" />
                            {interpretingRedline === redline.id ? 'Interpreting...' : 'AI Interpret'}
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <Alert className="mt-6 bg-blue-50 border-blue-200">
                  <AlertTriangle className="h-4 w-4 text-blue-700" />
                  <AlertDescription className="text-blue-800 text-xs">
                    <strong>ADVISORY:</strong> AI interpretation is for assistance only. All changes require engineer approval.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Geometry Tab */}
          <TabsContent value="geometry">
            <Card>
              <CardHeader>
                <CardTitle>Connection Geometry</CardTitle>
                <CardDescription>
                  3D geometry model and component details
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!connection.geometry ? (
                  <Alert className="bg-slate-50 border-slate-200">
                    <AlertTriangle className="h-4 w-4 text-slate-600" />
                    <AlertDescription className="text-slate-700">
                      Geometry not generated yet. Click &quot;Validate&quot; button above to generate 3D geometry model.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <div className="space-y-4">
                    {/* Geometry Summary */}
                    <div className="p-4 bg-green-50 border border-green-200 rounded-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle2 className="text-green-700" size={18} />
                        <span className="font-semibold text-sm text-green-900">
                          3D Geometry Model Generated
                        </span>
                      </div>
                      <p className="text-xs text-green-800">
                        Connection geometry has been calculated and is ready for export to Tekla Structures.
                      </p>
                    </div>

                    {/* Geometry Details */}
                    {connection.geometry.type && (
                      <div className="p-3 bg-slate-50 border border-slate-200 rounded-sm">
                        <div className="text-sm font-medium text-slate-900 mb-1">
                          Geometry Type: <span className="font-normal">{connection.geometry.type}</span>
                        </div>
                      </div>
                    )}

                    {/* Dimensions Summary */}
                    {connection.geometry.dimensions && (
                      <div className="p-4 bg-white border border-slate-200 rounded-sm">
                        <h4 className="font-semibold text-sm text-slate-900 mb-3">Overall Dimensions</h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {Object.entries(connection.geometry.dimensions).map(([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="text-slate-600">{key.replace(/_/g, ' ')}:</span>
                              <span className="ml-1 font-medium text-slate-900">
                                {typeof value === 'number' ? value.toFixed(2) : value}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Components */}
                    {(connection.geometry.plate || connection.geometry.bolts || connection.geometry.angles) && (
                      <div className="space-y-3">
                        <h4 className="font-semibold text-sm text-slate-900">Connection Components</h4>
                        
                        {connection.geometry.plate && (
                          <div className="p-3 bg-blue-50 border border-blue-200 rounded-sm">
                            <div className="font-medium text-sm text-blue-900 mb-2">Plate</div>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              {Object.entries(connection.geometry.plate).map(([key, value]) => (
                                <div key={key}>
                                  <span className="text-blue-700">{key}:</span>
                                  <span className="ml-1 text-blue-900 font-medium">
                                    {typeof value === 'number' ? value.toFixed(3) : value} in
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {connection.geometry.bolts && connection.geometry.bolts.length > 0 && (
                          <div className="p-3 bg-purple-50 border border-purple-200 rounded-sm">
                            <div className="font-medium text-sm text-purple-900 mb-2">
                              Bolts ({connection.geometry.bolts.length} total)
                            </div>
                            <div className="space-y-2 max-h-64 overflow-y-auto">
                              {connection.geometry.bolts.map((bolt, idx) => (
                                <div key={idx} className="text-xs p-2 bg-white rounded border border-purple-100">
                                  <div className="font-medium text-purple-900 mb-1">Bolt {idx + 1}</div>
                                  {bolt.position && (
                                    <div className="text-purple-700">
                                      Position: x={bolt.position.x?.toFixed(2)}, y={bolt.position.y?.toFixed(2)}, z={bolt.position.z?.toFixed(2)}
                                    </div>
                                  )}
                                  {bolt.diameter && (
                                    <div className="text-purple-700">Diameter: {bolt.diameter} in</div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {connection.geometry.angles && connection.geometry.angles.length > 0 && (
                          <div className="p-3 bg-orange-50 border border-orange-200 rounded-sm">
                            <div className="font-medium text-sm text-orange-900 mb-2">
                              Angles ({connection.geometry.angles.length} total)
                            </div>
                            <div className="text-xs">
                              {connection.geometry.angles.map((angle, idx) => (
                                <div key={idx} className="mb-2">
                                  <strong>Angle {idx + 1}:</strong> {JSON.stringify(angle)}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Raw Geometry Data */}
                    <details className="p-3 bg-slate-50 border border-slate-200 rounded-sm">
                      <summary className="cursor-pointer text-sm font-medium text-slate-900 hover:text-slate-700">
                        View Raw Geometry Data (JSON)
                      </summary>
                      <pre className="mt-3 text-xs bg-white p-3 rounded border border-slate-200 overflow-auto max-h-96 font-mono">
                        {JSON.stringify(connection.geometry, null, 2)}
                      </pre>
                    </details>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-8 p-4 bg-slate-50 border border-slate-200 rounded-sm">
          <p className="text-xs text-slate-700">
            <strong>ENGINEERING DISCLAIMER:</strong> This is a design assist tool. All outputs require licensed engineer review and approval. Not for stamped drawings.
          </p>
        </div>
      </div>
    </div>
  );
};

// Helper function to get parameter fields based on connection type
function getParameterFields(connectionType) {
  const commonFields = [
    { key: 'beam_depth', label: 'Beam Depth', placeholder: '24', unit: 'inches', required: true },
    { key: 'beam_flange_width', label: 'Beam Flange Width', placeholder: '9', unit: 'inches', required: true },
    { key: 'beam_flange_thickness', label: 'Beam Flange Thickness', placeholder: '0.75', unit: 'inches', step: '0.01', required: true },
    { key: 'beam_web_thickness', label: 'Beam Web Thickness', placeholder: '0.5', unit: 'inches', step: '0.01', required: true },
    { key: 'shear_force', label: 'Shear Force', placeholder: '50', unit: 'kips', required: true },
  ];

  const typeSpecificFields = {
    single_plate: [
      { key: 'plate_thickness', label: 'Plate Thickness', placeholder: '0.375', unit: 'inches', step: '0.01', required: true },
      { key: 'plate_width', label: 'Plate Width', placeholder: '6', unit: 'inches', required: true },
      { key: 'bolt_diameter', label: 'Bolt Diameter', placeholder: '0.75', unit: 'inches', step: '0.125', required: true },
      { key: 'bolt_rows', label: 'Number of Bolt Rows', placeholder: '3', required: true },
    ],
    double_angle: [
      { key: 'angle_size', label: 'Angle Size', placeholder: '6', unit: 'inches', required: true },
      { key: 'angle_thickness', label: 'Angle Thickness', placeholder: '0.5', unit: 'inches', step: '0.01', required: true },
      { key: 'bolt_diameter', label: 'Bolt Diameter', placeholder: '0.75', unit: 'inches', step: '0.125', required: true },
    ],
    end_plate: [
      { key: 'plate_thickness', label: 'Plate Thickness', placeholder: '0.5', unit: 'inches', step: '0.01', required: true },
      { key: 'bolt_diameter', label: 'Bolt Diameter', placeholder: '0.875', unit: 'inches', step: '0.125', required: true },
      { key: 'moment', label: 'Moment', placeholder: '200', unit: 'kip-ft', required: true },
    ],
  };

  return [...commonFields, ...(typeSpecificFields[connectionType] || [])];
}
