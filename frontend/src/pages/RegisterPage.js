import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    company: '',
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authAPI.register(formData);
      toast.success('Registration successful! Please log in.');
      navigate('/login');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-slate-50">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <h1 className="text-4xl font-heading font-bold text-slate-900 mb-2" data-testid="register-title">
            Create Account
          </h1>
          <p className="text-sm text-slate-600">
            Join SteelConnect AI
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-sm shadow-sm p-6">
          <form onSubmit={handleRegister} data-testid="register-form">
            <div className="space-y-4">
              <div>
                <Label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Full Name
                </Label>
                <Input
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="h-9 rounded-sm"
                  required
                  data-testid="register-name-input"
                />
              </div>
              <div>
                <Label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Email
                </Label>
                <Input
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="h-9 rounded-sm"
                  required
                  data-testid="register-email-input"
                />
              </div>
              <div>
                <Label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Company
                </Label>
                <Input
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                  className="h-9 rounded-sm"
                  data-testid="register-company-input"
                />
              </div>
              <div>
                <Label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Password
                </Label>
                <Input
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="h-9 rounded-sm"
                  required
                  data-testid="register-password-input"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-slate-900 text-white hover:bg-slate-800 rounded-sm"
                disabled={loading}
                data-testid="register-submit-button"
              >
                {loading ? 'Creating Account...' : 'Register'}
              </Button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium" data-testid="login-link">
                Log In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};