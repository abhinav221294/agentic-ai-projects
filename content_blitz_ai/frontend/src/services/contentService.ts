import api from "./api";

const API_URL = "http://127.0.0.1:8000";

export interface GenerateRequest {
  query: string;
  conversation_id: number;
}

export interface GenerateResponse {
  intent?: string;
  response?: string;
  workflow_step?: string;
  status?: string;
  active_agent?: string;
  confidence?: number;
  execution_time?: number;
  image_url?: string;
  trace?: unknown[];
}

export async function generateContent(
  request: GenerateRequest
): Promise<GenerateResponse> {
  const response = await api.post("/generate", request);
  return response.data;
}

export async function generateContentStream(
  request: GenerateRequest,
  onChunk: (chunk: string) => void
): Promise<void> {
  const token = localStorage.getItem("token");
  
  const response = await fetch(`${API_URL}/generate/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  });

const contentType = response.headers.get("content-type");

if (!response.ok) {
    if (contentType?.includes("application/json")) {
        const error = await response.json();
        throw new Error(error.detail ?? "Request failed");
    }

    throw new Error(`Streaming failed (${response.status})`);
}

if (contentType?.includes("application/json")) {
    const result = await response.json();

    if (result.intent === "image") {
        onChunk(
            `${result.response ?? ""}\n\n![Generated Image](${result.image_url})`
        );
    } else {
        onChunk(result.response ?? "");
    }

    return;
}


  if (!response.body) {
    throw new Error("ReadableStream not supported.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    const chunk = decoder.decode(value, {
      stream: true,
    });

    onChunk(chunk);
  }
}