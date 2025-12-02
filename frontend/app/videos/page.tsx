'use client';

import { useState, useEffect } from 'react';
import { getVideos, YouTubeVideo } from '@/lib/api';
import VideoCard from '@/components/VideoCard';
import Link from 'next/link';

// 추천 채널은 동적으로 로드됨 (실제 수집된 채널 기반)

export default function VideosPage() {
  const [videos, setVideos] = useState<YouTubeVideo[]>([]);
  const [filteredVideos, setFilteredVideos] = useState<YouTubeVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');
  const [featuredChannels, setFeaturedChannels] = useState<Array<{ name: string; count: number }>>([]);

  useEffect(() => {
    loadVideos();
  }, []);

  useEffect(() => {
    filterAndSortVideos();
  }, [videos, selectedChannel, sortOrder]);

  const loadVideos = async () => {
    try {
      setLoading(true);
      const data = await getVideos(0, 100);
      setVideos(data);

      // 채널별 영상 수 계산 (영상 개수 순으로 정렬)
      const channelCounts = data.reduce((acc: Record<string, number>, video) => {
        acc[video.channel_name] = (acc[video.channel_name] || 0) + 1;
        return acc;
      }, {});

      const channels = Object.entries(channelCounts)
        .map(([name, count]) => ({ name, count: count as number }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8); // 상위 8개 채널만

      setFeaturedChannels(channels);
      setError(null);
    } catch (err) {
      setError('Failed to load videos. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortVideos = () => {
    let result = [...videos];

    // 채널 필터링
    if (selectedChannel) {
      result = result.filter(video => video.channel_name === selectedChannel);
    }

    // 날짜순 정렬
    result.sort((a, b) => {
      const dateA = a.published_at ? new Date(a.published_at).getTime() : 0;
      const dateB = b.published_at ? new Date(b.published_at).getTime() : 0;
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });

    setFilteredVideos(result);
  };

  const handleChannelClick = (channelName: string) => {
    if (selectedChannel === channelName) {
      setSelectedChannel(null); // 이미 선택된 채널을 다시 클릭하면 필터 해제
    } else {
      setSelectedChannel(channelName);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-purple-50 to-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">🎬</div>
              <div>
                <h1 className="text-3xl font-bold">배틀 영상</h1>
                <p className="text-sm text-purple-100">유명 포켓몬고 배틀 유튜버 영상</p>
              </div>
            </div>
            <nav className="flex space-x-4">
              <Link
                href="/"
                className="px-4 py-2 rounded-lg bg-pokemon-red text-white font-semibold hover:bg-red-700 transition"
              >
                이벤트 뉴스
              </Link>
              <Link
                href="/analyzer"
                className="px-4 py-2 rounded-lg bg-pokemon-blue text-white font-semibold hover:bg-blue-700 transition"
              >
                IV 계산기
              </Link>
              <Link
                href="/videos"
                className="px-4 py-2 rounded-lg bg-white text-purple-600 font-semibold hover:bg-purple-50 transition"
              >
                배틀 영상
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            최신 포켓몬고 배틀 영상
          </h2>
          <p className="text-gray-600">
            대회 수상 경험이 있는 유명 포켓몬고 배틀 유튜버들의 최신 영상을 확인하세요
          </p>
        </div>

        {/* Featured Channels */}
        {featuredChannels.length > 0 && (
          <div className="mb-8 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-800 flex items-center">
                <span className="text-2xl mr-2">🏆</span>
                추천 채널 ({featuredChannels.length})
                {selectedChannel && (
                  <span className="ml-3 text-sm text-purple-600 font-normal">
                    (필터링: {selectedChannel})
                  </span>
                )}
              </h3>
              {selectedChannel && (
                <button
                  onClick={() => setSelectedChannel(null)}
                  className="text-sm px-3 py-1 bg-white rounded-lg hover:bg-gray-100 transition"
                >
                  필터 해제
                </button>
              )}
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {featuredChannels.map((channel) => (
                <button
                  key={channel.name}
                  onClick={() => handleChannelClick(channel.name)}
                  className={`rounded-lg p-3 text-center transition-all transform hover:scale-105 ${
                    selectedChannel === channel.name
                      ? 'bg-purple-600 text-white shadow-lg'
                      : 'bg-white text-gray-800 hover:bg-purple-50'
                  }`}
                >
                  <div className="font-semibold text-sm">{channel.name}</div>
                  <div className={`text-xs ${selectedChannel === channel.name ? 'text-purple-100' : 'text-gray-600'}`}>
                    {channel.count}개 영상
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Sort Controls */}
        <div className="mb-6 flex items-center justify-between">
          <div className="text-gray-700">
            <span className="font-semibold">{filteredVideos.length}</span>개의 영상
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">정렬:</span>
            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'newest' | 'oldest')}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
            >
              <option value="newest">최신순</option>
              <option value="oldest">오래된순</option>
            </select>
          </div>
        </div>

        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-600"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!loading && !error && filteredVideos.length === 0 && videos.length > 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl">선택한 채널의 영상이 없습니다</p>
            <p className="text-sm mt-2">다른 채널을 선택하거나 필터를 해제해보세요</p>
          </div>
        )}

        {!loading && !error && videos.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-6xl mb-4">📹</div>
            <p className="text-xl">영상을 찾을 수 없습니다</p>
            <p className="text-sm mt-2">나중에 다시 확인해주세요</p>
          </div>
        )}

        {!loading && filteredVideos.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVideos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-16 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">Pokemon GO Tracker - Unofficial fan-made tool</p>
          <p className="text-xs text-gray-400 mt-2">
            Not affiliated with Niantic or The Pokemon Company
          </p>
        </div>
      </footer>
    </div>
  );
}
