import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { BACKEND_URL } from '@/config/api';
import { getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';
import { CheckCircle2, XCircle, AlertCircle, Edit, Trash2 } from 'lucide-react';

interface Transaction {
  date: string;
  description: string;
  amount: number;
  category?: string;
  confidence?: number;
  vendor?: string;
}

interface Account {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
}

interface ExtractedData {
  transactions: Transaction[];
  validation?: {
    valid_count: number;
    invalid_count: number;
    total: number;
    errors: any[];
  };
}

interface Props {
  documentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm?: () => void;
}

export function TransactionReviewModal({ documentId, open, onOpenChange, onConfirm }: Props) {
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    if (open && documentId) {
      fetchExtractedData();
      fetchAccounts();
    }
  }, [open, documentId]);

  const fetchExtractedData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/documents/${documentId}/extracted_data/`, {
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setExtractedData(data);
        setTransactions(data.transactions || []);
        
        // Select all valid transactions by default
        const validIndices = new Set<number>();
        data.transactions?.forEach((t: Transaction, idx: number) => {
          validIndices.add(idx);
        });
        setSelectedIndices(validIndices);
      } else {
        toast.error('Failed to load extracted data');
      }
    } catch (error) {
      console.error('Error fetching extracted data:', error);
      toast.error('Failed to load extracted data');
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/accounts/`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.results || data || []);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const handleToggleTransaction = (index: number) => {
    const newSelected = new Set(selectedIndices);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedIndices(newSelected);
  };

  const handleToggleAll = () => {
    if (selectedIndices.size === transactions.length) {
      setSelectedIndices(new Set());
    } else {
      setSelectedIndices(new Set(transactions.map((_, idx) => idx)));
    }
  };

  const handleEditTransaction = (index: number, field: string, value: any) => {
    setTransactions(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleDeleteTransaction = (index: number) => {
    setTransactions(prev => prev.filter((_, idx) => idx !== index));
    const newSelected = new Set(selectedIndices);
    newSelected.delete(index);
    // Adjust indices for remaining items
    const adjustedSelected = new Set<number>();
    newSelected.forEach(idx => {
      if (idx > index) {
        adjustedSelected.add(idx - 1);
      } else if (idx < index) {
        adjustedSelected.add(idx);
      }
    });
    setSelectedIndices(adjustedSelected);
  };

  const handleConfirm = async () => {
    if (selectedIndices.size === 0) {
      toast.error('Please select at least one transaction');
      return;
    }

    setConfirming(true);
    try {
      const selectedTransactions = transactions.filter((_, idx) => selectedIndices.has(idx));

      const token = getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/documents/${documentId}/confirm_transactions/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        credentials: 'include',
        body: JSON.stringify({
          transactions: selectedTransactions
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message || 'Transactions confirmed successfully');
        onOpenChange(false);
        onConfirm?.();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to confirm transactions');
      }
    } catch (error) {
      console.error('Error confirming transactions:', error);
      toast.error('Failed to confirm transactions');
    } finally {
      setConfirming(false);
    }
  };

  const handleReject = async () => {
    try {
      const token = getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/documents/${documentId}/reject_transactions/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      if (response.ok) {
        toast.success('Transactions rejected');
        onOpenChange(false);
        onConfirm?.();
      } else {
        toast.error('Failed to reject transactions');
      }
    } catch (error) {
      console.error('Error rejecting transactions:', error);
      toast.error('Failed to reject transactions');
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'bg-gray-100 text-gray-800';
    if (confidence >= 0.8) return 'bg-green-100 text-green-800';
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const getConfidenceLabel = (confidence?: number) => {
    if (!confidence) return 'Unknown';
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.5) return 'Medium';
    return 'Low';
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Review Extracted Transactions</DialogTitle>
          <DialogDescription>
            Review and edit the transactions extracted from the document. Select the transactions you want to import.
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="py-8 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading extracted data...</p>
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4 py-4">
              <div className="rounded-lg border p-4">
                <div className="text-2xl font-bold">{transactions.length}</div>
                <div className="text-sm text-muted-foreground">Total Transactions</div>
              </div>
              <div className="rounded-lg border p-4">
                <div className="text-2xl font-bold">{selectedIndices.size}</div>
                <div className="text-sm text-muted-foreground">Selected</div>
              </div>
              {extractedData?.validation && (
                <div className="rounded-lg border p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {extractedData.validation.valid_count}
                  </div>
                  <div className="text-sm text-muted-foreground">Valid</div>
                </div>
              )}
            </div>

            {/* Bulk Actions */}
            <div className="flex items-center justify-between border-b pb-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  checked={selectedIndices.size === transactions.length}
                  onCheckedChange={handleToggleAll}
                  id="select-all"
                />
                <Label htmlFor="select-all" className="cursor-pointer">
                  Select All
                </Label>
              </div>
              <div className="text-sm text-muted-foreground">
                {selectedIndices.size} of {transactions.length} selected
              </div>
            </div>

            {/* Transactions List */}
            <ScrollArea className="h-[400px] pr-4">
              <div className="space-y-4">
                {transactions.map((transaction, index) => (
                  <div
                    key={index}
                    className={`rounded-lg border p-4 transition-colors ${
                      selectedIndices.has(index) ? 'border-primary bg-primary/5' : ''
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <Checkbox
                        checked={selectedIndices.has(index)}
                        onCheckedChange={() => handleToggleTransaction(index)}
                        className="mt-1"
                      />

                      <div className="flex-1 space-y-3">
                        {/* Header Row */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Transaction #{index + 1}</span>
                            {transaction.confidence && (
                              <Badge className={getConfidenceColor(transaction.confidence)}>
                                {getConfidenceLabel(transaction.confidence)} (
                                {Math.round(transaction.confidence * 100)}%)
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setEditingIndex(editingIndex === index ? null : index)
                              }
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteTransaction(index)}
                            >
                              <Trash2 className="h-4 w-4 text-red-500" />
                            </Button>
                          </div>
                        </div>

                        {/* Transaction Details */}
                        {editingIndex === index ? (
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <Label>Date</Label>
                              <Input
                                type="date"
                                value={transaction.date}
                                onChange={(e) =>
                                  handleEditTransaction(index, 'date', e.target.value)
                                }
                              />
                            </div>
                            <div>
                              <Label>Amount</Label>
                              <Input
                                type="number"
                                step="0.01"
                                value={transaction.amount}
                                onChange={(e) =>
                                  handleEditTransaction(
                                    index,
                                    'amount',
                                    parseFloat(e.target.value)
                                  )
                                }
                              />
                            </div>
                            <div className="col-span-2">
                              <Label>Description</Label>
                              <Input
                                value={transaction.description}
                                onChange={(e) =>
                                  handleEditTransaction(index, 'description', e.target.value)
                                }
                              />
                            </div>
                            <div>
                              <Label>Category</Label>
                              <Input
                                value={transaction.category || ''}
                                onChange={(e) =>
                                  handleEditTransaction(index, 'category', e.target.value)
                                }
                              />
                            </div>
                            <div>
                              <Label>Vendor</Label>
                              <Input
                                value={transaction.vendor || ''}
                                onChange={(e) =>
                                  handleEditTransaction(index, 'vendor', e.target.value)
                                }
                              />
                            </div>
                          </div>
                        ) : (
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div>
                              <span className="text-muted-foreground">Date:</span>{' '}
                              <span className="font-medium">{transaction.date}</span>
                            </div>
                            <div>
                              <span className="text-muted-foreground">Amount:</span>{' '}
                              <span className={`font-medium ${transaction.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                ${Math.abs(transaction.amount).toFixed(2)}
                              </span>
                            </div>
                            <div className="col-span-2">
                              <span className="text-muted-foreground">Description:</span>{' '}
                              <span className="font-medium">{transaction.description}</span>
                            </div>
                            {transaction.category && (
                              <div>
                                <span className="text-muted-foreground">Category:</span>{' '}
                                <span className="font-medium">{transaction.category}</span>
                              </div>
                            )}
                            {transaction.vendor && (
                              <div>
                                <span className="text-muted-foreground">Vendor:</span>{' '}
                                <span className="font-medium">{transaction.vendor}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* Validation Errors */}
            {extractedData?.validation && extractedData.validation.errors.length > 0 && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  <span className="font-medium text-red-900">Validation Issues</span>
                </div>
                <div className="text-sm text-red-800 space-y-1">
                  {extractedData.validation.errors.slice(0, 3).map((error: any, idx: number) => (
                    <div key={idx}>
                      Transaction #{error.transaction_index + 1}: {error.errors.join(', ')}
                    </div>
                  ))}
                  {extractedData.validation.errors.length > 3 && (
                    <div>And {extractedData.validation.errors.length - 3} more...</div>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={handleReject} disabled={confirming}>
            Reject All
          </Button>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={confirming}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={confirming || selectedIndices.size === 0}>
            {confirming ? 'Confirming...' : `Confirm ${selectedIndices.size} Transactions`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
