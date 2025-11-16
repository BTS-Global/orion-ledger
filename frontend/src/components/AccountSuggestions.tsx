import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from 'sonner';
import { Search, Sparkles, TrendingUp } from 'lucide-react';
import { BACKEND_URL } from '@/config/api';

interface AccountSuggestion {
  account_id: string;
  account_number: string;
  account_name: string;
  confidence: number;
  reasons: string[];
}

interface AccountSuggestionsProps {
  companyId: string;
}

export function AccountSuggestions({ companyId }: AccountSuggestionsProps) {
  const [description, setDescription] = useState('');
  const [suggestions, setSuggestions] = useState<AccountSuggestion[]>([]);
  const [loading, setLoading] = useState(false);

  const getSuggestions = async () => {
    if (!description.trim()) {
      toast.error('Please enter a transaction description');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/transactions/suggest_accounts/?company=${companyId}&description=${encodeURIComponent(description)}`,
        { credentials: 'include' }
      );

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        
        if (data.suggestions && data.suggestions.length === 0) {
          toast.info('No suggestions found. Try a different description.');
        }
      } else {
        toast.error('Failed to get account suggestions');
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      toast.error('Failed to get account suggestions');
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-300';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    return 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-600" />
          AI-Powered Account Suggestions
        </CardTitle>
        <CardDescription>
          Get intelligent account recommendations based on transaction descriptions
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="description">Transaction Description</Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Monthly office rent payment"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  getSuggestions();
                }
              }}
            />
          </div>
          <div className="flex items-end">
            <Button 
              onClick={getSuggestions}
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Get Suggestions
                </>
              )}
            </Button>
          </div>
        </div>

        {suggestions.length > 0 && (
          <div className="space-y-3 mt-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-600" />
              <h3 className="font-medium">Recommended Accounts</h3>
            </div>
            
            {suggestions.map((suggestion, index) => (
              <div
                key={suggestion.account_id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="font-mono">
                        {suggestion.account_number}
                      </Badge>
                      <span className="font-medium">{suggestion.account_name}</span>
                      <Badge className={getConfidenceColor(suggestion.confidence)}>
                        {getConfidenceLabel(suggestion.confidence)} ({Math.round(suggestion.confidence * 100)}%)
                      </Badge>
                    </div>
                    
                    {suggestion.reasons && suggestion.reasons.length > 0 && (
                      <div className="text-sm text-gray-600 space-y-1">
                        <p className="font-medium">Why this account?</p>
                        <ul className="list-disc list-inside space-y-1">
                          {suggestion.reasons.map((reason, idx) => (
                            <li key={idx}>{reason}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className="text-2xl">
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : ''}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {suggestions.length === 0 && !loading && (
          <div className="text-center py-8 text-gray-500">
            <Sparkles className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>Enter a transaction description to get AI-powered account suggestions</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
