import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from 'sonner';
import { AlertCircle, CheckCircle, TrendingUp, FileText } from 'lucide-react';
import { BACKEND_URL } from '@/config/api';

interface CoverageAnalysis {
  coverage_score: number;
  total_accounts: number;
  active_accounts: number;
  inactive_accounts: number;
  accounts_by_type: Record<string, number>;
  missing_accounts: string[];
  recommendations: string[];
  completeness: {
    assets: boolean;
    liabilities: boolean;
    equity: boolean;
    revenue: boolean;
    expenses: boolean;
  };
}

interface COACoverageAnalysisProps {
  companyId: string;
}

const TYPE_COLORS: Record<string, string> = {
  'ASSET': 'bg-green-100 text-green-800',
  'LIABILITY': 'bg-red-100 text-red-800',
  'EQUITY': 'bg-blue-100 text-blue-800',
  'REVENUE': 'bg-purple-100 text-purple-800',
  'EXPENSE': 'bg-orange-100 text-orange-800',
};

export function COACoverageAnalysis({ companyId }: COACoverageAnalysisProps) {
  const [analysis, setAnalysis] = useState<CoverageAnalysis | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (companyId) {
      fetchAnalysis();
    }
  }, [companyId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/companies/${companyId}/coa_coverage_analysis/`,
        { credentials: 'include' }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalysis(data);
      } else {
        toast.error('Failed to load coverage analysis');
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
      toast.error('Failed to load coverage analysis');
    } finally {
      setLoading(false);
    }
  };

  const getCoverageColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCoverageLabel = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-500 mt-4">Analyzing coverage...</p>
        </CardContent>
      </Card>
    );
  }

  if (!analysis) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          Chart of Accounts Coverage Analysis
        </CardTitle>
        <CardDescription>
          Comprehensive analysis of your chart of accounts completeness and quality
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Coverage Score */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Overall Coverage Score</h3>
              <p className="text-sm text-gray-500">
                {getCoverageLabel(analysis.coverage_score)}
              </p>
            </div>
            <div className={`text-3xl font-bold ${getCoverageColor(analysis.coverage_score)}`}>
              {analysis.coverage_score}%
            </div>
          </div>
          <Progress value={analysis.coverage_score} className="h-3" />
        </div>

        {/* Account Statistics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 text-center">
            <FileText className="h-6 w-6 mx-auto mb-2 text-blue-600" />
            <div className="text-2xl font-bold">{analysis.total_accounts}</div>
            <div className="text-sm text-gray-600">Total Accounts</div>
          </div>
          <div className="border rounded-lg p-4 text-center">
            <CheckCircle className="h-6 w-6 mx-auto mb-2 text-green-600" />
            <div className="text-2xl font-bold">{analysis.active_accounts}</div>
            <div className="text-sm text-gray-600">Active</div>
          </div>
          <div className="border rounded-lg p-4 text-center">
            <AlertCircle className="h-6 w-6 mx-auto mb-2 text-gray-400" />
            <div className="text-2xl font-bold">{analysis.inactive_accounts}</div>
            <div className="text-sm text-gray-600">Inactive</div>
          </div>
        </div>

        {/* Accounts by Type */}
        <div className="space-y-2">
          <h3 className="font-medium">Accounts by Type</h3>
          <div className="space-y-2">
            {Object.entries(analysis.accounts_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Badge className={TYPE_COLORS[type] || 'bg-gray-100 text-gray-800'}>
                    {type}
                  </Badge>
                </div>
                <span className="font-medium">{count} accounts</span>
              </div>
            ))}
          </div>
        </div>

        {/* Completeness Check */}
        <div className="space-y-2">
          <h3 className="font-medium">Account Type Completeness</h3>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(analysis.completeness).map(([type, hasAccounts]) => (
              <div
                key={type}
                className={`flex items-center gap-2 p-2 rounded border ${
                  hasAccounts ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                }`}
              >
                {hasAccounts ? (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-600" />
                )}
                <span className="text-sm font-medium capitalize">{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Accounts */}
        {analysis.missing_accounts && analysis.missing_accounts.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-yellow-600" />
              <h3 className="font-medium">Suggested Missing Accounts</h3>
            </div>
            <div className="space-y-1">
              {analysis.missing_accounts.map((account, idx) => (
                <div
                  key={idx}
                  className="text-sm p-2 bg-yellow-50 border border-yellow-200 rounded"
                >
                  {account}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {analysis.recommendations && analysis.recommendations.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-blue-600" />
              <h3 className="font-medium">Recommendations</h3>
            </div>
            <div className="space-y-2">
              {analysis.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="text-sm p-3 bg-blue-50 border border-blue-200 rounded"
                >
                  {rec}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Refresh Button */}
        <div className="flex justify-end pt-4 border-t">
          <Button
            variant="outline"
            onClick={fetchAnalysis}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Refresh Analysis'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
