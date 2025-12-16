import { PokemonAnalysis } from '@/lib/api';
import Link from 'next/link';

interface AnalysisResultProps {
  analysis: PokemonAnalysis;
}

export default function AnalysisResult({ analysis }: AnalysisResultProps) {
  const getRatingColor = (rating: string | null) => {
    if (!rating) return 'bg-gray-500';
    if (rating.startsWith('A')) return 'bg-green-500';
    if (rating.startsWith('B')) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  // 리그별 CP 계산 (간단한 예시 - 실제로는 백엔드에서 계산하는 것이 좋습니다)
  const calculateLeagueCP = (league: string) => {
    if (!analysis.cp) return 0;
    // 실제로는 각 리그의 CP 제한에 맞춰 계산해야 합니다
    // 여기서는 예시로 간단한 계산을 보여줍니다
    switch(league) {
      case 'great': return Math.min(1500, analysis.cp);
      case 'ultra': return Math.min(2500, analysis.cp);
      case 'master': return analysis.cp;
      default: return analysis.cp;
    }
  };

  // IV 퍼센트에 따른 리그 적합도 계산
  const getLeagueRank = (ivPercent: number | null) => {
    if (!ivPercent) return 'N/A';
    if (ivPercent >= 95) return 'S등급 (상위 5%)';
    if (ivPercent >= 90) return 'A등급 (상위 10%)';
    if (ivPercent >= 80) return 'B등급 (상위 20%)';
    if (ivPercent >= 70) return 'C등급 (상위 30%)';
    return 'D등급 (하위 30%)';
  };

  return (
    <div className="bg-white rounded-lg shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-pokemon-red to-red-600 text-white p-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-3xl font-bold">{analysis.pokemon_name || 'Unknown Pokemon'}</h2>
          {analysis.pokemon_name && (
            <Link
              href={`/pokedex?search=${encodeURIComponent(analysis.pokemon_name)}`}
              className="bg-white text-pokemon-red px-4 py-2 rounded-lg font-bold hover:bg-gray-100 transition flex items-center gap-2"
            >
              <span>📖</span>
              도감 보기
            </Link>
          )}
        </div>
        <div className="flex items-center space-x-4">
          <div className="bg-white text-pokemon-red px-4 py-2 rounded-lg font-bold">
            CP {analysis.cp || 'N/A'}
          </div>
          <div className="bg-white text-pokemon-red px-4 py-2 rounded-lg font-bold">
            HP {analysis.hp || 'N/A'}
          </div>
          {analysis.level && (
            <div className="bg-white text-pokemon-red px-4 py-2 rounded-lg font-bold">
              Level {analysis.level}
            </div>
          )}
        </div>
      </div>

      {/* IV Stats */}
      <div className="p-6">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xl font-bold text-gray-800">개체값 비율</h3>
            <span className="text-3xl font-bold text-pokemon-blue">
              {analysis.iv_percentage?.toFixed(1)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-pokemon-blue h-3 rounded-full transition-all"
              style={{ width: `${analysis.iv_percentage || 0}%` }}
            ></div>
          </div>
        </div>

        {/* Individual IVs */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-600 mb-1">공격</div>
            <div className="text-2xl font-bold text-red-600">{analysis.attack_iv || 0}</div>
            <div className="text-xs text-gray-500">/ 15</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-600 mb-1">방어</div>
            <div className="text-2xl font-bold text-blue-600">{analysis.defense_iv || 0}</div>
            <div className="text-xs text-gray-500">/ 15</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-sm text-gray-600 mb-1">체력</div>
            <div className="text-2xl font-bold text-green-600">{analysis.stamina_iv || 0}</div>
            <div className="text-xs text-gray-500">/ 15</div>
          </div>
        </div>

        {/* League Performance */}
        <div className="mb-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <span className="text-2xl mr-2">⚔️</span>
            리그별 개체 적합도
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Great League */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-semibold text-green-800">Great League</div>
                <div className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">CP 1500</div>
              </div>
              <div className="text-2xl font-bold text-green-700 mb-1">
                {getLeagueRank(analysis.iv_percentage)}
              </div>
              <div className="text-sm text-green-600">
                예상 CP: {calculateLeagueCP('great')}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                {analysis.iv_percentage && analysis.iv_percentage >= 90
                  ? '✅ 매우 우수한 개체입니다'
                  : '⚠️ 더 좋은 개체를 찾아보세요'}
              </div>
            </div>

            {/* Ultra League */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-300 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-semibold text-blue-800">Ultra League</div>
                <div className="text-xs bg-blue-200 text-blue-800 px-2 py-1 rounded">CP 2500</div>
              </div>
              <div className="text-2xl font-bold text-blue-700 mb-1">
                {getLeagueRank(analysis.iv_percentage)}
              </div>
              <div className="text-sm text-blue-600">
                예상 CP: {calculateLeagueCP('ultra')}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                {analysis.iv_percentage && analysis.iv_percentage >= 90
                  ? '✅ 매우 우수한 개체입니다'
                  : '⚠️ 더 좋은 개체를 찾아보세요'}
              </div>
            </div>

            {/* Master League */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-300 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-semibold text-purple-800">Master League</div>
                <div className="text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded">무제한</div>
              </div>
              <div className="text-2xl font-bold text-purple-700 mb-1">
                {getLeagueRank(analysis.iv_percentage)}
              </div>
              <div className="text-sm text-purple-600">
                현재 CP: {analysis.cp || 'N/A'}
              </div>
              <div className="mt-2 text-xs text-gray-600">
                {analysis.iv_percentage && analysis.iv_percentage >= 95
                  ? '✅ 최고 개체입니다!'
                  : analysis.iv_percentage && analysis.iv_percentage >= 90
                  ? '✅ 우수한 개체입니다'
                  : '⚠️ 마스터리그용으로는 부족합니다'}
              </div>
            </div>
          </div>
        </div>

        {/* Ratings */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="border-2 border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-2">배틀 등급 (PvP)</div>
            <div className="flex items-center">
              <span
                className={`${getRatingColor(
                  analysis.battle_rating
                )} text-white px-4 py-2 rounded-lg font-bold text-xl`}
              >
                {analysis.battle_rating || 'N/A'}
              </span>
            </div>
          </div>
          <div className="border-2 border-gray-200 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-2">레이드 등급</div>
            <div className="flex items-center">
              <span
                className={`${getRatingColor(
                  analysis.raid_rating
                )} text-white px-4 py-2 rounded-lg font-bold text-xl`}
              >
                {analysis.raid_rating || 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {analysis.recommendations && (
          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-6">
            <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <span className="text-2xl mr-2">💡</span>
              추천 사항
            </h4>

            {analysis.recommendations.should_power_up && (
              <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg mb-4 font-semibold">
                ✅ 강화 추천!
              </div>
            )}

            {analysis.recommendations.best_use_case && (
              <div className="mb-4">
                <strong className="text-gray-700">최적 용도:</strong>
                <p className="text-gray-600 mt-1">{analysis.recommendations.best_use_case}</p>
              </div>
            )}

            {analysis.recommendations.move_recommendations &&
              analysis.recommendations.move_recommendations.length > 0 && (
                <div className="mb-4">
                  <strong className="text-gray-700">추천 기술:</strong>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    {analysis.recommendations.move_recommendations.map((move, index) => (
                      <li key={index} className="text-gray-600 text-sm">
                        {move}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {analysis.recommendations.notes && analysis.recommendations.notes.length > 0 && (
              <div>
                <strong className="text-gray-700">참고사항:</strong>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  {analysis.recommendations.notes.map((note, index) => (
                    <li key={index} className="text-gray-600 text-sm">
                      {note}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
