// User types
export type StoredUser = {
  uid?: string;
  displayName?: string | null;
  email?: string | null;
  photoURL?: string | null;
  provider?: string | null;
};

export type UserFormData = {
  username: string;
  email: string;
  photoURL: string | null;
};

// Record types
export type DetectionRecord = {
  _id: string;
  type: string;
  text?: string;
  result?: any;
  created_at: string;
};

export type GenerationRecord = {
  _id: string;
  type: string;
  prompt?: string;
  generated_text?: string;
  created_at: string;
  params?: {
    style?: string;
    domain?: string;
  };
};

// Statistics types
export type DetectionStats = {
  real: number;
  fake: number;
  misleading: number;
};

export type GenerationStats = {
  byStyle: Record<string, number>;
  byDomain: Record<string, number>;
};

export type OverallStats = {
  real: number;
  fake: number;
  misleading: number;
  totalDetections: number;
  totalGenerations: number;
};