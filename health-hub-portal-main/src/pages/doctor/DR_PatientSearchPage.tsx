import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api, getErrorMessage } from '@/lib/api';
import { PageHeader } from '@/components/common/PageHeader';
import { LoadingState } from '@/components/common/LoadingState';
import { ErrorState } from '@/components/common/ErrorState';
import { EmptyState } from '@/components/common/EmptyState';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Users, Search, FileText } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface Patient {
  id: string;
  patient_uid: string;
  full_name?: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
}

export const DR_PatientSearchPage: React.FC = () => {
  const [patientUid, setPatientUid] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['doctor', 'patients', 'search', searchQuery],
    queryFn: async () => {
      if (!searchQuery) return [];
      const response = await api.get<Patient[]>(`/doctor/patients/search?patient_uid=${searchQuery}`);
      return response.data;
    },
    enabled: !!searchQuery,
  });

  const handleSearch = () => {
    setSearchQuery(patientUid);
  };

  const patients = data || [];

  return (
    <div>
      <PageHeader
        title="Patient Search"
        description="Search for patients by their UID"
      />

      <div className="mb-6">
        <div className="flex gap-3 max-w-md">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Enter patient UID..."
              value={patientUid}
              onChange={(e) => setPatientUid(e.target.value)}
              className="pl-10"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button onClick={handleSearch}>Search</Button>
        </div>
      </div>

      {!searchQuery ? (
        <div className="table-container">
          <EmptyState
            icon={Users}
            title="Search for patients"
            description="Enter a patient UID to search for their records."
          />
        </div>
      ) : isLoading ? (
        <LoadingState message="Searching patients..." />
      ) : isError ? (
        <ErrorState message={getErrorMessage(error)} onRetry={() => refetch()} />
      ) : patients.length === 0 ? (
        <div className="table-container">
          <EmptyState
            icon={Users}
            title="No patients found"
            description={`No patients found with UID "${searchQuery}"`}
          />
        </div>
      ) : (
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Patient UID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {patients.map((patient) => (
                <TableRow key={patient.id}>
                  <TableCell className="font-medium font-mono">
                    {patient.patient_uid}
                  </TableCell>
                  <TableCell>{patient.full_name || '—'}</TableCell>
                  <TableCell>{patient.email || '—'}</TableCell>
                  <TableCell>{patient.phone || '—'}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/doctor/patients/${patient.id}/history`}>
                        <FileText className="w-4 h-4 mr-2" />
                        History
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
};
