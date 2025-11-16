import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from 'sonner';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { BACKEND_URL } from '@/config/api';
import { getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';

interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: string;
  type: string;
  account?: {
    id: string;
    account_number: string;
    account_name: string;
  };
  is_validated: boolean;
}

interface BulkTransactionValidatorProps {
  documentId: string;
  transactions: Transaction[];
  onValidationComplete: () => void;
}

export function BulkTransactionValidator({
  documentId,
  transactions,
  onValidationComplete,
}: BulkTransactionValidatorProps) {
  const [selectedTransactions, setSelectedTransactions] = useState<Set<string>>(new Set());
  const [validating, setValidating] = useState(false);

  const pendingTransactions = transactions.filter(t => !t.is_validated && t.account);
  const selectableTransactions = pendingTransactions.filter(t => t.account);

  const toggleTransaction = (id: string) => {
    const newSelected = new Set(selectedTransactions);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedTransactions(newSelected);
  };

  const toggleAll = () => {
    if (selectedTransactions.size === selectableTransactions.length) {
      setSelectedTransactions(new Set());
    } else {
      setSelectedTransactions(new Set(selectableTransactions.map(t => t.id)));
    }
  };

  const validateSelected = async () => {
    if (selectedTransactions.size === 0) {
      toast.error('Please select at least one transaction');
      return;
    }

    setValidating(true);
    let successCount = 0;
    let errorCount = 0;

    for (const transactionId of Array.from(selectedTransactions)) {
      try {
        const token = getCsrfTokenFromCookie();
        const response = await fetch(
          `${BACKEND_URL}/api/transactions/${transactionId}/validate/`,
          {
            method: 'POST',
            headers: {
              'X-CSRFToken': token,
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          }
        );

        if (response.ok) {
          successCount++;
        } else {
          errorCount++;
        }
      } catch (error) {
        console.error('Error validating transaction:', error);
        errorCount++;
      }
    }

    setValidating(false);
    setSelectedTransactions(new Set());

    if (errorCount === 0) {
      toast.success(`Successfully validated ${successCount} transactions`);
    } else {
      toast.warning(
        `Validated ${successCount} transactions, ${errorCount} failed`
      );
    }

    onValidationComplete();
  };

  const formatAmount = (amount: string) => {
    const num = parseFloat(amount);
    return num.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    });
  };

  if (selectableTransactions.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Bulk Validation</span>
          <Badge variant="secondary">
            {selectedTransactions.size} / {selectableTransactions.length} selected
          </Badge>
        </CardTitle>
        <CardDescription>
          Review and validate multiple transactions at once
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Select All */}
        <div className="flex items-center gap-2 pb-2 border-b">
          <Checkbox
            checked={selectedTransactions.size === selectableTransactions.length}
            onCheckedChange={toggleAll}
          />
          <span className="text-sm font-medium">Select All</span>
        </div>

        {/* Transaction List */}
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {selectableTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                selectedTransactions.has(transaction.id)
                  ? 'bg-blue-50 border-blue-300'
                  : 'hover:bg-gray-50'
              }`}
            >
              <Checkbox
                checked={selectedTransactions.has(transaction.id)}
                onCheckedChange={() => toggleTransaction(transaction.id)}
                className="mt-1"
              />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{transaction.description}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(transaction.date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-mono font-medium ${
                      transaction.type === 'CREDIT' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.type === 'CREDIT' ? '+' : '-'}
                      {formatAmount(transaction.amount)}
                    </p>
                  </div>
                </div>
                
                {transaction.account && (
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    <Badge variant="outline" className="font-mono">
                      {transaction.account.account_number}
                    </Badge>
                    <span className="text-gray-600">
                      {transaction.account.account_name}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <AlertCircle className="h-4 w-4" />
            <span>
              Transactions with assigned accounts will be validated
            </span>
          </div>
          <Button
            onClick={validateSelected}
            disabled={validating || selectedTransactions.size === 0}
          >
            {validating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Validating...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4 mr-2" />
                Validate Selected ({selectedTransactions.size})
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
