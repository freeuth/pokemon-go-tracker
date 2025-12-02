import { YouTubeVideo } from '@/lib/api';
import { format } from 'date-fns';
import { useEffect } from 'react';

interface VideoCardProps {
  video: YouTubeVideo;
}

export default function VideoCard({ video }: VideoCardProps) {
  const publishedDate = video.published_at
    ? format(new Date(video.published_at), 'MMM dd, yyyy')
    : 'Date unknown';

  const formatViewCount = (count: number | null) => {
    if (!count) return '0 views';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M views`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K views`;
    return `${count} views`;
  };

  // URL 일관성 검증 (개발자용)
  useEffect(() => {
    if (!video.video_url) {
      console.warn('⚠️ URL 누락:', video.title, '- video_url이 없습니다');
      return;
    }

    // YouTube video_id 추출
    const videoIdMatch = video.video_url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)/);
    if (!videoIdMatch) {
      console.warn('⚠️ 유효하지 않은 YouTube URL:', video.title, video.video_url);
      return;
    }

    const videoId = videoIdMatch[1];
    const expectedThumbnail = `https://i.ytimg.com/vi/${videoId}/maxresdefault.jpg`;

    // thumbnail_url과 video_url의 video_id가 일치하는지 확인
    if (video.thumbnail_url && !video.thumbnail_url.includes(videoId)) {
      console.warn(
        '⚠️ URL 불일치 감지:',
        `\n  제목: ${video.title}`,
        `\n  video_url: ${video.video_url}`,
        `\n  video_id: ${videoId}`,
        `\n  thumbnail_url: ${video.thumbnail_url}`,
        `\n  예상 thumbnail: ${expectedThumbnail}`,
        '\n  → thumbnail_url과 video_url이 다른 영상을 가리키고 있습니다!'
      );
    }

    // EXAMPLE_VIDEO_ID 등 placeholder 감지
    if (videoId.includes('EXAMPLE') || videoId.includes('PLACEHOLDER')) {
      console.warn(
        '⚠️ 더미 데이터 감지:',
        `\n  제목: ${video.title}`,
        `\n  video_id: ${videoId}`,
        '\n  → 실제 YouTube 영상 ID로 교체가 필요합니다!'
      );
    }
  }, [video]);

  return (
    <a
      href={video.video_url || '#'}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white rounded-lg shadow-md hover:shadow-xl transition-all overflow-hidden group"
    >
      {/* Thumbnail */}
      <div className="relative h-48 bg-gray-900 overflow-hidden">
        {video.thumbnail_url ? (
          <img
            src={video.thumbnail_url}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.currentTarget.src = 'https://via.placeholder.com/480x360?text=YouTube';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-red-500 to-red-700">
            <div className="text-white text-6xl">▶</div>
          </div>
        )}

        {/* Play overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all">
          <div className="bg-red-600 rounded-full p-4 opacity-0 group-hover:opacity-100 transition-opacity transform scale-75 group-hover:scale-100">
            <svg
              className="w-8 h-8 text-white"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="text-base font-semibold text-gray-800 mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors">
          {video.title}
        </h3>

        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span className="font-medium text-purple-600">{video.channel_name}</span>
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{formatViewCount(video.view_count)}</span>
          <span>{publishedDate}</span>
        </div>

        {video.description && (
          <p className="mt-2 text-xs text-gray-600 line-clamp-2">
            {video.description}
          </p>
        )}
      </div>
    </a>
  );
}
