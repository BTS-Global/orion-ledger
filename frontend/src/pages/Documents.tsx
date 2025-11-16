import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from 'sonner';
import { TransactionReviewModal } from '@/components/TransactionReviewModal';
import { useCsrfToken, getCsrfTokenFromCookie } from '@/hooks/useCsrfToken';
import { InfoTooltip } from "@/components/InfoTooltip";
import { DOCUMENT_UPLOAD_TOOLTIPS } from "@/lib/tooltips";
import { Search, FileText, Upload, ChevronLeft, ChevronRight } from "lucide-react";
import { BACKEND_URL } from '@/config/api';

interface Document {
  id: string;
  company: string;
  company_name: string;
  file_name: string;
  file_type: string;
  file_size: number;
  status: string;
  upload_date: string;
  processed_date: string | null;
  processing_result: any;
  file_path: string;
}

interface Company {
  id: string;
  name: string;
}

const STATUS_COLORS: Record<string, string> = {
  'PENDING': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'PROCESSING': 'bg-blue-100 text-blue-800 border-blue-300',
  'COMPLETED': 'bg-green-100 text-green-800 border-green-300',
  'FAILED': 'bg-red-100 text-red-800 border-red-300',
};

const FILE_TYPE_ICONS: Record<string, string> = {
  'PDF': '📄',
  'CSV': '📊',
  'IMAGE': '🖼️',
  'JPG': '🖼️',
  'JPEG': '🖼️',
  'PNG': '🖼️',
};

