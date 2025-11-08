import PaginationComponent from "@/components/Profile/Pagination";

type BaseRecord = {
  _id: string;
  created_at: string;
};

type FilteredRecordsListProps<T extends BaseRecord> = {
  title: string;
  records: T[];
  currentPage: number;
  totalPages: number;
  itemsPerPage?: number;
  onPageChange: (page: number) => void;
  onClearFilter: () => void;
  onRecordClick?: (record: T) => void;
  renderText: (record: T) => string;
};

function FilteredRecordsList<T extends BaseRecord>({
  title,
  records,
  currentPage,
  totalPages,
  itemsPerPage = 5,
  onPageChange,
  onClearFilter,
  onRecordClick,
  renderText,
}: FilteredRecordsListProps<T>) {
  // Paginate records
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  const paginatedRecords = records.slice(start, end);

  // limited text length
  const truncateText = (text: string, maxLength: number = 60) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  return (
    <div className="mt-6 border border-gray-300 dark:border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-md font-semibold">
          {title} ({records.length})
        </h3>
        <button
          onClick={onClearFilter}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          Clear Filter
        </button>
      </div>

      <div className="space-y-2">
        {paginatedRecords.length > 0 ? (
          paginatedRecords.map((record) => {
            // Fix overflow bug
            const displayText = truncateText(renderText(record), 60);
            
            return (
              <div
                key={record._id}
                onClick={() => onRecordClick?.(record)}
                className={`p-3 rounded-md border border-gray-200 dark:border-border hover:bg-muted transition-colors ${
                  onRecordClick ? "cursor-pointer" : ""
                }`}
              >
                <p className="text-sm font-medium">
                  {displayText}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(record.created_at).toLocaleString()}
                </p>
              </div>
            );
          })
        ) : (
          <p className="text-center text-muted-foreground py-8">
            No records found
          </p>
        )}
      </div>

      {totalPages > 1 && (
        <div className="mt-4">
          <PaginationComponent
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
}

export default FilteredRecordsList;