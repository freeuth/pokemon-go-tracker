'use client';

import { useState, useEffect } from 'react';
import { getPokemonDetail, PokemonDetail } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';

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

export default function PokemonDetailPage() {
  const params = useParams();
  const [pokemon, setPokemon] = useState<PokemonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPokemon();
  }, [params.id]);

  const loadPokemon = async () => {
    try {
      setLoading(true);
      const id = parseInt(params.id as string);
      const data = await getPokemonDetail(id);
      setPokemon(data);
      setError(null);
    } catch (err) {
      setError('포켓몬 정보를 불러오지 못했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-yellow-500"></div>
      </div>
    );
  }

  if (error || !pokemon) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-white">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error || '포켓몬을 찾을 수 없습니다.'}
          </div>
          <Link href="/pokedex" className="text-yellow-600 hover:underline mt-4 inline-block">
            ← 도감으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-yellow-50 to-white">
      <header className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <Link href="/pokedex" className="text-white hover:underline text-sm mb-2 inline-block">
            ← 도감으로 돌아가기
          </Link>
          <div className="flex items-center space-x-4">
            <div className="text-4xl">📖</div>
            <div>
              <h1 className="text-3xl font-bold">
                #{pokemon.pokedex_number.toString().padStart(3, '0')} {pokemon.name_ko}
              </h1>
              <p className="text-sm text-yellow-100">{pokemon.name_en}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
              <div className="relative aspect-square bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg mb-4">
                <img
                  src={pokemon.image_url}
                  alt={pokemon.name_ko}
                  className="w-full h-full object-contain p-8"
                />
              </div>
              <div className="flex gap-2 justify-center mb-4">
                {pokemon.types.map((type) => (
                  <span
                    key={type}
                    className={`px-4 py-2 rounded-full text-sm font-semibold text-white ${
                      TYPE_COLORS[type] || 'bg-gray-400'
                    }`}
                  >
                    {type}
                  </span>
                ))}
              </div>
              {(pokemon.can_dynamax || pokemon.can_gigantamax) && (
                <div className="flex gap-2 justify-center">
                  {pokemon.can_gigantamax && (
                    <div className="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-lg font-bold text-sm shadow-lg flex items-center gap-2">
                      <span className="text-2xl">⭐</span>
                      <div>
                        <div>거다이맥스 가능</div>
                        <div className="text-xs opacity-90">Gigantamax</div>
                      </div>
                    </div>
                  )}
                  {pokemon.can_dynamax && !pokemon.can_gigantamax && (
                    <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white px-4 py-2 rounded-lg font-bold text-sm shadow-lg flex items-center gap-2">
                      <span className="text-2xl">💫</span>
                      <div>
                        <div>다이맥스 가능</div>
                        <div className="text-xs opacity-90">Dynamax</div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">기본 스탯</h2>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-semibold text-red-500">공격력 (Attack)</span>
                    <span className="font-bold">{pokemon.base_attack}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{ width: `${(pokemon.base_attack / 350) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-semibold text-blue-500">방어력 (Defense)</span>
                    <span className="font-bold">{pokemon.base_defense}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(pokemon.base_defense / 350) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="font-semibold text-green-500">체력 (HP)</span>
                    <span className="font-bold">{pokemon.base_stamina}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(pokemon.base_stamina / 350) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">레이드 100% IV CP</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-gray-600 mb-1">레벨 20 (일반)</div>
                  <div className="text-3xl font-bold text-purple-600">
                    {pokemon.raid_perfect_cp.lv20_cp_100}
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <div className="text-sm text-gray-600 mb-1">레벨 25 (날씨부스트)</div>
                  <div className="text-3xl font-bold text-purple-600">
                    {pokemon.raid_perfect_cp.lv25_cp_100}
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">평타 기술</h2>
              <div className="space-y-2">
                {pokemon.moves_fast.map((move) => (
                  <div
                    key={move.move_id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-semibold">{move.name_ko}</div>
                      <div className="text-xs text-gray-500">{move.name_en}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm">
                        <span className="text-red-500 font-bold">{move.power || 0}</span> 위력
                      </span>
                      <span className="text-sm">
                        <span className="text-blue-500 font-bold">{move.energy || 0}</span> 에너지
                      </span>
                      {move.is_legacy && (
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                          레거시
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">차징 기술</h2>
              <div className="space-y-2">
                {pokemon.moves_charged.map((move) => (
                  <div
                    key={move.move_id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="font-semibold">{move.name_ko}</div>
                      <div className="text-xs text-gray-500">{move.name_en}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm">
                        <span className="text-red-500 font-bold">{move.power || 0}</span> 위력
                      </span>
                      <span className="text-sm">
                        <span className="text-blue-500 font-bold">{move.energy || 0}</span> 에너지
                      </span>
                      {move.is_legacy && (
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                          레거시
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {pokemon.raid_counters && pokemon.raid_counters.recommended_teams && pokemon.raid_counters.recommended_teams.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-800">레이드 카운터 추천</h2>
                <div className="space-y-4">
                  {pokemon.raid_counters.recommended_teams.map((team, idx) => (
                    <div key={idx} className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                      <h3 className="text-lg font-bold text-purple-800 mb-2">{team.name_ko}</h3>
                      {team.description_ko && (
                        <p className="text-sm text-gray-600 mb-3">{team.description_ko}</p>
                      )}
                      <div className="grid grid-cols-1 gap-2">
                        {team.members.map((member, memberIdx) => (
                          <div key={memberIdx} className="flex items-center justify-between p-2 bg-white rounded">
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-gray-800">{member.pokemon_name_ko}</span>
                              <span className="text-xs text-gray-500">({member.role_ko})</span>
                            </div>
                            <div className="text-xs text-gray-600">
                              {member.fast_move_id} / {member.charged_move_id}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
