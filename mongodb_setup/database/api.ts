const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
  };
  timestamp: string;
}

export interface GenerationRequest {
  topic: string;
  model?: string;
}

export interface GenerationResponse {
  success: boolean;
  result: {
    generated_text?: string;
    article?: string;
  };
  timestamp: string;
}

class ApiService {
  private async makeRequest<T>(
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    body?: any
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      console.log(`Making API request to: ${url}`);
      const response = await fetch(url, options);
      
      console.log(`Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP error response: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }
      
      const data = await response.json();
      console.log(`API response received for ${endpoint}:`, data);
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  async detectImproved(request: DetectionRequest): Promise<DetectionResponse> {
    return this.makeRequest<DetectionResponse>('/api/detect/improved', 'POST', request);
  }

  async detectBaseline(text: string): Promise<DetectionResponse> {
    return this.makeRequest<DetectionResponse>('/api/detect/baseline', 'POST', { text });
  }

  async generateSingle(request: GenerationRequest): Promise<GenerationResponse> {
    return this.makeRequest<GenerationResponse>('/api/generate/single', 'POST', request);
  }

  async generateMultiple(request: GenerationRequest): Promise<GenerationResponse> {
    return this.makeRequest<GenerationResponse>('/api/generate/multiple', 'POST', request);
  }

  async checkHealth(): Promise<{ status: string; services: any }> {
    return this.makeRequest<{ status: string; services: any }>('/health');
  }

  // ===== Auth =====
  async register(username: string, email: string, password: string): Promise<{ success: boolean; user_id: string }> {
    return this.makeRequest('/api/auth/register', 'POST', { username, email, password });
  }

  async login(usernameOrEmail: string, password: string): Promise<{ success: boolean; username: string; email: string }> {
    return this.makeRequest('/api/auth/login', 'POST', { username_or_email: usernameOrEmail, password });
  }
}

export const apiService = new ApiService();
