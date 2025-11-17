import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useState, useEffect } from "react";
import { FileDown, Loader2, DollarSign } from "lucide-react";

import { BACKEND_URL } from "@/config/api";;
import logger from '@/utils/logger';

interface BalanceSheetData {
  date: string;
  company: string;
  assets: {
    items: Array<{ account_name: string; balance: number }>;
    total: number;
  };
  liabilities: {
    items: Array<{ account_name: string; balance: number }>;
    total: number;
  };
  equity: {
    items: Array<{ account_name: string; balance: number }>;
    total: number;
  };
  total_liabilities_and_equity: number;
  balanced: boolean;
}

interface IncomeStatementData {
  start_date: string;
  end_date: string;
  company: string;
  revenues: {
    items: Array<{ account_name: string; amount: number }>;
    total: number;
  };
  expenses: {
    items: Array<{ account_name: string; amount: number }>;
    total: number;
  };
  net_income: number;
}

interface CashFlowData {
  start_date: string;
  end_date: string;
  company: string;
  beginning_cash_balance: number;
  ending_cash_balance: number;
  net_change_in_cash: number;
  net_income: number;
  operating_activities: number;
  investing_activities: number;
  financing_activities: number;
}

interface Company {
  id: string;
  name: string;
}

export default function Reports() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheetData | null>(null);
  const [incomeStatement, setIncomeStatement] = useState<IncomeStatementData | null>(null);
  const [cashFlow, setCashFlow] = useState<CashFlowData | null>(null);
  const [loading, setLoading] = useState(false);
  
  // Form states
  const [bsEndDate, setBsEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [isStartDate, setIsStartDate] = useState(new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]);
  const [isEndDate, setIsEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [cfStartDate, setCfStartDate] = useState(new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0]);
  const [cfEndDate, setCfEndDate] = useState(new Date().toISOString().split('T')[0]);

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
        const companyList = data.results || data || [];
        setCompanies(companyList);
        if (companyList.length > 0 && !selectedCompany) {
          setSelectedCompany(companyList[0].id);
        }
      }
    } catch (error) {
      logger.error('Failed to fetch companies', error);
    }
  };

  const fetchBalanceSheet = async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/reports/balance_sheet/?company=${selectedCompany}&end_date=${bsEndDate}`,
        { credentials: 'include' }
      );
      if (response.ok) {
        const data = await response.json();
        setBalanceSheet(data);
      }
    } catch (error) {
      logger.error('Failed to fetch balance sheet', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIncomeStatement = async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/reports/income_statement/?company=${selectedCompany}&start_date=${isStartDate}&end_date=${isEndDate}`,
        { credentials: 'include' }
      );
      if (response.ok) {
        const data = await response.json();
        setIncomeStatement(data);
      }
    } catch (error) {
      logger.error('Failed to fetch income statement', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCashFlow = async () => {
    if (!selectedCompany) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/reports/cash_flow/?company=${selectedCompany}&start_date=${cfStartDate}&end_date=${cfEndDate}`,
        { credentials: 'include' }
      );
      if (response.ok) {
        const data = await response.json();
        setCashFlow(data);
      }
    } catch (error) {
      logger.error('Failed to fetch cash flow', error);
    } finally {
      setLoading(false);
    }
  };

  const exportReport = (reportType: string, format: string, startDate?: string, endDate?: string) => {
    console.log('=== EXPORT REPORT CALLED ===', reportType, format);
    let url = `${BACKEND_URL}/api/reports/${reportType}/?format=${format}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    
    window.open(url, '_blank');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Financial Reports</h1>
              <p className="text-sm text-muted-foreground">
                Generate and export financial statements
              </p>
            </div>
            <div className="w-64">
              <Label htmlFor="company-select">Company</Label>
              <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                <SelectTrigger id="company-select">
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
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="balance-sheet" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="balance-sheet">Balance Sheet</TabsTrigger>
            <TabsTrigger value="income-statement">Income Statement</TabsTrigger>
            <TabsTrigger value="cash-flow">Cash Flow</TabsTrigger>
          </TabsList>

          {/* Balance Sheet Tab */}
          <TabsContent value="balance-sheet" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Balance Sheet</CardTitle>
                <CardDescription>Statement of Financial Position</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="bs-end-date">As of Date</Label>
                    <Input
                      id="bs-end-date"
                      type="date"
                      value={bsEndDate}
                      onChange={(e) => setBsEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={fetchBalanceSheet} disabled={loading}>
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                    Generate Report
                  </Button>
                  {balanceSheet && (
                    <>
                      <Button
                        variant="outline"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); console.log('Export Excel clicked'); exportReport('balance_sheet', 'excel', undefined, bsEndDate); }}
                      >
                        <FileDown className="w-4 h-4 mr-2" />
                        Export Excel
                      </Button>
                      <Button
                        variant="outline"
                        onClick={(e) => { e.preventDefault(); e.stopPropagation(); console.log('Export PDF clicked'); exportReport('balance_sheet', 'pdf', undefined, bsEndDate); }}
                      >
                        <FileDown className="w-4 h-4 mr-2" />
                        Export PDF
                      </Button>
                    </>
                  )}
                </div>

                {balanceSheet && (
                  <div className="mt-6 space-y-6">
                    <div className="text-center">
                      <h2 className="text-xl font-bold">{balanceSheet.company}</h2>
                      <h3 className="text-lg">Balance Sheet</h3>
                      <p className="text-sm text-muted-foreground">As of {balanceSheet.date}</p>
                    </div>

                    {/* Assets */}
                    <div>
                      <h4 className="font-bold text-lg mb-2 bg-blue-100 p-2">ASSETS</h4>
                      <div className="space-y-1">
                        {balanceSheet.assets.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between px-4">
                            <span>{item.account_name}</span>
                            <span>{formatCurrency(item.balance)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between px-4 font-bold border-t-2 pt-2">
                          <span>Total Assets</span>
                          <span>{formatCurrency(balanceSheet.assets.total)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Liabilities */}
                    <div>
                      <h4 className="font-bold text-lg mb-2 bg-blue-100 p-2">LIABILITIES</h4>
                      <div className="space-y-1">
                        {balanceSheet.liabilities.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between px-4">
                            <span>{item.account_name}</span>
                            <span>{formatCurrency(item.balance)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between px-4 font-bold border-t-2 pt-2">
                          <span>Total Liabilities</span>
                          <span>{formatCurrency(balanceSheet.liabilities.total)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Equity */}
                    <div>
                      <h4 className="font-bold text-lg mb-2 bg-blue-100 p-2">EQUITY</h4>
                      <div className="space-y-1">
                        {balanceSheet.equity.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between px-4">
                            <span>{item.account_name}</span>
                            <span>{formatCurrency(item.balance)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between px-4 font-bold border-t-2 pt-2">
                          <span>Total Equity</span>
                          <span>{formatCurrency(balanceSheet.equity.total)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="border-t-4 border-double pt-4">
                      <div className="flex justify-between px-4 font-bold text-lg">
                        <span>TOTAL LIABILITIES & EQUITY</span>
                        <span>{formatCurrency(balanceSheet.total_liabilities_and_equity)}</span>
                      </div>
                      {balanceSheet.balanced && (
                        <p className="text-sm text-green-600 text-center mt-2">✓ Balanced</p>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Income Statement Tab */}
          <TabsContent value="income-statement" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Income Statement</CardTitle>
                <CardDescription>Profit & Loss Statement</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="is-start-date">Start Date</Label>
                    <Input
                      id="is-start-date"
                      type="date"
                      value={isStartDate}
                      onChange={(e) => setIsStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="is-end-date">End Date</Label>
                    <Input
                      id="is-end-date"
                      type="date"
                      value={isEndDate}
                      onChange={(e) => setIsEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={fetchIncomeStatement} disabled={loading}>
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                    Generate Report
                  </Button>
                  {incomeStatement && (
                    <>
                      <Button
                        variant="outline"
                        onClick={() => exportReport('income_statement', 'excel', isStartDate, isEndDate)}
                      >
                        <FileDown className="w-4 h-4 mr-2" />
                        Export Excel
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => exportReport('income_statement', 'pdf', isStartDate, isEndDate)}
                      >
                        <FileDown className="w-4 h-4 mr-2" />
                        Export PDF
                      </Button>
                    </>
                  )}
                </div>

                {incomeStatement && (
                  <div className="mt-6 space-y-6">
                    <div className="text-center">
                      <h2 className="text-xl font-bold">{incomeStatement.company}</h2>
                      <h3 className="text-lg">Income Statement</h3>
                      <p className="text-sm text-muted-foreground">
                        For the period {incomeStatement.start_date} to {incomeStatement.end_date}
                      </p>
                    </div>

                    {/* Revenue */}
                    <div>
                      <h4 className="font-bold text-lg mb-2 bg-green-100 p-2">REVENUE</h4>
                      <div className="space-y-1">
                        {incomeStatement.revenues.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between px-4">
                            <span>{item.account_name}</span>
                            <span>{formatCurrency(item.amount)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between px-4 font-bold border-t-2 pt-2">
                          <span>Total Revenue</span>
                          <span>{formatCurrency(incomeStatement.revenues.total)}</span>
                        </div>
                      </div>
                    </div>

                    {/* Expenses */}
                    <div>
                      <h4 className="font-bold text-lg mb-2 bg-red-100 p-2">EXPENSES</h4>
                      <div className="space-y-1">
                        {incomeStatement.expenses.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between px-4">
                            <span>{item.account_name}</span>
                            <span>{formatCurrency(item.amount)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between px-4 font-bold border-t-2 pt-2">
                          <span>Total Expenses</span>
                          <span>{formatCurrency(incomeStatement.expenses.total)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="border-t-4 border-double pt-4">
                      <div className="flex justify-between px-4 font-bold text-xl">
                        <span>NET INCOME</span>
                        <span className={incomeStatement.net_income >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {formatCurrency(incomeStatement.net_income)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Cash Flow Tab */}
          <TabsContent value="cash-flow" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Cash Flow Statement</CardTitle>
                <CardDescription>Statement of Cash Flows</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="cf-start-date">Start Date</Label>
                    <Input
                      id="cf-start-date"
                      type="date"
                      value={cfStartDate}
                      onChange={(e) => setCfStartDate(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="cf-end-date">End Date</Label>
                    <Input
                      id="cf-end-date"
                      type="date"
                      value={cfEndDate}
                      onChange={(e) => setCfEndDate(e.target.value)}
                    />
                  </div>
                </div>
                <Button onClick={fetchCashFlow} disabled={loading}>
                  {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  Generate Report
                </Button>

                {cashFlow && (
                  <div className="mt-6 space-y-6">
                    <div className="text-center">
                      <h2 className="text-xl font-bold">{cashFlow.company}</h2>
                      <h3 className="text-lg">Cash Flow Statement</h3>
                      <p className="text-sm text-muted-foreground">
                        For the period {cashFlow.start_date} to {cashFlow.end_date}
                      </p>
                    </div>

                    <div className="space-y-4">
                      <div className="flex justify-between px-4 py-2 bg-gray-100">
                        <span className="font-semibold">Beginning Cash Balance</span>
                        <span className="font-semibold">{formatCurrency(cashFlow.beginning_cash_balance)}</span>
                      </div>

                      <div className="px-4 space-y-2">
                        <div className="flex justify-between">
                          <span>Net Income</span>
                          <span>{formatCurrency(cashFlow.net_income)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Operating Activities</span>
                          <span>{formatCurrency(cashFlow.operating_activities)}</span>
                        </div>
                      </div>

                      <div className="flex justify-between px-4 py-2 bg-gray-100">
                        <span className="font-semibold">Ending Cash Balance</span>
                        <span className="font-semibold">{formatCurrency(cashFlow.ending_cash_balance)}</span>
                      </div>

                      <div className="flex justify-between px-4 py-3 bg-blue-100 font-bold text-lg">
                        <span>Net Change in Cash</span>
                        <span className={cashFlow.net_change_in_cash >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {formatCurrency(cashFlow.net_change_in_cash)}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

