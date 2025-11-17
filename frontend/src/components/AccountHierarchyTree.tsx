import { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, Folder, FolderOpen, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from 'sonner';
import { BACKEND_URL } from '@/config/api';
import logger from '@/utils/logger';

interface Account {
  id: string;
  account_number: string;
  account_name: string;
  account_type: string;
  balance: string;
  is_group_account: boolean;
  parent_account: string | null;
  level: number;
  has_children: boolean;
}

interface AccountNode extends Account {
  children: AccountNode[];
  expanded: boolean;
}

interface AccountHierarchyTreeProps {
  companyId: string;
  onAccountSelect?: (account: Account) => void;
  selectedAccountId?: string;
}

const TYPE_COLORS: Record<string, string> = {
  'ASSET': 'bg-green-100 text-green-800',
  'LIABILITY': 'bg-red-100 text-red-800',
  'EQUITY': 'bg-blue-100 text-blue-800',
  'REVENUE': 'bg-purple-100 text-purple-800',
  'EXPENSE': 'bg-orange-100 text-orange-800',
};

export function AccountHierarchyTree({ 
  companyId, 
  onAccountSelect,
  selectedAccountId 
}: AccountHierarchyTreeProps) {
  const [hierarchy, setHierarchy] = useState<AccountNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (companyId) {
      fetchHierarchy();
    }
  }, [companyId]);

  const fetchHierarchy = async () => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/accounts/hierarchy/?company=${companyId}`,
        { credentials: 'include' }
      );

      if (response.ok) {
        const data = await response.json();
        setHierarchy(buildTree(data));
      } else {
        toast.error('Failed to load account hierarchy');
      }
    } catch (error) {
      logger.error('Failed to fetch hierarchy', error);
      toast.error('Failed to load account hierarchy');
    } finally {
      setLoading(false);
    }
  };

  const buildTree = (accounts: Account[]): AccountNode[] => {
    const accountMap = new Map<string, AccountNode>();
    const roots: AccountNode[] = [];

    // First pass: create all nodes
    accounts.forEach(account => {
      accountMap.set(account.id, {
        ...account,
        children: [],
        expanded: false,
      });
    });

    // Second pass: build tree structure
    accounts.forEach(account => {
      const node = accountMap.get(account.id)!;
      if (account.parent_account) {
        const parent = accountMap.get(account.parent_account);
        if (parent) {
          parent.children.push(node);
        } else {
          roots.push(node);
        }
      } else {
        roots.push(node);
      }
    });

    return roots;
  };

  const toggleExpand = (node: AccountNode) => {
    node.expanded = !node.expanded;
    setHierarchy([...hierarchy]);
  };

  const formatBalance = (balance: string) => {
    const num = parseFloat(balance);
    return num.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    });
  };

  const renderNode = (node: AccountNode, depth: number = 0) => {
    const hasChildren = node.children.length > 0;
    const isSelected = node.id === selectedAccountId;

    return (
      <div key={node.id}>
        <div
          className={`flex items-center gap-2 py-2 px-3 hover:bg-gray-50 cursor-pointer border-l-2 transition-colors ${
            isSelected ? 'bg-blue-50 border-l-blue-500' : 'border-l-transparent'
          }`}
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
          onClick={() => onAccountSelect?.(node)}
        >
          {hasChildren ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleExpand(node);
              }}
              className="p-1 hover:bg-gray-200 rounded"
            >
              {node.expanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </button>
          ) : (
            <div className="w-6" />
          )}

          {node.is_group_account ? (
            node.expanded ? (
              <FolderOpen className="h-4 w-4 text-yellow-600" />
            ) : (
              <Folder className="h-4 w-4 text-yellow-600" />
            )
          ) : (
            <FileText className="h-4 w-4 text-gray-500" />
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm text-gray-600">
                {node.account_number}
              </span>
              <span className="font-medium truncate">{node.account_name}</span>
              <Badge className={`${TYPE_COLORS[node.account_type]} text-xs`}>
                {node.account_type}
              </Badge>
            </div>
          </div>

          <div className="font-mono text-sm font-medium">
            {formatBalance(node.balance)}
          </div>
        </div>

        {hasChildren && node.expanded && (
          <div>
            {node.children.map(child => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-sm text-gray-500 mt-4">Loading hierarchy...</p>
        </CardContent>
      </Card>
    );
  }

  if (hierarchy.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-500">No accounts found</p>
          <p className="text-sm text-gray-400 mt-2">
            Create accounts or initialize the default chart of accounts
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Account Hierarchy</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              const expandAll = (nodes: AccountNode[]) => {
                nodes.forEach(node => {
                  node.expanded = true;
                  if (node.children.length > 0) {
                    expandAll(node.children);
                  }
                });
              };
              expandAll(hierarchy);
              setHierarchy([...hierarchy]);
            }}
          >
            Expand All
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="border rounded-lg overflow-hidden">
          {hierarchy.map(node => renderNode(node))}
        </div>
      </CardContent>
    </Card>
  );
}
