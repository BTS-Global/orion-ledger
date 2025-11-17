import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";
import { KPICard } from "@/components/KPICard";
import { RevenueChart } from "@/components/RevenueChart";
import { ExpenseBreakdown } from "@/components/ExpenseBreakdown";
import { CashRunway } from "@/components/CashRunway";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Wallet,
  Building2,
  FileText,
  Receipt,
  BarChart3,
} from "lucide-react";

import { BACKEND_URL } from "@/config/api";;
import logger from '@/utils/logger';

interface Stats {
  companies: number;
  transactions: number;
  documents: number;
  accounts: number;
}

interface KPIData {
  revenue: {
    current_month: number;
    last_month: number;
    ytd: number;
    change_percent: number;
  };
  expenses: {
    current_month: number;
    last_month: number;
    ytd: number;
    change_percent: number;
  };
  profit: {
    current_month: number;
    last_month: number;
    ytd: number;
    change_percent: number;
    margin_percent: number;
  };
  cash_runway: {
    current_balance: number;
    monthly_burn_rate: number;
    months_remaining: number;
  };
  top_expenses: Array<{
    category: string;
    amount: number;
    percent: number;
  }>;
  revenue_by_month: Array<{
    month: string;
    amount: number;
  }>;
  expenses_by_month: Array<{
    month: string;
    amount: number;
  }>;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({ companies: 0, transactions: 0, documents: 0, accounts: 0 });
  const [kpis, setKpis] = useState<KPIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [kpisLoading, setKpisLoading] = useState(true);
  const [companyId, setCompanyId] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
    fetchCompanyAndKPIs();
    
