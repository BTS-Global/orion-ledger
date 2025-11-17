import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { BACKEND_URL } from '@/config/api';
import { getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';
import logger from '@/utils/logger';

interface Transaction {
  date: string;
  description: string;
  amount: number;
  category?: string;
  account?: string;
  selected: boolean;
}

interface Account {
  id: string;
  account_code: string;
  account_name: string;
  account_type: string;
}

interface Props {
  document: any;
  onClose: () => void;
  onImportComplete?: () => void;
  csrfToken?: string;
}

export function TransactionReviewModal({ document, onClose, onImportComplete, csrfToken }: Props) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    // Initialize transactions from document
    const extracted = document.processing_result?.transactions || [];
    setTransactions(extracted.map((t: any) => ({
      ...t,
      selected: true,
      account: ''
    })));

    // Fetch accounts
    fetchAccounts();
  }, [document]);

  const fetchAccounts = async () => {
    try {
      logger.dev('Fetching accounts from API');
      const response = await fetch(`${BACKEND_URL}/api/accounts/`, {
        credentials: 'include',
      });
      const data = await response.json();
      const accountsList = data.results || data || [];
      logger.dev('Loaded accounts:', accountsList.length);
      setAccounts(accountsList);
    } catch (error) {
      logger.error('Failed to fetch accounts:', error);
      toast.error('Failed to load accounts');
    }
  };

  const handleToggleSelect = (index: number) => {
    setTransactions(prev => prev.map((t, i) => 
      i === index ? { ...t, selected: !t.selected } : t
    ));
  };

  const handleToggleAll = () => {
    const allSelected = transactions.every(t => t.selected);
    setTransactions(prev => prev.map(t => ({ ...t, selected: !allSelected })));
  };

  const handleUpdateTransaction = (index: number, field: string, value: any) => {
    logger.dev('Updating transaction', { index, field, value });
    setTransactions(prev => {
      const updated = prev.map((t, i) => 
        i === index ? { ...t, [field]: value } : t
      );
      return updated;
    });
  };

  const handleImport = async () => {
    logger.dev('Starting transaction import');
    const selected = transactions.filter(t => t.selected);
    
    if (selected.length === 0) {
      toast.error('Please select at least one transaction to import');
      return;
    }

    // Validate that all selected transactions have accounts
    const missingAccounts = selected.filter(t => !t.account);
    if (missingAccounts.length > 0) {
      toast.error(`Please select an account for all ${missingAccounts.length} transaction(s)`);
      return;
    }

    setImporting(true);

    try {
      // Import each transaction
      let successCount = 0;
      let failCount = 0;

      for (const trans of selected) {
        try {
          const token = csrfToken || getCsrfTokenFromCookie();
          const response = await fetch(`${BACKEND_URL}/api/transactions/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': token,
            },
            credentials: 'include',
            body: JSON.stringify({
              company: document.company,
              date: trans.date,
              description: trans.description,
              amount: Math.abs(trans.amount),
              transaction_type: trans.amount < 0 ? 'EXPENSE' : 'INCOME',
              account: trans.account,
              status: 'PENDING',
              document: document.id,
            }),
          });

          if (response.ok) {
            successCount++;
          } else {
            failCount++;
            const error = await response.json();
            logger.error('Failed to import transaction', error);
          }
        } catch (error) {
          failCount++;
          logger.error('Error importing transaction', error);
        }
      }

      if (successCount > 0) {
        toast.success(`Successfully imported ${successCount} transaction(s)!`);
        if (onImportComplete) {
          onImportComplete();
        }
        onClose();
      }

      if (failCount > 0) {
        toast.error(`Failed to import ${failCount} transaction(s)`);
      }
    } catch (error) {
      logger.error('Import error', error);
      toast.error('Failed to import transactions');
    } finally {
      setImporting(false);
    }
  };

  const selectedCount = transactions.filter(t => t.selected).length;
  const totalAmount = transactions
    .filter(t => t.selected)
    .reduce((sum, t) => sum + t.amount, 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold">{document.file_name}</h2>
            <p className="text-gray-600">
              Review and import {document.processing_result?.transactions_count || 0} extracted transactions
            </p>
          </div>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </div>

        {/* Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">{selectedCount}</div>
              <div className="text-sm text-gray-600">Selected</div>
            </div>
            <div>
              <div className={`text-2xl font-bold ${totalAmount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${Math.abs(totalAmount).toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Total Amount</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-700">{accounts.length}</div>
              <div className="text-sm text-gray-600">Accounts Available</div>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="overflow-x-auto mb-4">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-3">
                  <input
                    type="checkbox"
                    checked={transactions.every(t => t.selected)}
                    onChange={handleToggleAll}
                    className="rounded"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account *</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.map((trans, idx) => (
                <tr key={idx} className={trans.selected ? 'bg-blue-50' : 'bg-white'}>
                  <td className="px-3 py-3">
                    <input
                      type="checkbox"
                      checked={trans.selected}
                      onChange={() => handleToggleSelect(idx)}
                      className="rounded"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="date"
                      value={trans.date}
                      onChange={(e) => handleUpdateTransaction(idx, 'date', e.target.value)}
                      className="border rounded px-2 py-1 text-sm w-full"
                      disabled={!trans.selected}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={trans.description}
                      onChange={(e) => handleUpdateTransaction(idx, 'description', e.target.value)}
                      className="border rounded px-2 py-1 text-sm w-full"
                      disabled={!trans.selected}
                    />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <input
                      type="number"
                      step="0.01"
                      value={Math.abs(trans.amount)}
                      onChange={(e) => {
                        const parsed = parseFloat(e.target.value);
                        if (isNaN(parsed)) return;
                        const newAmount = parsed * (trans.amount < 0 ? -1 : 1);
                        handleUpdateTransaction(idx, 'amount', newAmount);
                      }}
                      className={`border rounded px-2 py-1 text-sm w-24 text-right font-medium ${
                        trans.amount < 0 ? 'text-red-600' : 'text-green-600'
                      }`}
                      disabled={!trans.selected}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      trans.amount < 0 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {trans.amount < 0 ? 'EXPENSE' : 'INCOME'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Select
                      value={trans.account || ''}
                      onValueChange={(value) => {
                        handleUpdateTransaction(idx, 'account', value);
                      }}
                      disabled={!trans.selected}
                    >
                      <SelectTrigger 
                        size="sm"
                        className={`w-full ${
                          !trans.account && trans.selected ? 'border-red-300' : ''
                        }`}
                      >
                        <SelectValue placeholder="Select account..." />
                      </SelectTrigger>
                      <SelectContent>
                        {accounts.map(acc => (
                          <SelectItem key={acc.id} value={acc.id}>
                            {acc.account_code} - {acc.account_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="text-sm text-gray-600">
            * Account is required for all selected transactions
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} disabled={importing}>
              Cancel
            </Button>
            <Button
              onClick={handleImport}
              disabled={importing || selectedCount === 0}
            >
              {importing ? 'Importing...' : `Import ${selectedCount} Transaction(s)`}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

