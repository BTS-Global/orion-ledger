import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState, useEffect } from "react";
import { FileText, Download, Loader2, CheckCircle } from "lucide-react";
import { useCsrfToken, getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';
import { toast } from "sonner";
import { InfoTooltip } from "@/components/InfoTooltip";
import { IRS_FORM_TOOLTIPS } from "@/lib/tooltips";
import { AIFormAnalysis } from "@/components/AIFormAnalysis";

import { BACKEND_URL } from "@/config/api";;
import logger from '@/utils/logger';

interface IRSForm {
  id: number;
  form_type: string;
  tax_year: number;
  status: string;
  pdf_url: string | null;
  created_at: string;
}

interface Company {
  id: string;
  name: string;
}

export default function IRSForms() {
  const csrfToken = useCsrfToken();
  const [forms, setForms] = useState<IRSForm[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState<string | null>(null);
  
  // Form generation states
  const [selectedForm, setSelectedForm] = useState('5472');
  const [taxYear, setTaxYear] = useState(new Date().getFullYear().toString());

  useEffect(() => {
    fetchCompanies();
    fetchForms();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/companies/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const companiesList = data.results || data || [];
        setCompanies(companiesList);
        if (companiesList.length > 0) {
          setSelectedCompany(companiesList[0].id);
        }
      }
    } catch (error) {
      logger.error('Failed to fetch companies', error);
    }
  };

  const fetchForms = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/irs-forms/`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setForms(data.results || data || []);
      }
    } catch (error) {
      logger.error('Failed to fetch forms', error);
    }
  };

  const generateForm = async (formType: string) => {
    if (!selectedCompany) {
      toast.error('Please select a company first');
      return;
    }

    setGenerating(formType);
    setLoading(true);
    
    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      // Normalize form type: remove hyphens for API endpoint (1099-nec -> 1099nec)
      const normalizedFormType = formType.replace(/-/g, '');
      const endpoint = `${BACKEND_URL}/api/irs-forms-api/generate-${normalizedFormType}/`;
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        credentials: 'include',
        body: JSON.stringify({
          company_id: selectedCompany, // Use selected company (UUID)
          tax_year: parseInt(taxYear),
          recipient_data: (formType === '1099-nec' || formType === '1099nec') ? {
            name: 'John Doe',
            tin: '123-45-6789',
            address: '123 Main St, City, State 12345',
            amount: 50000
          } : undefined,
          taxpayer_data: formType === '1040' ? {
            name: 'Jane Smith',
            ssn: '987-65-4321',
            address: '456 Oak Ave, City, State 12345',
            filing_status: 'SINGLE',
            total_income: 75000,
            adjustments: 5000,
            wages: 75000
          } : undefined
        })
      });

      if (response.ok) {
        // Download PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Form_${formType}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast.success(`Form ${formType} generated successfully!`);
      } else {
        const errorData = await response.json();
        toast.error(`Failed to generate form: ${errorData.error || 'Unknown error'}`);
        logger.error('Failed to generate form', errorData);
      }
    } catch (error) {
      logger.error('Error generating form', error);
    } finally {
      setLoading(false);
      setGenerating(null);
    }
  };

  const downloadForm = (formId: number, formType: string, year: number) => {
    window.open(`${BACKEND_URL}/api/irs-forms/${formId}/download/?export_format=csv`, '_blank');
  };

  const getFormTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      '5472': 'Form 5472 - Information Return',
      '1099-NEC': 'Form 1099-NEC - Nonemployee Compensation',
      '1120': 'Form 1120 - Corporate Income Tax',
      '1040': 'Form 1040 - Individual Income Tax'
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      'DRAFT': 'bg-yellow-100 text-yellow-800',
      'READY': 'bg-blue-100 text-blue-800',
      'FILED': 'bg-green-100 text-green-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">IRS Tax Forms</h1>
          <p className="text-sm text-muted-foreground">
            Generate and manage IRS tax forms
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Generate New Form */}
        <Card>
          <CardHeader>
            <CardTitle>Generate New Form</CardTitle>
            <CardDescription>Create IRS tax forms from your accounting data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <Label htmlFor="company">Company *</Label>
                <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                  <SelectTrigger id="company">
                    <SelectValue placeholder="Select company" />
                  </SelectTrigger>
                  <SelectContent>
                    {companies.map((company) => (
                      <SelectItem key={company.id} value={company.id}>
                        {company.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="form-type">Form Type</Label>
                <Select value={selectedForm} onValueChange={setSelectedForm}>
                  <SelectTrigger id="form-type">
                    <SelectValue placeholder="Select form type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="5472">Form 5472 - Information Return</SelectItem>
                    <SelectItem value="1099-nec">Form 1099-NEC - Nonemployee Compensation</SelectItem>
                    <SelectItem value="1120">Form 1120 - Corporate Income Tax</SelectItem>
                    <SelectItem value="1040">Form 1040 - Individual Income Tax</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="tax-year">Tax Year</Label>
                <Input
                  id="tax-year"
                  type="number"
                  value={taxYear}
                  onChange={(e) => setTaxYear(e.target.value)}
                  min="2020"
                  max="2030"
                />
              </div>
            </div>
            <Button 
              onClick={() => generateForm(selectedForm)} 
              disabled={loading}
              className="w-full md:w-auto"
            >
              {generating === selectedForm ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Generate Form
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* AI Form Analysis - All Forms */}
        {selectedCompany && (
          <div className="space-y-6">
            <AIFormAnalysis
              companyId={selectedCompany}
              formType="5472"
              formTitle="Form 5472"
              formDescription="Information Return of a 25% Foreign-Owned U.S. Corporation - AI-powered analysis"
            />
            
            <AIFormAnalysis
              companyId={selectedCompany}
              formType="1099nec"
              formTitle="Form 1099-NEC"
              formDescription="Nonemployee Compensation - AI-powered analysis and generation"
            />
            
            <AIFormAnalysis
              companyId={selectedCompany}
              formType="1120"
              formTitle="Form 1120"
              formDescription="U.S. Corporation Income Tax Return - AI-powered analysis and generation"
            />
            
            <AIFormAnalysis
              companyId={selectedCompany}
              formType="1040"
              formTitle="Form 1040"
              formDescription="U.S. Individual Income Tax Return - AI-powered analysis and generation"
            />
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Form 5472</CardTitle>
                <InfoTooltip content={IRS_FORM_TOOLTIPS.form5472} side="left" />
              </div>
              <CardDescription>Information Return</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" disabled={loading}>
                {generating === '5472' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate'}
              </Button>
            </CardContent>
          </Card>

            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Form 1099-NEC</CardTitle>
                <InfoTooltip content={IRS_FORM_TOOLTIPS.form1099NEC} side="left" />
              </div>
              <CardDescription>Nonemployee Comp.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" disabled={loading}>
                {generating === '1099-nec' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate'}
              </Button>
            </CardContent>
          </Card>

            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Form 1120</CardTitle>
                <InfoTooltip content={IRS_FORM_TOOLTIPS.form1120} side="left" />
              </div>
              <CardDescription>Corporate Tax Return</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" disabled={loading}>
                {generating === '1120' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate'}
              </Button>
            </CardContent>
          </Card>

            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Form 1040</CardTitle>
                <InfoTooltip content={IRS_FORM_TOOLTIPS.form1040} side="left" />
              </div>
              <CardDescription>Individual Tax Return</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" disabled={loading}>
                {generating === '1040' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Generate'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Generated Forms List */}
        <Card>
          <CardHeader>
            <CardTitle>Generated Forms</CardTitle>
            <CardDescription>View and download your IRS tax forms</CardDescription>
          </CardHeader>
          <CardContent>
            {forms.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No forms generated yet</p>
                <p className="text-sm">Generate your first IRS form above</p>
              </div>
            ) : (
              <div className="space-y-3">
                {forms.map((form) => (
                  <div
                    key={form.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-center gap-4">
                      <FileText className="w-8 h-8 text-blue-600" />
                      <div>
                        <h3 className="font-semibold">{getFormTypeLabel(form.form_type)}</h3>
                        <p className="text-sm text-muted-foreground">
                          Tax Year: {form.tax_year} • Created: {new Date(form.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(form.status)}
                      {form.pdf_url && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadForm(form.id, form.form_type, form.tax_year)}
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Download CSV
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-900">
              <CheckCircle className="w-5 h-5" />
              Automated Form Generation
            </CardTitle>
          </CardHeader>
          <CardContent className="text-blue-800">
            <p className="text-sm">
              Forms are automatically populated with data from your accounting records. 
              Review each form carefully before filing with the IRS. These are simplified 
              representations - consult with a tax professional for official filing.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

