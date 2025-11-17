import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { toast } from 'sonner';
import { 
  Lightbulb, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  BarChart3,
  Brain,
  RefreshCw
} from 'lucide-react';
import { BACKEND_URL } from '@/config/api';
import logger from '@/utils/logger';

interface Suggestion {
  type: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
  missing_codes?: string[];
}

interface Statistics {
  total_transactions: number;
  validated_transactions: number;
  validation_rate: number;
}

interface InsightsData {
  suggestions: Suggestion[];
  statistics: Statistics;
}

interface TransactionInsightsProps {
  companyId: string;
}

const PRIORITY_CONFIG = {
  high: {
    color: 'bg-red-100 text-red-800 border-red-300',
    icon: AlertTriangle,
    label: 'High Priority'
  },
  medium: {
    color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    icon: Lightbulb,
    label: 'Medium Priority'
  },
  low: {
    color: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: TrendingUp,
    label: 'Low Priority'
  }
};

export function TransactionInsights({ companyId }: TransactionInsightsProps) {
  const [insights, setInsights] = useState<InsightsData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (companyId) {
      fetchInsights();
    }
  }, [companyId]);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/transactions/insights/?company=${companyId}`,
        { credentials: 'include' }
      );

      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      } else {
        toast.error('Failed to load insights');
      }
    } catch (error) {
      logger.error('Failed to fetch insights', error);
      toast.error('Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-500 mt-4">Analyzing data...</p>
        </CardContent>
      </Card>
    );
  }

  if (!insights) {
    return null;
  }

  const { suggestions, statistics } = insights;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-purple-600" />
          AI-Powered Transaction Insights
        </CardTitle>
        <CardDescription>
          Smart recommendations to improve your accounting accuracy and efficiency
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Statistics Overview */}
        <div className="grid grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <BarChart3 className="h-5 w-5 text-blue-600 mb-2" />
            <div className="text-2xl font-bold">{statistics.total_transactions}</div>
            <div className="text-sm text-gray-600">Total Transactions</div>
          </div>
          <div className="border rounded-lg p-4">
            <CheckCircle className="h-5 w-5 text-green-600 mb-2" />
            <div className="text-2xl font-bold">{statistics.validated_transactions}</div>
            <div className="text-sm text-gray-600">Validated</div>
          </div>
          <div className="border rounded-lg p-4">
            <TrendingUp className="h-5 w-5 text-purple-600 mb-2" />
            <div className="text-2xl font-bold">
              {statistics.validation_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600">Validation Rate</div>
          </div>
        </div>

        {/* Validation Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium">Overall Progress</span>
            <span className="text-gray-600">
              {statistics.validated_transactions} / {statistics.total_transactions}
            </span>
          </div>
          <Progress 
            value={statistics.validation_rate} 
            className="h-3"
          />
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 ? (
          <div className="space-y-3">
            <h3 className="font-medium flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-yellow-600" />
              Recommendations
            </h3>
            
            {suggestions.map((suggestion, index) => {
              const config = PRIORITY_CONFIG[suggestion.priority];
              const Icon = config.icon;
              
              return (
                <Alert key={index} className="border-l-4">
                  <Icon className="h-4 w-4" />
                  <AlertTitle className="flex items-center gap-2">
                    <Badge className={config.color}>
                      {config.label}
                    </Badge>
                    <span className="capitalize">{suggestion.type.replace('_', ' ')}</span>
                  </AlertTitle>
                  <AlertDescription>
                    {suggestion.message}
                    {suggestion.missing_codes && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {suggestion.missing_codes.map(code => (
                          <Badge key={code} variant="outline" className="font-mono">
                            {code}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </AlertDescription>
                </Alert>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-600" />
            <p className="font-medium text-green-700">All Good!</p>
            <p className="text-sm text-gray-600 mt-1">
              No recommendations at this time. Your accounting is in great shape!
            </p>
          </div>
        )}

        {/* Refresh Button */}
        <div className="flex justify-end pt-4 border-t">
          <Button
            variant="outline"
            onClick={fetchInsights}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Analyzing...' : 'Refresh Insights'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
