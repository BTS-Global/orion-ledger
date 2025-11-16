import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from 'sonner';
import { FileText, Download, TrendingUp, DollarSign, Calendar } from 'lucide-react';
import { BACKEND_URL } from '@/config/api';

interface FinancialReportsProps {
  companyId: string;
}

export function FinancialReports({ companyId }: FinancialReportsProps) {
  const [activeTab, setActiveTab] = useState('trial-balance');
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reportData, setReportData] = useState<any>(null);

  const generateReport = async (reportType: string) => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/reports/${reportType}/?company=${companyId}`;
      
      if (startDate) url += `&start_date=${startDate}`;
      if (endDate) url += `&end_date=${endDate}`;
      
      const response = await fetch(url, { credentials: 'include' });
      
      if (response.ok) {
        const data = await response.json();
        setReportData(data);
        toast.success('Report generated successfully');
      } else {
        toast.error('Failed to generate report');
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
      toast.error('Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const renderTrialBalance = () => {
    if (!reportData?.accounts) return null;
    
    return (
      <div className="space-y-4">
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-3 font-medium">Account Code</th>
                <th className="text-left p-3 font-medium">Account Name</th>
                <th className="text-right p-3 font-medium">Debits</th>
                <th className="text-right p-3 font-medium">Credits</th>
                <th className="text-right p-3 font-medium">Balance</th>
              </tr>
            </thead>
            <tbody>
              {reportData.accounts.map((account: any, index: number) => (
                <tr key={index} className="border-t hover:bg-gray-50">
                  <td className="p-3 font-mono text-sm">{account.account_code}</td>
                  <td className="p-3">{account.account_name}</td>
                  <td className="p-3 text-right font-mono">
                    {formatCurrency(account.debits)}
                  </td>
                  <td className="p-3 text-right font-mono">
                    {formatCurrency(account.credits)}
                  </td>
                  <td className="p-3 text-right font-mono font-medium">
                    {formatCurrency(account.balance)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot className="bg-gray-50 border-t-2 border-gray-300">
              <tr>
                <td colSpan={2} className="p-3 font-bold">Totals</td>
                <td className="p-3 text-right font-mono font-bold">
                  {formatCurrency(reportData.totals.debits)}
                </td>
                <td className="p-3 text-right font-mono font-bold">
                  {formatCurrency(reportData.totals.credits)}
                </td>
                <td className="p-3"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    );
  };

  const renderProfitLoss = () => {
    if (!reportData?.revenue) return null;
    
    return (
      <div className="space-y-6">
        {/* Revenue Section */}
        <div className="border rounded-lg p-4">
          <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-green-600" />
            Revenue
          </h3>
          <div className="space-y-2">
            {reportData.revenue.map((item: any, index: number) => (
              <div key={index} className="flex justify-between items-center">
                <span>{item.account_name}</span>
                <span className="font-mono font-medium text-green-600">
                  {formatCurrency(item.balance)}
                </span>
              </div>
            ))}
            <div className="flex justify-between items-center pt-2 border-t font-bold">
              <span>Total Revenue</span>
              <span className="font-mono text-green-600">
                {formatCurrency(reportData.total_revenue)}
              </span>
            </div>
          </div>
        </div>

        {/* Expenses Section */}
        <div className="border rounded-lg p-4">
          <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-red-600" />
            Expenses
          </h3>
          <div className="space-y-2">
            {reportData.expenses.map((item: any, index: number) => (
              <div key={index} className="flex justify-between items-center">
                <span>{item.account_name}</span>
                <span className="font-mono font-medium text-red-600">
                  {formatCurrency(item.balance)}
                </span>
              </div>
            ))}
            <div className="flex justify-between items-center pt-2 border-t font-bold">
              <span>Total Expenses</span>
              <span className="font-mono text-red-600">
                {formatCurrency(reportData.total_expenses)}
              </span>
            </div>
          </div>
        </div>

        {/* Net Income */}
        <div className={`border-2 rounded-lg p-4 ${
          reportData.net_income >= 0 ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex justify-between items-center">
            <span className="font-bold text-lg">Net Income</span>
            <span className={`font-mono font-bold text-2xl ${
              reportData.net_income >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(reportData.net_income)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  const renderBalanceSheet = () => {
    if (!reportData?.assets) return null;
    
    return (
      <div className="space-y-6">
        {/* Assets */}
        <div className="border rounded-lg p-4">
          <h3 className="font-bold text-lg mb-3">Assets</h3>
          {reportData.assets.current_assets.length > 0 && (
            <div className="mb-4">
              <h4 className="font-medium text-sm mb-2">Current Assets</h4>
              {reportData.assets.current_assets.map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center ml-4">
                  <span>{item.account_name}</span>
                  <span className="font-mono">{formatCurrency(item.balance)}</span>
                </div>
              ))}
            </div>
          )}
          {reportData.assets.fixed_assets.length > 0 && (
            <div>
              <h4 className="font-medium text-sm mb-2">Fixed Assets</h4>
              {reportData.assets.fixed_assets.map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center ml-4">
                  <span>{item.account_name}</span>
                  <span className="font-mono">{formatCurrency(item.balance)}</span>
                </div>
              ))}
            </div>
          )}
          <div className="flex justify-between items-center pt-3 mt-3 border-t font-bold">
            <span>Total Assets</span>
            <span className="font-mono">{formatCurrency(reportData.assets.total)}</span>
          </div>
        </div>

        {/* Liabilities & Equity */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-bold text-lg mb-3">Liabilities</h3>
            <div className="space-y-2">
              {reportData.liabilities.current_liabilities.map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm">{item.account_name}</span>
                  <span className="font-mono text-sm">{formatCurrency(item.balance)}</span>
                </div>
              ))}
              <div className="flex justify-between items-center pt-2 border-t font-bold">
                <span>Total Liabilities</span>
                <span className="font-mono">{formatCurrency(reportData.liabilities.total)}</span>
              </div>
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h3 className="font-bold text-lg mb-3">Equity</h3>
            <div className="space-y-2">
              {reportData.equity.accounts.map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm">{item.account_name}</span>
                  <span className="font-mono text-sm">{formatCurrency(item.balance)}</span>
                </div>
              ))}
              <div className="flex justify-between items-center pt-2 border-t font-bold">
                <span>Total Equity</span>
                <span className="font-mono">{formatCurrency(reportData.equity.total)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          Financial Reports
        </CardTitle>
        <CardDescription>
          Generate comprehensive financial reports with real-time data
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Date Range Selector */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="start-date">Start Date</Label>
            <Input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="end-date">End Date</Label>
            <Input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>

        {/* Report Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="trial-balance">Trial Balance</TabsTrigger>
            <TabsTrigger value="profit-loss">P&L</TabsTrigger>
            <TabsTrigger value="balance-sheet">Balance Sheet</TabsTrigger>
            <TabsTrigger value="cash-flow">Cash Flow</TabsTrigger>
          </TabsList>

          <TabsContent value="trial-balance" className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                View all account balances with debits and credits
              </p>
              <Button
                onClick={() => generateReport('trial_balance_cached')}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
            {reportData && renderTrialBalance()}
          </TabsContent>

          <TabsContent value="profit-loss" className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Income statement showing revenue, expenses, and net income
              </p>
              <Button
                onClick={() => generateReport('profit_loss')}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
            {reportData && renderProfitLoss()}
          </TabsContent>

          <TabsContent value="balance-sheet" className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Snapshot of assets, liabilities, and equity
              </p>
              <Button
                onClick={() => generateReport('balance_sheet_optimized')}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
            {reportData && renderBalanceSheet()}
          </TabsContent>

          <TabsContent value="cash-flow" className="space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Track cash inflows and outflows
              </p>
              <Button
                onClick={() => generateReport('cash_flow')}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>
            {reportData && (
              <div className="text-center text-gray-500">
                Cash flow report ready
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Report Metadata */}
        {reportData && (
          <div className="flex items-center gap-4 text-sm text-gray-600 border-t pt-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>
                Generated: {new Date(reportData.generated_at).toLocaleString()}
              </span>
            </div>
            {reportData.period_start && (
              <Badge variant="outline">
                Period: {reportData.period_start} to {reportData.period_end}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
