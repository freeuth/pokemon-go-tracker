'use client';

import { useState, useEffect } from 'react';
import { getEvents, Event } from '@/lib/api';
import EventCard from '@/components/EventCard';
import EmailSubscription from '@/components/EmailSubscription';
import Link from 'next/link';

export default function Home() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const data = await getEvents();
      setEvents(data);
      setError(null);
    } catch (err) {
      setError('Failed to load events. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-pokemon-red text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">🎮</div>
              <div>
                <h1 className="text-3xl font-bold">Pokemon GO Tracker</h1>
                <p className="text-sm text-red-100">포켓몬고 이벤트 & 배틀 영상</p>
              </div>
            </div>
            <nav className="flex space-x-2">
              <Link
                href="/"
                className="px-4 py-2 rounded-lg bg-white text-pokemon-red font-semibold hover:bg-red-50 transition"
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
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:from-purple-700 hover:to-pink-700 transition"
              >
                배틀 영상
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Email Subscription */}
        <div className="mb-12">
          <EmailSubscription />
        </div>

        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">최신 포켓몬고 이벤트</h2>
          <p className="text-gray-600">
            커뮤니티 데이, 레이드 아워, 특별 이벤트 정보를 확인하세요
          </p>
        </div>

        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-pokemon-red"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-xl">이벤트를 찾을 수 없습니다</p>
            <p className="text-sm mt-2">나중에 다시 확인해주세요</p>
          </div>
        )}

        {!loading && events.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-16 py-8">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            Pokemon GO Tracker - Unofficial fan-made tool
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Not affiliated with Niantic or The Pokemon Company
          </p>
        </div>
      </footer>
    </div>
  );
}