export default function Documents() {
  const csrfToken = useCsrfToken();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  
  // Delete confirmation
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<{id: string, name: string} | null>(null);

  useEffect(() => {
    fetchCompanies();
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    filterDocuments();
  }, [documents, searchQuery, statusFilter, typeFilter]);

  const fetchCompanies = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/companies/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const companyList = data.results || data || [];
        setCompanies(companyList);
        if (companyList.length > 0 && !selectedCompany) {
          setSelectedCompany(companyList[0].id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch companies:', error);
      toast.error('Failed to load companies');
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/documents/`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const docList = data.results || data || [];
        setDocuments(docList);
        setLoading(false);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setLoading(false);
    }
  };

  const filterDocuments = () => {
    let filtered = [...documents];
    
    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(doc =>
        doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }
    
    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(doc => doc.file_type === typeFilter);
    }
    
    setFilteredDocuments(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    if (!selectedCompany) {
      toast.error('Please select a company first');
      return;
    }

    setUploading(true);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // Validate file type
      const validTypes = ['application/pdf', 'text/csv', 'image/png', 'image/jpeg', 'image/jpg'];
      if (!validTypes.includes(file.type)) {
        toast.error(`Invalid file type: ${file.name}. Only PDF, CSV, and images are allowed.`);
        continue;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`File too large: ${file.name}. Maximum size is 10MB.`);
        continue;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('company', selectedCompany);

      try {
        const token = csrfToken || getCsrfTokenFromCookie();
        const response = await fetch(`${BACKEND_URL}/api/documents/upload/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': token,
          },
          body: formData,
          credentials: 'include',
        });

        if (response.ok) {
          toast.success(`Uploaded ${file.name}`);
        } else {
          const error = await response.json();
          toast.error(`Failed to upload ${file.name}: ${error.detail || 'Unknown error'}`);
        }
      } catch (error) {
        console.error('Upload error:', error);
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    setUploading(false);
    fetchDocuments();
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const handleRetry = async (id: string) => {
    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/documents/${id}/reprocess/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      if (response.ok) {
        toast.success('Document reprocessing started');
        fetchDocuments();
      } else {
        toast.error('Failed to reprocess document');
      }
    } catch (error) {
      console.error('Reprocess error:', error);
      toast.error('Failed to reprocess document');
    }
  };

  const confirmDelete = (id: string, name: string) => {
    setDocumentToDelete({ id, name });
    setDeleteDialogOpen(true);
  };

  const handleDelete = async () => {
    if (!documentToDelete) return;

    try {
      const token = csrfToken || getCsrfTokenFromCookie();
      const response = await fetch(`${BACKEND_URL}/api/documents/${documentToDelete.id}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': token,
        },
        credentials: 'include',
      });

      if (response.ok) {
        toast.success('Document deleted!');
        fetchDocuments();
      } else {
        toast.error('Failed to delete document');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete document');
    }

    setDeleteDialogOpen(false);
    setDocumentToDelete(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  // Pagination
  const totalPages = Math.ceil(filteredDocuments.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedDocuments = filteredDocuments.slice(startIndex, endIndex);

  const uniqueTypes = Array.from(new Set(documents.map(d => d.file_type)));

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            Documents
            <InfoTooltip content={DOCUMENT_UPLOAD_TOOLTIPS.title} />
          </h1>
          <p className="text-gray-600">Upload and process bank statements and receipts</p>
        </div>
        <Button onClick={() => document.getElementById('file-input')?.click()}>
          <Upload className="mr-2 h-4 w-4" />
          Upload Document
        </Button>
      </div>

      {/* Company Selection */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <Label>Select Company ({companies.length} available)</Label>
            <Select value={selectedCompany} onValueChange={setSelectedCompany}>
              <SelectTrigger>
                <SelectValue placeholder="Select a company" />
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
        </CardContent>
      </Card>

      {/* Upload Area - Collapsible */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Upload Documents
            <InfoTooltip content={DOCUMENT_UPLOAD_TOOLTIPS.uploadArea} />
          </CardTitle>
          <CardDescription>
            Drag and drop files or click to browse. Supports PDF, CSV, and images.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <input
            id="file-input"
            type="file"
            multiple
            accept=".pdf,.csv,.jpg,.jpeg,.png"
            onChange={(e) => handleFileUpload(e.target.files)}
            className="hidden"
          />
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-700">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 mt-2">
              PDF, CSV, PNG, JPG (max 10MB each)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by filename..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="PENDING">Pending</SelectItem>
                  <SelectItem value="PROCESSING">Processing</SelectItem>
                  <SelectItem value="COMPLETED">Completed</SelectItem>
                  <SelectItem value="FAILED">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {uniqueTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Uploaded Documents ({filteredDocuments.length})</CardTitle>
            {filteredDocuments.length > 0 && (
              <p className="text-sm text-gray-500">
                Showing {startIndex + 1}-{Math.min(endIndex, filteredDocuments.length)} of {filteredDocuments.length}
              </p>
            )}
          </div>
          <CardDescription>View and manage your uploaded documents</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-12">
              <p className="text-gray-500">Loading documents...</p>
            </div>
          ) : filteredDocuments.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p className="text-gray-500">No documents found</p>
              <p className="text-sm text-gray-400 mt-2">
                {searchQuery || statusFilter !== 'all' || typeFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Upload your first document to get started'}
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {paginatedDocuments.map((doc) => (
                  <div
                    key={doc.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4 flex-1">
                        <div className="text-4xl">{FILE_TYPE_ICONS[doc.file_type] || '📄'}</div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-lg truncate">{doc.file_name}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge className={STATUS_COLORS[doc.status]}>{doc.status}</Badge>
                            <Badge variant="outline">{doc.file_type}</Badge>
                          </div>
                          <div className="text-sm text-gray-600 mt-2 space-y-1">
                            <p><strong>Company:</strong> {doc.company_name}</p>
                            <p><strong>Size:</strong> {formatFileSize(doc.file_size)}</p>
                            <p><strong>Uploaded:</strong> {formatDate(doc.upload_date)}</p>
                            {doc.processed_date && (
                              <p><strong>Processed:</strong> {formatDate(doc.processed_date)}</p>
                            )}
                            {doc.processing_result && doc.processing_result.transactions_count > 0 && (
                              <p className="text-green-600 font-medium">
                                ✓ Extracted {doc.processing_result.transactions_count} transactions
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            // Handle both absolute and relative paths
                            const filePath = doc.file_path.startsWith('/')
                              ? `${BACKEND_URL}${doc.file_path}`
                              : `${BACKEND_URL}/${doc.file_path}`;
                            window.open(filePath, '_blank');
                          }}
                        >
                          View Document
                        </Button>
                        
                        {doc.status === 'COMPLETED' && doc.processing_result && doc.processing_result.transactions_count > 0 && (
                          <Button
                            size="sm"
                            onClick={() => setSelectedDocument(doc)}
                          >
                            View Extracted Data
                          </Button>
                        )}
                        
                        {doc.status === 'FAILED' && (
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleRetry(doc.id)}
                          >
                            Retry
                          </Button>
                        )}
                        
                        {doc.status === 'COMPLETED' && (!doc.processing_result || doc.processing_result.transactions_count === 0) && (
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleRetry(doc.id)}
                          >
                            Extract Data
                          </Button>
                        )}
                        
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => confirmDelete(doc.id, doc.file_name)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4 mr-2" />
                    Previous
                  </Button>
                  <div className="flex items-center gap-2">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                      <Button
                        key={page}
                        variant={currentPage === page ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(page)}
                      >
                        {page}
                      </Button>
                    ))}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete "{documentToDelete?.name}". This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Transaction Review Modal */}
      {selectedDocument && (
        <TransactionReviewModal
          document={selectedDocument}
          onClose={() => setSelectedDocument(null)}
          onImportComplete={() => {
            setSelectedDocument(null);
            fetchDocuments();
          }}
          csrfToken={csrfToken}
        />
      )}
    </div>
  );
}

