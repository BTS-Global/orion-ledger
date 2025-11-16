import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle2, XCircle, Edit, Trash2, RefreshCw } from "lucide-react";
import { BACKEND_URL } from "@/config/api";

interface Transaction {
  id: string;
  company: string;
  document: string | null;
  date: string;
  description: string;
  amount: string;
  category: string | null;
  account: string | null;
  is_validated: boolean;
  suggested_category: string | null;
  confidence_score: number;
  notes: string | null;
}

interface Company {
  id: string;
  name: string;
}

interface Account {
  id: string;
  account_number: string;
  account_name: string;
  account_type: string;
}

export default function Transactions() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null);
  const [editForm, setEditForm] = useState({
    date: "",
    description: "",
    amount: "",
    category: "",
    account: "",
    notes: "",
  });

  useEffect(() => {
    fetchCompanies();
    fetchAccounts();
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      fetchTransactions();
    }
  }, [selectedCompany, filterStatus]);

  const fetchCompanies = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/companies/`);
      const data = await response.json();
      const companies = data.results || data || [];
      setCompanies(companies);
      if (companies.length > 0) {
        setSelectedCompany(companies[0].id);
      }
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const fetchAccounts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/accounts/`);
      const data = await response.json();
      setAccounts(data.results || data || []);
    } catch (error) {
      console.error("Error fetching accounts:", error);
    }
  };

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      let url = `${BACKEND_URL}/api/transactions/?company=${selectedCompany}`;
      if (filterStatus === "validated") {
        url += "&is_validated=true";
      } else if (filterStatus === "pending") {
        url += "&is_validated=false";
      }
      
      const response = await fetch(url);
      const data = await response.json();
      setTransactions(data.results || data || []);
    } catch (error) {
      console.error("Error fetching transactions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setSelectedTransaction(transaction);
    setEditForm({
      date: transaction.date,
      description: transaction.description,
      amount: transaction.amount,
      category: transaction.category || "",
      account: transaction.account || "",
      notes: transaction.notes || "",
    });
    setEditDialogOpen(true);
  };

  const handleSaveEdit = async () => {
    if (!selectedTransaction) return;

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/transactions/${selectedTransaction.id}/`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(editForm),
        }
      );

      if (response.ok) {
        setEditDialogOpen(false);
        fetchTransactions();
      }
    } catch (error) {
      console.error("Error updating transaction:", error);
    }
  };

  const handleValidate = async (transactionId: string) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/transactions/${transactionId}/validate/`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        fetchTransactions();
      }
    } catch (error) {
      console.error("Error validating transaction:", error);
    }
  };

  const handleDelete = async (transactionId: string) => {
    if (!confirm("Tem certeza que deseja deletar esta transação?")) return;

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/transactions/${transactionId}/`,
        {
          method: "DELETE",
        }
      );

      if (response.ok) {
        fetchTransactions();
      }
    } catch (error) {
      console.error("Error deleting transaction:", error);
    }
  };

  const handleBulkValidate = async () => {
    const unvalidatedIds = transactions
      .filter((t) => !t.is_validated)
      .map((t) => t.id);

    if (unvalidatedIds.length === 0) {
      alert("Nenhuma transação pendente para validar");
      return;
    }

    if (!confirm(`Validar ${unvalidatedIds.length} transações?`)) return;

    for (const id of unvalidatedIds) {
      await handleValidate(id);
    }
  };

  const formatCurrency = (value: string) => {
    const num = parseFloat(value);
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(num);
  };

  const getConfidenceBadge = (score: number) => {
    if (score >= 0.8) return <Badge className="bg-green-500">Alta</Badge>;
    if (score >= 0.5) return <Badge className="bg-yellow-500">Média</Badge>;
    return <Badge className="bg-red-500">Baixa</Badge>;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Transações</h1>
          <p className="text-gray-600 mt-2">
            Valide e gerencie transações extraídas dos documentos
          </p>
        </div>

        {/* Filters */}
        <Card className="p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>Empresa</Label>
              <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma empresa" />
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
              <Label>Status</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="pending">Pendentes</SelectItem>
                  <SelectItem value="validated">Validadas</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end gap-2">
              <Button onClick={fetchTransactions} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
              <Button onClick={handleBulkValidate}>
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Validar Todas
              </Button>
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4">
            <div className="text-sm text-gray-600">Total</div>
            <div className="text-2xl font-bold">{transactions.length}</div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-gray-600">Pendentes</div>
            <div className="text-2xl font-bold text-yellow-600">
              {transactions.filter((t) => !t.is_validated).length}
            </div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-gray-600">Validadas</div>
            <div className="text-2xl font-bold text-green-600">
              {transactions.filter((t) => t.is_validated).length}
            </div>
          </Card>
          <Card className="p-4">
            <div className="text-sm text-gray-600">Total (USD)</div>
            <div className="text-2xl font-bold">
              {formatCurrency(
                transactions
                  .reduce((sum, t) => sum + parseFloat(t.amount), 0)
                  .toString()
              )}
            </div>
          </Card>
        </div>

        {/* Transactions Table */}
        <Card>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Descrição</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Categoria</TableHead>
                  <TableHead>Conta</TableHead>
                  <TableHead>Confiança</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8">
                      Carregando...
                    </TableCell>
                  </TableRow>
                ) : transactions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8">
                      Nenhuma transação encontrada
                    </TableCell>
                  </TableRow>
                ) : (
                  transactions.map((transaction) => (
                    <TableRow key={transaction.id}>
                      <TableCell>
                        {new Date(transaction.date).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {transaction.description}
                      </TableCell>
                      <TableCell
                        className={
                          parseFloat(transaction.amount) >= 0
                            ? "text-green-600 font-semibold"
                            : "text-red-600 font-semibold"
                        }
                      >
                        {formatCurrency(transaction.amount)}
                      </TableCell>
                      <TableCell>
                        {transaction.category || transaction.suggested_category || (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {transaction.account ? (
                          <span className="text-sm">
                            {accounts.find((a) => a.id === transaction.account)
                              ?.account_name || transaction.account}
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {getConfidenceBadge(transaction.confidence_score)}
                      </TableCell>
                      <TableCell>
                        {transaction.is_validated ? (
                          <Badge className="bg-green-500">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Validada
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            <XCircle className="h-3 w-3 mr-1" />
                            Pendente
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(transaction)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          {!transaction.is_validated && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleValidate(transaction.id)}
                            >
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleDelete(transaction.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </Card>

        {/* Edit Dialog */}
        <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Editar Transação</DialogTitle>
              <DialogDescription>
                Edite os detalhes da transação e associe a uma conta contábil
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="date">Data</Label>
                  <Input
                    id="date"
                    type="date"
                    value={editForm.date}
                    onChange={(e) =>
                      setEditForm({ ...editForm, date: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="amount">Valor</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={editForm.amount}
                    onChange={(e) =>
                      setEditForm({ ...editForm, amount: e.target.value })
                    }
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="description">Descrição</Label>
                <Input
                  id="description"
                  value={editForm.description}
                  onChange={(e) =>
                    setEditForm({ ...editForm, description: e.target.value })
                  }
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category">Categoria</Label>
                  <Input
                    id="category"
                    value={editForm.category}
                    onChange={(e) =>
                      setEditForm({ ...editForm, category: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="account">Conta Contábil</Label>
                  <Select
                    value={editForm.account}
                    onValueChange={(value) =>
                      setEditForm({ ...editForm, account: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione uma conta" />
                    </SelectTrigger>
                    <SelectContent>
                      {accounts.map((account) => (
                        <SelectItem key={account.id} value={account.id}>
                          {account.account_number} - {account.account_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="notes">Notas</Label>
                <Textarea
                  id="notes"
                  value={editForm.notes}
                  onChange={(e) =>
                    setEditForm({ ...editForm, notes: e.target.value })
                  }
                  rows={3}
                />
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveEdit}>Salvar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}

