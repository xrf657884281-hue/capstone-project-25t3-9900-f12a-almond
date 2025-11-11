const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface DetectionRequest {
  text: string;
  use_improved_detection?: boolean;
}

export interface DetectionResponse {
  success: boolean;
  result: {
    final_prediction: string;
    fake_probability: number;
    confidence: number;
    explanation: any;
    detectgpt: any;
    wikipedia_verification: any;
    key_factors: string[];
    record_id?: string;
    _id?: string;
  };
  record_id?: string;
  _id?: string;
  timestamp: string;
}

export interface GenerationRequest {
  topic: string;
  model?: string;
  image_url_or_b64?: string;
}

export interface GenerationResponse {
  success: boolean;
  result: {
    generated_text?: string;
    article?: string;
    source_url?: string;
  };
  timestamp: string;
}

export interface VisionDescribeRequest {
  image_url_or_b64: string;
  detail_level?: "low" | "high" | "auto";
  output_mode?: "detailed" | "concise";
  max_chars?: number;
}

export interface VisionDescribeResponse {
  success: boolean;
  description?: string;
  error?: string;
}

export interface LoginResponse {
  success: boolean;
  username: string;
  email: string;
  access_token?: string;
  user_id?: string;
}

export interface RegisterResponse {
  success: boolean;
  user_id: string;
}

class ApiService {

  private async makeRequest<T>(
    endpoint: string,
    method: "GET" | "POST" = "GET",
    body?: any
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem("access_token");

    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options: RequestInit = {
      method,
      headers,
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      console.log(`🔹 API → ${method} ${url}`);
      const response = await fetch(url, options);
      console.log(`🔹 Status: ${response.status}`);

      const data = await response.json();

      if (!response.ok) {
        console.error(`❌ API Error (${response.status}):`, data);
        throw new Error(data.detail || `Request failed (${response.status})`);
      }

      return data;
    } catch (error) {
      console.error(`🚨 API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // ===== Detection =====
  async detectImproved(request: DetectionRequest): Promise<DetectionResponse> {
    return this.makeRequest<DetectionResponse>("/api/detect/improved", "POST", request);
  }

  async detectBaseline(text: string): Promise<DetectionResponse> {
    return this.makeRequest<DetectionResponse>("/api/detect/baseline", "POST", { text });
  }

  // ===== Generation =====
  async generateSingle(request: GenerationRequest): Promise<GenerationResponse> {
    return this.makeRequest<GenerationResponse>("/api/generate/single", "POST", request);
  }

  async generateMultiple(request: GenerationRequest): Promise<GenerationResponse> {
    return this.makeRequest<GenerationResponse>("/api/generate/multiple", "POST", request);
  }

  // ===== Vision Describe =====
  async visionDescribe(request: VisionDescribeRequest): Promise<VisionDescribeResponse> {
    return this.makeRequest<VisionDescribeResponse>("/api/vision/describe", "POST", request);
  }

  // ===== Detection History =====
  async getDetectionHistory(): Promise<any> {
    return this.makeRequest("/api/detection/history?page=1&page_size=9999", "GET");
  }

  // ===== Generation History =====
  async getGenerationHistory(): Promise<any> {
    return this.makeRequest("/api/generation/history?page=1&page_size=9999", "GET");
  }

  // ===== System Health =====
  async checkHealth(): Promise<{ status: string; services: any }> {
    return this.makeRequest<{ status: string; services: any }>("/health");
  }

  // ===== Auth =====
  async register(username: string, email: string, password: string): Promise<RegisterResponse> {
    return this.makeRequest("/api/auth/register", "POST", { username, email, password });
  }

  async login(usernameOrEmail: string, password: string): Promise<LoginResponse> {
    const data = await this.makeRequest<LoginResponse>("/api/auth/login", "POST", {
      username_or_email: usernameOrEmail,
      password,
    });

    if (data.success && data.access_token) {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          uid: data.user_id || `local-${Date.now()}`,
          displayName: data.username,
          email: data.email,
          provider: "local",
        })
      );
    }

    return data;
  }
}

export const apiService = new ApiService();
