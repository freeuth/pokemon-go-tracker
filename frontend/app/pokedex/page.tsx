'use client';

import { useState, useEffect } from 'react';
import { getPokemonList, Pokemon } from '@/lib/api';
import Link from 'next/link';

const TYPE_COLORS: { [key: string]: string } = {
  Normal: 'bg-gray-400',
  Fire: 'bg-red-500',
  Water: 'bg-blue-500',
  Electric: 'bg-yellow-400',
  Grass: 'bg-green-500',
  Ice: 'bg-cyan-400',
  Fighting: 'bg-red-700',
  Poison: 'bg-purple-500',
  Ground: 'bg-yellow-600',
  Flying: 'bg-indigo-400',
  Psychic: 'bg-pink-500',
  Bug: 'bg-lime-500',
  Rock: 'bg-yellow-700',
  Ghost: 'bg-purple-700',
  Dragon: 'bg-indigo-600',
  Dark: 'bg-gray-800',
  Steel: 'bg-gray-500',
  Fairy: 'bg-pink-400',
};

const REGIONS = [
  { id: 'all', name: '전체', name_en: 'All' },
  { id: 'kanto', name: '관동', name_en: 'Kanto' },
  { id: 'johto', name: '성도', name_en: 'Johto' },
  { id: 'hoenn', name: '호연', name_en: 'Hoenn' },
  { id: 'sinnoh', name: '신오', name_en: 'Sinnoh' },
  { id: 'unova', name: '하나', name_en: 'Unova' },
  { id: 'kalos', name: '칼로스', name_en: 'Kalos' },
  { id: 'alola', name: '알로라', name_en: 'Alola' },
  { id: 'galar', name: '가라르', name_en: 'Galar' },
];

export default function PokedexPage() {
  const [pokemon, setPokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPokemon();
  }, [selectedRegion]);

  const loadPokemon = async () => {
    try {
      setLoading(true);
      const region = selectedRegion === 'all' ? undefined : selectedRegion;
      const data = await getPokemonList(undefined, region);
      const sorted = data.sort((a, b) => a.pokedex_number - b.pokedex_number);
      setPokemon(sorted);
      setError(null);
    } catch (err) {
      setError('포켓몬 데이터를 불러오지 못했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadPokemon();
      return;
    }

    try {
      setLoading(true);
      const data = await getPokemonList(searchQuery);
      const sorted = data.sort((a, b) => a.pokedex_number - b.pokedex_number);
      setPokemon(sorted);
      setError(null);
    } catch (err) {
      setError('검색 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-white">
      <header className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-4 hover:opacity-80 transition">
              <div className="text-4xl">📖</div>
              <div>
                <h1 className="text-3xl font-bold">포켓몬 도감</h1>
                <p className="text-sm text-yellow-100">Pokemon GO Pokédex</p>
              </div>
            </Link>
            <nav className="flex space-x-2">
              <Link
                href="/"
                className="px-4 py-2 rounded-lg bg-white text-pokemon-red font-semibold hover:bg-red-50 transition"
              >
                이벤트 뉴스
              </Link>
              <Link
                href="/pokedex"
                className="px-4 py-2 rounded-lg bg-white bg-opacity-30 text-white font-semibold border-2 border-white transition"
              >
                포켓몬 도감
              </Link>
              <Link
                href="/analyzer"
                className="px-4 py-2 rounded-lg bg-pokemon-blue text-white font-semibold hover:bg-blue-700 transition"
              >
                IV 계산기
              </Link>
              <Link
                href="/videos"
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:from-purple-700 hover:to-pink-700 transition"
              >
                배틀 영상
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 max-w-2xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="포켓몬 이름 검색 (한글/영문)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 px-4 py-3 border-2 border-yellow-300 rounded-lg focus:outline-none focus:border-yellow-500"
            />
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-yellow-500 text-white font-semibold rounded-lg hover:bg-yellow-600 transition"
            >
              검색
            </button>
            <button
              onClick={() => {
                setSearchQuery('');
                loadPokemon();
              }}
              className="px-6 py-3 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition"
            >
              전체보기
            </button>
          </div>
        </div>

        <div className="mb-6 overflow-x-auto">
          <div className="flex gap-2 min-w-max justify-center pb-2">
            {REGIONS.map((region) => (
              <button
                key={region.id}
                onClick={() => setSelectedRegion(region.id)}
                className={`px-6 py-2 rounded-full font-semibold transition ${
                  selectedRegion === region.id
                    ? 'bg-yellow-500 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-yellow-100'
                }`}
              >
                {region.name}
                <span className="text-xs ml-1 opacity-70">({region.name_en})</span>
              </button>
            ))}
          </div>
        </div>

        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-yellow-500"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 max-w-2xl mx-auto">
            {error}
          </div>
        )}

        {!loading && pokemon.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl">포켓몬을 찾을 수 없습니다</p>
          </div>
        )}

        {!loading && pokemon.length > 0 && (
          <>
            <div className="text-center mb-4 text-gray-600">
              총 {pokemon.length}마리의 포켓몬
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {pokemon.map((poke) => (
                <Link
                  key={poke.id}
                  href={`/pokedex/${poke.pokedex_number}`}
                  className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group"
                >
                  <div className="relative aspect-square bg-gradient-to-br from-gray-50 to-gray-100">
                    <img
                      src={poke.image_url}
                      alt={poke.name_ko}
                      className="w-full h-full object-contain p-4 group-hover:scale-110 transition-transform duration-300"
                    />
                    <div className="absolute top-2 right-2 bg-white/90 px-2 py-1 rounded-full text-xs font-bold text-gray-600">
                      #{poke.pokedex_number.toString().padStart(3, '0')}
                    </div>
                    {poke.can_gigantamax && (
                      <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-bold shadow-lg">
                        G-Max
                      </div>
                    )}
                    {poke.can_dynamax && !poke.can_gigantamax && (
                      <div className="absolute top-2 left-2 bg-purple-500 text-white px-2 py-1 rounded-full text-xs font-bold shadow-lg">
                        D-Max
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="text-lg font-bold text-gray-800 mb-1">{poke.name_ko}</h3>
                    <p className="text-xs text-gray-500 mb-2">{poke.name_en}</p>
                    <div className="flex gap-1 flex-wrap">
                      {poke.types.map((type) => (
                        <span
                          key={type}
                          className={`px-2 py-1 rounded-full text-xs font-semibold text-white ${
                            TYPE_COLORS[type] || 'bg-gray-400'
                          }`}
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
