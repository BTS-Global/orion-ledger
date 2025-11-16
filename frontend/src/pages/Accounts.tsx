import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useCsrfToken, getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';
import { InfoTooltip } from "@/components/InfoTooltip";
import { ACCOUNT_TYPE_TOOLTIPS, ACCOUNT_CODE_TOOLTIP, DOUBLE_ENTRY_TOOLTIP } from "@/lib/tooltips";
import { AIChartAnalysis } from "@/components/AIChartAnalysis";

import { BACKEND_URL } from "@/config/api";;

interface Account {
  id: string;
  company: string;
  company_name: string;
  account_number: string;
  account_name: string;
  account_type: string;
  description: string;
  is_active: boolean;
  balance: string;
  created_at: string;
}

interface Company {
  id: string;
  name: string;
}

const ACCOUNT_TYPES = [
  { value: 'ASSET', label: 'Asset' },
  { value: 'LIABILITY', label: 'Liability' },
  { value: 'EQUITY', label: 'Equity' },
  { value: 'REVENUE', label: 'Revenue' },
  { value: 'EXPENSE', label: 'Expense' },
];

const TYPE_COLORS: Record<string, string> = {
  'ASSET': 'bg-green-100 text-green-800',
  'LIABILITY': 'bg-red-100 text-red-800',
  'EQUITY': 'bg-blue-100 text-blue-800',
  'REVENUE': 'bg-purple-100 text-purple-800',
  'EXPENSE': 'bg-orange-100 text-orange-800',
};

