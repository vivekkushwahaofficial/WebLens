export interface AnalyzeRequest {
  url: string;
}

export interface AnalyzeResponse {
  url: string;
  risk_score: number;
  verdict: string;
  confidence: number | null;
  reasons: string[];
}
