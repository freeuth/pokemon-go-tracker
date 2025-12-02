import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Event {
  id: number;
  title: string;
  url: string;
  summary: string | null;
  published_date: string | null;
  image_url: string | null;
  category: string | null;
  created_at: string;
}

export interface PokemonAnalysis {
  id: number;
  pokemon_name: string | null;
  cp: number | null;
  hp: number | null;
  level: number | null;
  iv_percentage: number | null;
  attack_iv: number | null;
  defense_iv: number | null;
  stamina_iv: number | null;
  battle_rating: string | null;
  raid_rating: string | null;
  recommendations: {
    should_power_up: boolean;
    best_use_case: string;
    move_recommendations: string[];
    notes: string[];
  } | null;
  analyzed_at: string;
}

// Event API calls
export const getEvents = async (skip = 0, limit = 20): Promise<Event[]> => {
  const response = await api.get(`/api/events?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getEvent = async (id: number): Promise<Event> => {
  const response = await api.get(`/api/events/${id}`);
  return response.data;
};

export const triggerCrawl = async () => {
  const response = await api.post('/api/events/crawl');
  return response.data;
};

// Analysis API calls
export const uploadScreenshot = async (file: File): Promise<PokemonAnalysis> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/analysis/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysisHistory = async (skip = 0, limit = 20): Promise<PokemonAnalysis[]> => {
  const response = await api.get(`/api/analysis/history?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const getAnalysis = async (id: number): Promise<PokemonAnalysis> => {
  const response = await api.get(`/api/analysis/${id}`);
  return response.data;
};

// YouTube Video API
export interface YouTubeVideo {
  id: number;
  video_id: string;
  title: string;
  channel_name: string;
  thumbnail_url: string | null;
  description: string | null;
  published_at: string | null;
  video_url: string | null;
  view_count: number | null;
}

export const getVideos = async (skip = 0, limit = 20): Promise<YouTubeVideo[]> => {
  const response = await api.get(`/api/videos?skip=${skip}&limit=${limit}`);
  return response.data;
};

export const refreshVideos = async () => {
  const response = await api.post('/api/videos/refresh');
  return response.data;
};

// Email Subscription API
export interface Subscription {
  id: number;
  email: string;
  is_active: boolean;
}

export const createSubscription = async (email: string): Promise<Subscription> => {
  const response = await api.post('/api/subscriptions/', { email });
  return response.data;
};

export const getSubscription = async (email: string): Promise<Subscription> => {
  const response = await api.get(`/api/subscriptions/${email}`);
  return response.data;
};

export const updateSubscription = async (
  email: string,
  newEmail: string,
  isActive: boolean
): Promise<Subscription> => {
  const response = await api.put(`/api/subscriptions/${email}`, {
    email: newEmail,
    is_active: isActive,
  });
  return response.data;
};

export const deleteSubscription = async (email: string) => {
  const response = await api.delete(`/api/subscriptions/${email}`);
  return response.data;
};

export default api;
