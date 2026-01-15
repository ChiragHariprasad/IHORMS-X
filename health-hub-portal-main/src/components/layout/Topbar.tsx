import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, Bell, Settings } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth();

  // Health check query
  const { data: healthStatus, isError: isBackendDown } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await api.get('/health');
      return response.data;
    },
    refetchInterval: 30000, // Check every 30 seconds
    retry: false,
  });

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="fixed top-0 left-64 right-0 h-16 bg-card border-b border-border z-30 flex items-center justify-between px-6">
      {/* Backend status indicator */}
      {isBackendDown && (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-destructive/10 text-destructive rounded-lg text-sm">
          <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
          Backend unavailable
        </div>
      )}

      {!isBackendDown && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span className="w-2 h-2 rounded-full bg-success" />
          System online
        </div>
      )}

      {/* Right side actions */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" className="text-muted-foreground">
          <Bell className="w-5 h-5" />
        </Button>
        
        <div className="h-8 w-px bg-border" />
        
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-medium text-foreground">
              {user?.full_name || user?.email}
            </p>
            <p className="text-xs text-muted-foreground capitalize">
              {user?.role.replace('_', ' ')}
            </p>
          </div>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="text-muted-foreground hover:text-destructive"
          >
            <LogOut className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};
