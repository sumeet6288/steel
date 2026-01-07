export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getRuleStatusColor = (status) => {
  switch (status) {
    case 'pass':
      return 'text-green-700 bg-green-50 border-green-200';
    case 'fail':
      return 'text-red-700 bg-red-50 border-red-200';
    case 'warning':
      return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    default:
      return 'text-slate-700 bg-slate-50 border-slate-200';
  }
};

export const getConnectionTypeLabel = (type) => {
  const labels = {
    beam_to_column_shear: 'Beam-to-Column Shear',
    beam_to_beam_shear: 'Beam-to-Beam Shear',
    single_plate: 'Single Plate',
    double_angle: 'Double Angle',
    end_plate: 'End Plate',
  };
  return labels[type] || type;
};

export const getConnectionStatusColor = (status) => {
  switch (status) {
    case 'validated':
      return 'text-green-700 bg-green-50 border-green-200';
    case 'failed':
      return 'text-red-700 bg-red-50 border-red-200';
    case 'exported':
      return 'text-blue-700 bg-blue-50 border-blue-200';
    case 'draft':
    default:
      return 'text-slate-700 bg-slate-50 border-slate-200';
  }
};