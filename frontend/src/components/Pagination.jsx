import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ page, totalPages, hasNext, hasPrevious, onPageChange }) {
  if (totalPages <= 1) return null;

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={!hasPrevious}
        className="btn btn-secondary btn-sm"
        style={{ padding: '0.4rem 0.6rem' }}
      >
        <ChevronLeft size={16} />
        <span>Previous</span>
      </button>

      <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', padding: '0 0.5rem' }}>
        Page <strong>{page}</strong> of <strong>{totalPages}</strong>
      </span>

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={!hasNext}
        className="btn btn-secondary btn-sm"
        style={{ padding: '0.4rem 0.6rem' }}
      >
        <span>Next</span>
        <ChevronRight size={16} />
      </button>
    </div>
  );
}
