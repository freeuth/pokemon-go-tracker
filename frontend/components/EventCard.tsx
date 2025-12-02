import { Event } from '@/lib/api';
import { format } from 'date-fns';

interface EventCardProps {
  event: Event;
}

export default function EventCard({ event }: EventCardProps) {
  const publishedDate = event.published_date
    ? format(new Date(event.published_date), 'MMM dd, yyyy')
    : 'Date unknown';

  // 기본 플레이스홀더 이미지 URL
  const placeholderImage = 'https://lh3.googleusercontent.com/c8_zDZVu8lEKu3xL6P-rRCMaABf0FJgk6qJK5QqLjLbBwR0PcbO_RBH1YQqR6IFVwQWk=w400-h200';

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow overflow-hidden">
      {/* 썸네일 이미지 - 항상 표시 */}
      <div className="h-48 bg-gradient-to-br from-red-500 to-red-700 overflow-hidden relative">
        <img
          src={event.image_url || placeholderImage}
          alt={event.title}
          className="w-full h-full object-cover"
          onError={(e) => {
            // 이미지 로드 실패 시 기본 포켓몬GO 배경색 유지 및 로고 표시
            e.currentTarget.style.display = 'none';
            const parent = e.currentTarget.parentElement;
            if (parent) {
              parent.innerHTML = `
                <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-red-500 to-red-700">
                  <div class="text-center text-white">
                    <div class="text-6xl mb-2">🎮</div>
                    <p class="text-sm font-semibold opacity-90">Pokemon GO</p>
                  </div>
                </div>
              `;
            }
          }}
        />
      </div>

      <div className="p-6">
        {event.category && (
          <span className="inline-block bg-pokemon-red text-white text-xs px-3 py-1 rounded-full mb-3">
            {event.category}
          </span>
        )}

        <h3 className="text-xl font-bold text-gray-800 mb-2 line-clamp-2">
          {event.title}
        </h3>

        {event.summary && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">
            {event.summary}
          </p>
        )}

        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">{publishedDate}</span>
          <a
            href={event.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-pokemon-blue hover:text-blue-700 font-semibold text-sm flex items-center transition-colors"
          >
            자세히 보기
            <svg
              className="w-4 h-4 ml-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
