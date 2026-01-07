import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../../lib/api';
import { setAuthToken, setUser } from '../../lib/auth';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { toast } from 'sonner';

export const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authAPI.login({ email, password });
      setAuthToken(response.data.access_token);
      setUser(response.data.user);
      toast.success('Login successful');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="mb-8">
            <h1 className="text-4xl font-heading font-bold text-slate-900 mb-2" data-testid="login-title">
              SteelConnect AI
            </h1>
            <p className="text-sm text-slate-600">
              AI-Assisted Steel Connection Detailing for US Fabricators
            </p>
          </div>

          <div className="bg-white border border-slate-200 rounded-sm shadow-sm p-6">
            <form onSubmit={handleLogin} data-testid="login-form">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-9 rounded-sm border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                    required
                    data-testid="login-email-input"
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-9 rounded-sm border-slate-300 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                    required
                    data-testid="login-password-input"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-slate-900 text-white hover:bg-slate-800 rounded-sm font-medium shadow-sm"
                  disabled={loading}
                  data-testid="login-submit-button"
                >
                  {loading ? 'Logging in...' : 'Log In'}
                </Button>
              </div>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium" data-testid="register-link">
                  Register
                </Link>
              </p>
            </div>
          </div>

          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-sm">
            <p className="text-xs text-yellow-800">
              <strong>ADVISORY TOOL:</strong> AI suggestions are not authoritative. All outputs require engineer review and approval.
            </p>
          </div>
        </div>
      </div>

      <div
        className="hidden lg:block flex-1 bg-cover bg-center"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1762584345845-f1cf77e1f28c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxzdGVlbCUyMGNvbnN0cnVjdGlvbiUyMHNpdGUlMjBza3lzY3JhcGVyfGVufDB8fHx8MTc2Nzc3MzYxOHww&ixlib=rb-4.1.0&q=85')`,
        }}
      >
        <div className="h-full bg-slate-900/40 flex items-center justify-center p-12">
          <div className="text-white max-w-lg">
            <h2 className="text-3xl font-heading font-bold mb-4">
              Precision Engineering
            </h2>
            <p className="text-lg text-slate-200">
              AISC 360-16 compliant connection design with deterministic rule validation and Tekla integration.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};