    // Refresh stats every 30 seconds
    const interval = setInterval(() => {
      fetchStats();
      fetchCompanyAndKPIs();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const [companiesRes, transactionsRes, documentsRes, accountsRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/companies/`, { credentials: 'include' }),
        fetch(`${BACKEND_URL}/api/transactions/`, { credentials: 'include' }),
        fetch(`${BACKEND_URL}/api/documents/`, { credentials: 'include' }),
        fetch(`${BACKEND_URL}/api/accounts/`, { credentials: 'include' }),
      ]);

      const companies = await companiesRes.json();
      const transactions = await transactionsRes.json();
      const documents = await documentsRes.json();
      const accounts = await accountsRes.json();

      setStats({
        companies: companies.results ? companies.results.length : (companies.count || 0),
        transactions: transactions.results ? transactions.results.length : (transactions.count || 0),
        documents: documents.results ? documents.results.length : (documents.count || 0),
        accounts: accounts.results ? accounts.results.length : (accounts.count || 0),
      });
    } catch (error) {
      logger.error('Failed to fetch stats', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanyAndKPIs = async () => {
    setKpisLoading(true);
    try {
      // First, get the list of companies
      const companiesRes = await fetch(`${BACKEND_URL}/api/companies/`, { credentials: 'include' });
      const companiesData = await companiesRes.json();
      
      if (companiesData.results && companiesData.results.length > 0) {
        const firstCompany = companiesData.results[0];
        setCompanyId(firstCompany.id);
        
        // Fetch KPIs for the first company
        const kpisRes = await fetch(`${BACKEND_URL}/api/companies/${firstCompany.id}/kpis/`, {
          credentials: 'include',
        });
        const kpisData = await kpisRes.json();
        
        if (kpisData.status === 'success') {
          setKpis(kpisData.data);
        }
      }
    } catch (error) {
      logger.error('Failed to fetch KPIs', error);
    } finally {
      setKpisLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Accounting Software</h1>
              <p className="text-sm text-gray-600">Dashboard</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Cards */}
        {kpisLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader className="pb-3">
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                </CardHeader>
              </Card>
            ))}
          </div>
        ) : kpis ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <KPICard
              title="Revenue"
              value={formatCurrency(kpis.revenue.current_month)}
              change={kpis.revenue.change_percent}
              subtitle="vs last month"
              icon={<DollarSign className="h-4 w-4" />}
              trend="up"
            />
            <KPICard
              title="Expenses"
              value={formatCurrency(kpis.expenses.current_month)}
              change={kpis.expenses.change_percent}
              subtitle="vs last month"
              icon={<TrendingDown className="h-4 w-4" />}
              trend={kpis.expenses.change_percent > 0 ? "down" : "up"}
            />
            <KPICard
              title="Profit"
              value={formatCurrency(kpis.profit.current_month)}
              change={kpis.profit.change_percent}
              subtitle={`${kpis.profit.margin_percent.toFixed(1)}% margin`}
              icon={<TrendingUp className="h-4 w-4" />}
              trend="up"
            />
            <KPICard
              title="Cash Runway"
              value={`${kpis.cash_runway.months_remaining.toFixed(1)} months`}
              subtitle={formatCurrency(kpis.cash_runway.current_balance)}
              icon={<Wallet className="h-4 w-4" />}
              trend={kpis.cash_runway.months_remaining >= 6 ? "up" : kpis.cash_runway.months_remaining >= 3 ? "neutral" : "down"}
            />
          </div>
        ) : null}

        {/* Charts Row */}
        {kpis && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <RevenueChart
              data={kpis.revenue_by_month}
              expensesData={kpis.expenses_by_month}
              type="line"
            />
            <ExpenseBreakdown data={kpis.top_expenses} />
          </div>
        )}

        {/* Cash Runway Card */}
        {kpis && (
          <div className="mb-8">
            <CashRunway
              currentBalance={kpis.cash_runway.current_balance}
              monthlyBurnRate={kpis.cash_runway.monthly_burn_rate}
              monthsRemaining={kpis.cash_runway.months_remaining}
            />
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center space-x-2">
                <Building2 className="h-4 w-4" />
                <span>Companies</span>
              </CardDescription>
              <CardTitle className="text-3xl">{loading ? '...' : stats.companies}</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href="/companies">
                <a className="text-sm text-blue-600 hover:underline">View all →</a>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center space-x-2">
                <Receipt className="h-4 w-4" />
                <span>Transactions</span>
              </CardDescription>
              <CardTitle className="text-3xl">{loading ? '...' : stats.transactions}</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href="/transactions">
                <a className="text-sm text-blue-600 hover:underline">View all →</a>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Documents</span>
              </CardDescription>
              <CardTitle className="text-3xl">{loading ? '...' : stats.documents}</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href="/documents">
                <a className="text-sm text-blue-600 hover:underline">View all →</a>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Chart of Accounts</span>
              </CardDescription>
              <CardTitle className="text-3xl">{loading ? '...' : stats.accounts}</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href="/accounts">
                <a className="text-sm text-blue-600 hover:underline">View all →</a>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <Link href="/companies">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <Building2 className="h-6 w-6 mb-2" />
                  <span className="text-xs">Manage Companies</span>
                </Button>
              </Link>
              <Link href="/accounts">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <BarChart3 className="h-6 w-6 mb-2" />
                  <span className="text-xs">Chart of Accounts</span>
                </Button>
              </Link>
              <Link href="/documents">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <FileText className="h-6 w-6 mb-2" />
                  <span className="text-xs">Upload Document</span>
                </Button>
              </Link>
              <Link href="/transactions">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <Receipt className="h-6 w-6 mb-2" />
                  <span className="text-xs">View Transactions</span>
                </Button>
              </Link>
              <Link href="/reports">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <BarChart3 className="h-6 w-6 mb-2" />
                  <span className="text-xs">Generate Reports</span>
                </Button>
              </Link>
              <Link href="/irs-forms">
                <Button variant="outline" className="w-full h-auto flex flex-col items-center py-4">
                  <FileText className="h-6 w-6 mb-2" />
                  <span className="text-xs">IRS Forms</span>
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Getting Started */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Follow these steps to set up your accounting system</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4">
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  1
                </span>
                <div>
                  <h3 className="font-medium">Set up your company</h3>
                  <p className="text-sm text-gray-600">Add company details and configure fiscal year</p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  2
                </span>
                <div>
                  <h3 className="font-medium">Upload bank statements</h3>
                  <p className="text-sm text-gray-600">Import transactions from PDF, CSV, or images</p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  3
                </span>
                <div>
                  <h3 className="font-medium">Review and validate transactions</h3>
                  <p className="text-sm text-gray-600">Categorize and approve extracted data</p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                  4
                </span>
                <div>
                  <h3 className="font-medium">Generate financial reports</h3>
                  <p className="text-sm text-gray-600">Create Balance Sheet, Income Statement, and Cash Flow reports</p>
                </div>
              </li>
            </ol>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

