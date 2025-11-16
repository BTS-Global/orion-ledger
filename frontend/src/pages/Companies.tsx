import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { useCsrfToken, getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';

import { BACKEND_URL } from "@/config/api";;

interface Company {
  id: string;
  name: string;
  tax_id: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  email: string;
  fiscal_year_start: string;
  accounts_count: number;
  created_at: string;
}

export default function Companies() {
  const csrfToken = useCsrfToken();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    tax_id: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    phone: '',
    email: '',
    fiscal_year_start: new Date().getFullYear() + '-01-01',
  });

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/companies/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setCompanies(data.results || data);
      }
    } catch (error) {
      console.error('Failed to fetch companies:', error);
      toast.error('Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingCompany 
        ? `${BACKEND_URL}/api/companies/${editingCompany.id}/`
        : `${BACKEND_URL}/api/companies/`;
      
      const method = editingCompany ? 'PUT' : 'POST';
      
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast.success(editingCompany ? 'Company updated!' : 'Company created!');
        setIsDialogOpen(false);
        resetForm();
        fetchCompanies();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save company');
      }
    } catch (error) {
      console.error('Failed to save company:', error);
      toast.error('Failed to save company');
    }
  };

  const handleEdit = (company: Company) => {
    setEditingCompany(company);
    setFormData({
      name: company.name,
      tax_id: company.tax_id,
      address: company.address,
      city: company.city,
      state: company.state,
      zip_code: company.zip_code,
      phone: company.phone,
      email: company.email,
      fiscal_year_start: company.fiscal_year_start,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/companies/${id}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      if (response.ok) {
        toast.success('Company deleted!');
        fetchCompanies();
      } else {
        toast.error('Failed to delete company');
      }
    } catch (error) {
      console.error('Failed to delete company:', error);
      toast.error('Failed to delete company');
    }
  };

  const handleActivate = async (id: string, name: string) => {
    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/companies/${id}/activate/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message || `${name} is now your active company`);
      } else {
        toast.error('Failed to activate company');
      }
    } catch (error) {
      console.error('Failed to activate company:', error);
      toast.error('Failed to activate company');
    }
  };

  const resetForm = () => {
    setEditingCompany(null);
    setFormData({
      name: '',
      tax_id: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      phone: '',
      email: '',
      fiscal_year_start: new Date().getFullYear() + '-01-01',
    });
  };

  const openNewDialog = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
              <p className="text-sm text-gray-600">Manage your companies</p>
            </div>
            <Button onClick={openNewDialog}>
              + New Company
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <Card key={company.id}>
              <CardHeader>
                <CardTitle>{company.name}</CardTitle>
                <CardDescription>EIN: {company.tax_id}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <p><strong>Address:</strong> {company.address}, {company.city}, {company.state} {company.zip_code}</p>
                  <p><strong>Phone:</strong> {company.phone}</p>
                  <p><strong>Email:</strong> {company.email}</p>
                  <p><strong>Fiscal Year:</strong> Starts {company.fiscal_year_start}</p>
                  <p><strong>Accounts:</strong> {company.accounts_count}</p>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button size="sm" variant="outline" onClick={() => handleActivate(company.id, company.name)}>
                    Set Active
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleEdit(company)}>
                    Edit
                  </Button>
                  <Button size="sm" variant="destructive" onClick={() => handleDelete(company.id, company.name)}>
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {companies.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 mb-4">No companies yet</p>
              <Button onClick={openNewDialog}>Create Your First Company</Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingCompany ? 'Edit Company' : 'New Company'}</DialogTitle>
            <DialogDescription>
              {editingCompany ? 'Update company information' : 'Add a new company to your account'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">Company Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="tax_id">EIN / Tax ID *</Label>
                  <Input
                    id="tax_id"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                    placeholder="12-3456789"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="address">Address *</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City *</Label>
                  <Input
                    id="city"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="state">State *</Label>
                  <Input
                    id="state"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    placeholder="NY"
                    maxLength={2}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="zip_code">ZIP Code *</Label>
                  <Input
                    id="zip_code"
                    value={formData.zip_code}
                    onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                    placeholder="10001"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    placeholder="(555) 123-4567"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="fiscal_year_start">Fiscal Year Start *</Label>
                <Input
                  id="fiscal_year_start"
                  type="date"
                  value={formData.fiscal_year_start}
                  onChange={(e) => setFormData({ ...formData, fiscal_year_start: e.target.value })}
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingCompany ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

