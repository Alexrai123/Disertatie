// Reusable UI Components
import React from 'react';

// Loading Spinner Component
export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
    const sizeClass = size === 'sm' ? 'spinner-sm' : '';
    return (
        <div className={`spinner ${sizeClass}`} role="status" aria-label="Loading">
            <span className="sr-only">Loading...</span>
        </div>
    );
};

// Loading Container
export const LoadingContainer: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => {
    return (
        <div className="loading-container">
            <Spinner />
            <p className="text-muted">{message}</p>
        </div>
    );
};

// Alert Component
interface AlertProps {
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({ type, message, onClose }) => {
    return (
        <div className={`alert alert-${type}`} role="alert">
            <div style={{ flex: 1 }}>{message}</div>
            {onClose && (
                <button
                    onClick={onClose}
                    className="btn btn-sm btn-secondary"
                    aria-label="Close alert"
                >
                    ×
                </button>
            )}
        </div>
    );
};

// Card Component
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    title?: string;
    children: React.ReactNode;
    actions?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, children, actions, className, ...rest }) => {
    return (
        <div className={`card ${className || ''}`} {...rest}>
            {title && (
                <div className="card-header">
                    <h3 className="card-title">{title}</h3>
                    {actions && <div>{actions}</div>}
                </div>
            )}
            <div className="card-body">{children}</div>
        </div>
    );
};

// Badge Component
interface BadgeProps {
    type: 'success' | 'warning' | 'danger' | 'info' | 'primary';
    children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ type, children }) => {
    return <span className={`badge badge-${type}`}>{children}</span>;
};

// Empty State Component
interface EmptyStateProps {
    icon?: string;
    title: string;
    message?: string;
    action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon = '📭', title, message, action }) => {
    return (
        <div className="empty-state">
            <div className="empty-state-icon">{icon}</div>
            <h3>{title}</h3>
            {message && <p className="text-muted">{message}</p>}
            {action && <div className="mt-2">{action}</div>}
        </div>
    );
};

// Pagination Component
interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    hasMore?: boolean;
}

export const Pagination: React.FC<PaginationProps> = ({
    currentPage,
    totalPages,
    onPageChange,
    hasMore = false,
}) => {
    return (
        <div className="pagination">
            <button
                className="pagination-btn"
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
            >
                ← Previous
            </button>

            <span className="text-muted">
                Page {currentPage} {totalPages > 0 && `of ${totalPages}`}
            </span>

            <button
                className="pagination-btn"
                onClick={() => onPageChange(currentPage + 1)}
                disabled={!hasMore && currentPage >= totalPages}
            >
                Next →
            </button>
        </div>
    );
};

// Table Component
interface Column<T> {
    key: string;
    header: string;
    render?: (item: T) => React.ReactNode;
}

interface TableProps<T> {
    columns: Column<T>[];
    data: T[];
    loading?: boolean;
    emptyMessage?: string;
}

export function Table<T extends Record<string, any>>({
    columns,
    data,
    loading = false,
    emptyMessage = 'No data available',
}: TableProps<T>) {
    if (loading) {
        return <LoadingContainer message="Loading data..." />;
    }

    if (data.length === 0) {
        return <EmptyState title={emptyMessage} icon="📊" />;
    }

    return (
        <div className="table-container">
            <table className="table">
                <thead>
                    <tr>
                        {columns.map((col) => (
                            <th key={col.key}>{col.header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, idx) => (
                        <tr key={idx}>
                            {columns.map((col) => (
                                <td key={col.key}>
                                    {col.render ? col.render(item) : item[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

// Error Boundary Component
interface ErrorBoundaryProps {
    children: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="main-content">
                    <Card title="Something went wrong">
                        <Alert
                            type="error"
                            message={this.state.error?.message || 'An unexpected error occurred'}
                        />
                        <button
                            className="btn btn-primary mt-2"
                            onClick={() => window.location.reload()}
                        >
                            Reload Page
                        </button>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

// Modal Component
interface ModalProps {
    isOpen: boolean;
    title: string;
    children: React.ReactNode;
    onClose: () => void;
    onConfirm?: () => void;
    confirmText?: string;
    cancelText?: string;
    confirmType?: 'primary' | 'danger' | 'success';
}

export const Modal: React.FC<ModalProps> = ({
    isOpen,
    title,
    children,
    onClose,
    onConfirm,
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    confirmType = 'primary',
}) => {
    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal" role="dialog" aria-modal="true">
                <div className="modal-header">
                    <h3 className="modal-title">{title}</h3>
                    <button
                        onClick={onClose}
                        className="btn btn-sm btn-secondary"
                        aria-label="Close modal"
                    >
                        ×
                    </button>
                </div>
                <div className="modal-body">{children}</div>
                <div className="modal-footer">
                    <button onClick={onClose} className="btn btn-secondary">
                        {cancelText}
                    </button>
                    {onConfirm && (
                        <button
                            onClick={onConfirm}
                            className={`btn btn-${confirmType}`}
                        >
                            {confirmText}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};
