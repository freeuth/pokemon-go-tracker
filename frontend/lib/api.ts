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

// Pokédex API
export interface Pokemon {
  id: number;
  pokedex_number: number;
  name_en: string;
  name_ko: string;
  types: string[];
  image_url: string;
  can_dynamax?: boolean;
  can_gigantamax?: boolean;
}

export interface Move {
  move_id: string;
  name_en: string;
  name_ko: string;
  type: string;
  power: number | null;
  energy: number | null;
  move_type: string;
  is_legacy: boolean;
}

export interface PokemonDetail extends Pokemon {
  base_attack: number;
  base_defense: number;
  base_stamina: number;
  sprite_url: string | null;
  can_dynamax?: boolean;
  can_gigantamax?: boolean;
  evolutions: any[] | null;
  moves_fast: Move[];
  moves_charged: Move[];
  raid_perfect_cp: {
    lv20_cp_100: number;
    lv25_cp_100: number;
  };
  current_season: {
    season_id: string;
    season_name_ko: string;
    raid_tier: string;
    raid_attack_tier: string | null;
    gbl_great_tier: string;
    gbl_ultra_tier: string;
    gbl_master_tier: string;
    raid_role_ko: string | null;
  } | null;
  raid_counters: {
    boss_pokemon_id: number;
    season_id: string;
    recommended_teams: Array<{
      name_ko: string;
      description_ko: string;
      members: Array<{
        pokemon_id: number;
        pokemon_name_ko: string;
        fast_move_id: string;
        charged_move_id: string;
        role_ko: string;
      }>;
    }>;
  } | null;
}

export interface PvPPartyRanking {
  rank: number;
  team: {
    pokemon_id: number;
    pokemon_name_ko: string;
    pokemon_name_en: string;
    pokemon_image_url: string;
    fast_move_id: string;
    fast_move_name_ko: string;
    charged_move_id: string;
    charged_move_name_ko: string;
  }[];
  estimated_rating: number;
  notes_ko: string;
}

export const getPokemonList = async (search?: string, region?: string): Promise<Pokemon[]> => {
  let url = '/api/pokedex';
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (region) params.append('region', region);
  if (params.toString()) url += `?${params.toString()}`;

  const response = await api.get(url);
  return response.data;
};

export const getPokemonDetail = async (id: number): Promise<PokemonDetail> => {
  const response = await api.get(`/api/pokedex/${id}`);
  return response.data;
};

export const getRaidCounters = async (bossId: number) => {
  const response = await api.get(`/api/raids/${bossId}/counters`);
  return response.data;
};

export const getTopAttackers = async (type?: string) => {
  const url = type ? `/api/raids/top-attackers?type=${type}` : '/api/raids/top-attackers';
  const response = await api.get(url);
  return response.data;
};

export const getPvPPartyRankings = async (league: string = 'Great', limit: number = 20) => {
  const response = await api.get(`/api/pvp/party-rankings?league=${league}&limit=${limit}`);
  return response.data;
};

export default api;
