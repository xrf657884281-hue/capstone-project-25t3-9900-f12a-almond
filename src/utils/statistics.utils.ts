import type { GenerationRecord } from "@/types/profile.types";

/**
 * Extract style from generation record
 */
export const getStyleFromRecord = (record: GenerationRecord): string => {
  if (record.params?.style) {
    return record.params.style.charAt(0).toUpperCase() + record.params.style.slice(1);
  }
  return record.type || "Unknown";
};

/**
 * Extract domain from generation record
 */
export const getDomainFromRecord = (record: GenerationRecord): string => {
  if (record.params?.domain) {
    return record.params.domain.charAt(0).toUpperCase() + record.params.domain.slice(1);
  }
  return "General";
};

/**
 * Get text preview from record
 */
export const getRecordPreview = (
  text: string | undefined,
  maxLength: number = 100
): string => {
  if (!text) return "No text";
  return text.slice(0, maxLength);
};

/**
 * Calculate total pages for pagination
 */
export const calculateTotalPages = (totalItems: number, itemsPerPage: number): number => {
  return Math.ceil(totalItems / itemsPerPage);
};