export default function Accounts() {
  const csrfToken = useCsrfToken();
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterCompany, setFilterCompany] = useState<string>('all');
  const [showInitCOADialog, setShowInitCOADialog] = useState(false);
  const [selectedCompanyForInit, setSelectedCompanyForInit] = useState<string>('');
  const [initializingCOA, setInitializingCOA] = useState(false);
  const [formData, setFormData] = useState({
    company: '',
    account_code: '',
    account_name: '',
    account_type: 'ASSET',
    description: '',
    is_active: true,
  });

  useEffect(() => {
    fetchCompanies();
    fetchAccounts();
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
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/accounts/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.results || data);
      }
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
      toast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingAccount 
        ? `${BACKEND_URL}/api/accounts/${editingAccount.id}/`
        : `${BACKEND_URL}/api/accounts/`;
      
      const method = editingAccount ? 'PUT' : 'POST';
      
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
        toast.success(editingAccount ? 'Account updated!' : 'Account created!');
        setIsDialogOpen(false);
        resetForm();
        fetchAccounts();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to save account');
      }
    } catch (error) {
      console.error('Failed to save account:', error);
      toast.error('Failed to save account');
    }
  };

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setFormData({
      company: account.company,
      account_code: account.account_number,
      account_name: account.account_name,
      account_type: account.account_type,
      description: account.description,
      is_active: account.is_active,
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/accounts/${id}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      if (response.ok) {
        toast.success('Account deleted!');
        fetchAccounts();
      } else {
        toast.error('Failed to delete account');
      }
    } catch (error) {
      console.error('Failed to delete account:', error);
      toast.error('Failed to delete account');
    }
  };

  const toggleActive = async (account: Account) => {
    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/accounts/${account.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        credentials: 'include',
        body: JSON.stringify({ is_active: !account.is_active }),
      });

      if (response.ok) {
        toast.success(`Account ${!account.is_active ? 'activated' : 'deactivated'}!`);
        fetchAccounts();
      } else {
        toast.error('Failed to update account');
      }
    } catch (error) {
      console.error('Failed to update account:', error);
      toast.error('Failed to update account');
    }
  };

  const resetForm = () => {
    setEditingAccount(null);
    setFormData({
      company: companies.length > 0 ? companies[0].id : '',
      account_code: '',
      account_name: '',
      account_type: 'ASSET',
      description: '',
      is_active: true,
    });
  };

  const openNewDialog = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const handleInitializeDefaultCOA = async (companyId: string, overwrite: boolean = false) => {
    setInitializingCOA(true);
    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/companies/${companyId}/initialize_default_coa/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        credentials: 'include',
        body: JSON.stringify({ overwrite }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success(data.message || 'Default chart of accounts initialized successfully');
        fetchAccounts();
        setShowInitCOADialog(false);
      } else {
        toast.error(data.message || 'Failed to initialize chart of accounts');
      }
    } catch (error) {
      console.error('Error initializing COA:', error);
      toast.error('Failed to initialize chart of accounts');
    } finally {
      setInitializingCOA(false);
    }
  };

  const filteredAccounts = accounts.filter(account => {
    if (filterType !== 'all' && account.account_type !== filterType) return false;
    if (filterCompany !== 'all' && account.company !== filterCompany) return false;
    return true;
  });

  const groupedAccounts = filteredAccounts.reduce((acc, account) => {
    if (!acc[account.account_type]) {
      acc[account.account_type] = [];
    }
    acc[account.account_type].push(account);
    return acc;
  }, {} as Record<string, Account[]>);

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
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-gray-900">Chart of Accounts</h1>
                <InfoTooltip content={DOUBLE_ENTRY_TOOLTIP} />
              </div>
              <p className="text-sm text-gray-600">Manage your accounting structure</p>
            </div>
            <Button onClick={openNewDialog}>
              + New Account
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Label htmlFor="filter-type">Filter by Type</Label>
                  <InfoTooltip content="Filter accounts by their type: Assets, Liabilities, Equity, Revenue, or Expenses" />
                </div>
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger id="filter-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {ACCOUNT_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="filter-company">Filter by Company</Label>
                <Select value={filterCompany} onValueChange={setFilterCompany}>
                  <SelectTrigger id="filter-company">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Companies</SelectItem>
                    {companies.map(company => (
                      <SelectItem key={company.id} value={company.id}>{company.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* AI Analysis */}
        {companies.length > 0 && (
          <div className="mb-6">
            <AIChartAnalysis companyId={companies[0].id} />
          </div>
        )}

        {/* Accounts grouped by type */}
        {Object.entries(groupedAccounts).map(([type, typeAccounts]) => (
          <Card key={type} className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Badge className={TYPE_COLORS[type]}>
                  {ACCOUNT_TYPES.find(t => t.value === type)?.label || type}
                </Badge>
                <span className="text-sm text-gray-500">({typeAccounts.length} accounts)</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-4">Number</th>
                      <th className="text-left py-2 px-4">Name</th>
                      <th className="text-left py-2 px-4">Company</th>
                      <th className="text-right py-2 px-4">Balance</th>
                      <th className="text-center py-2 px-4">Status</th>
                      <th className="text-right py-2 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {typeAccounts.map((account) => (
                      <tr key={account.id} className="border-b hover:bg-gray-50">
                        <td className="py-3 px-4 font-mono text-sm">{account.account_number}</td>
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium">{account.account_name}</div>
                            {account.description && (
                              <div className="text-sm text-gray-500">{account.description}</div>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">{account.company_name}</td>
                        <td className="py-3 px-4 text-right font-mono">
                          ${parseFloat(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Badge variant={account.is_active ? "default" : "secondary"}>
                            {account.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex gap-2 justify-end">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => toggleActive(account)}
                            >
                              {account.is_active ? 'Deactivate' : 'Activate'}
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleEdit(account)}>
                              Edit
                            </Button>
                            <Button 
                              size="sm" 
                              variant="destructive" 
                              onClick={() => handleDelete(account.id, account.account_name)}
                            >
                              Delete
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredAccounts.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500 mb-4">No accounts found</p>
              <Button onClick={openNewDialog}>Create Your First Account</Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingAccount ? 'Edit Account' : 'New Account'}</DialogTitle>
            <DialogDescription>
              {editingAccount ? 'Update account information' : 'Add a new account to your chart of accounts'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div>
                <Label htmlFor="company">Company *</Label>
                <Select 
                  value={formData.company} 
                  onValueChange={(value) => setFormData({ ...formData, company: value })}
                  required
                >
                  <SelectTrigger id="company">
                    <SelectValue placeholder="Select a company" />
                  </SelectTrigger>
                  <SelectContent>
                    {companies.map(company => (
                      <SelectItem key={company.id} value={company.id}>{company.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Label htmlFor="account_code">Account Number *</Label>
                    <InfoTooltip content={ACCOUNT_CODE_TOOLTIP} />
                  </div>
                  <Input
                    id="account_code"
                    value={formData.account_code}
                    onChange={(e) => setFormData({ ...formData, account_code: e.target.value })}
                    placeholder="1000"
                    required
                  />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Label htmlFor="account_type">Account Type *</Label>
                    <InfoTooltip 
                      content={
                        <div className="space-y-2">
                          <p className="font-semibold">Account Types:</p>
                          {Object.entries(ACCOUNT_TYPE_TOOLTIPS).map(([key, value]) => (
                            <div key={key}>
                              <p className="font-medium text-xs">{key}:</p>
                              <p className="text-xs">{value}</p>
                            </div>
                          ))}
                        </div>
                      }
                    />
                  </div>
                  <Select 
                    value={formData.account_type} 
                    onValueChange={(value) => setFormData({ ...formData, account_type: value })}
                  >
                    <SelectTrigger id="account_type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ACCOUNT_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="account_name">Account Name *</Label>
                <Input
                  id="account_name"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                  placeholder="Cash"
                  required
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Optional description"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4"
                />
                <Label htmlFor="is_active" className="cursor-pointer">Active account</Label>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingAccount ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

