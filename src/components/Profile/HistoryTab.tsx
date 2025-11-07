import { TabsContent } from "@/components/ui/tabs";
import PaginationComponent from "./Pagination";

type HistoryTabContentProps = {
  tabValue: string;
  loading?: boolean;
  error?: string | null;
  items: any[];
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onItemClick?: (item: any) => void;
  getItemText: (item: any) => string;
};

const HistoryTabContent = ({
  tabValue,
  loading = false,
  error = null,
  items,
  currentPage,
  totalPages,
  onPageChange,
  onItemClick,
  getItemText,
}: HistoryTabContentProps) => {
  const itemsPerPage = 5;
  const getPaginatedItems = (itemsList: any[], page: number) => {
    const startIndex = (page - 1) * itemsPerPage;
    return itemsList.slice(startIndex, startIndex + itemsPerPage);
  };

  const paginatedItems = getPaginatedItems(items, currentPage);

  return (
    <TabsContent value={tabValue} className="mt-4">
      {loading && (
        <p className="text-sm text-muted-foreground">Loading...</p>
      )}
      {error && <p className="text-sm text-red-600">❌ {error}</p>}
      {!loading && !error && items.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No {tabValue} history available.
        </p>
      )}
      {!loading && items.length > 0 && (
        <>
          <ul className="space-y-3">
            {paginatedItems.map((item) => (
              <li
                key={item._id}
                onClick={() => onItemClick?.(item)}
                className={`border border-gray-300 dark:border-border rounded-md p-2 bg-gray-50 dark:bg-muted text-sm ${
                  onItemClick ? "cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800" : ""
                } transition`}
              >
                <div className="font-medium truncate">
                  {getItemText(item) || "No text"}
                </div>
                <div className="text-xs text-right text-muted-foreground mt-1">
                  {new Date(item.created_at).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
          <PaginationComponent
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={onPageChange}
          />
        </>
      )}
    </TabsContent>
  );
};

export default HistoryTabContent;