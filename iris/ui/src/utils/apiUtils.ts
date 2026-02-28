import axios from 'axios';

/**
 * Helper function for GET requests that return lists
 */
export async function listRequest<T>(
  url: string,
  params?: Record<string, any>
): Promise<T> {
  const response = await axios.get<T>(url, { params });
  return response.data;
}

/**
 * Helper function for mutation requests (POST, PUT, DELETE, PATCH)
 */
export async function mutateRequest<TRequest, TResponse>(
  url: string,
  method: 'POST' | 'PUT' | 'DELETE' | 'PATCH',
  data?: TRequest
): Promise<TResponse> {
  const response = await axios.request<TResponse>({
    url,
    method,
    data,
  });
  return response.data;
}
