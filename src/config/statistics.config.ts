// Statistics configuration
export const ITEMS_PER_PAGE = 5;

// Detection filter options
export const DETECTION_FILTERS = [
  { key: "Real", label: "Real", color: "green" as const },
  { key: "Fake", label: "Fake", color: "red" as const },
  { key: "Misleading", label: "Misleading", color: "yellow" as const },
] as const;

// Generation style filters
export const STYLE_FILTERS = [
  { key: "Fun", label: "Fun", color: "blue" as const },
  { key: "Formal", label: "Formal", color: "red" as const },
  { key: "Sensational", label: "Sensational", color: "yellow" as const },
  { key: "Normal", label: "Normal", color: "purple" as const },
] as const;

// Generation domain filters
export const DOMAIN_FILTERS = [
  { key: "Technology", label: "Technology", color: "green" as const },
  { key: "Politics", label: "Politics", color: "amber" as const },
  { key: "Business", label: "Business", color: "red" as const },
  { key: "Sports", label: "Sports", color: "purple" as const },
  { key: "Health", label: "Health", color: "yellow" as const },
  { key: "Environment", label: "Environment", color: "pink" as const },
  { key: "Science", label: "Science", color: "blue" as const },
  { key: "Crime", label: "Crime", color: "indigo" as const },
  { key: "Entertainment", label: "Entertainment", color: "cyan" as const },
  { key: "General", label: "General", color: "gray" as const },
] as const;

// Tab configuration
export const STAT_TABS = [
  { value: "overall", label: "Overall" },
  { value: "detection", label: "Detection" },
  { value: "generation", label: "Generation" },
] as const;

// Variant configuration
export const GENERATION_VARIANTS = [
  { value: "style" as const, label: "By Style" },
  { value: "domain" as const, label: "By Topic" },
] as const;