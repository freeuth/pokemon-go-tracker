'use client';

import { useState } from 'react';
import { uploadScreenshot, PokemonAnalysis } from '@/lib/api';
import { useDropzone } from 'react-dropzone';
import Link from 'next/link';
import AnalysisResult from '@/components/AnalysisResult';

export default function Analyzer() {
  const [analysis, setAnalysis] = useState<PokemonAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await uploadScreenshot(file);
      setAnalysis(result);
    } catch (err) {
      setError('Failed to analyze screenshot. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
    },
    maxFiles: 1,
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-pokemon-blue text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">🔍</div>
              <div>
                <h1 className="text-3xl font-bold">IV Analyzer</h1>
                <p className="text-sm text-blue-100">Analyze your Pokemon screenshots</p>
              </div>
            </div>
            <nav className="flex space-x-2">
              <Link
                href="/"
                className="px-4 py-2 rounded-lg bg-pokemon-red text-white font-semibold hover:bg-red-700 transition"
              >
                이벤트 뉴스
              </Link>
              <Link
                href="/pokedex"
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-yellow-400 to-yellow-600 text-white font-semibold hover:from-yellow-500 hover:to-yellow-700 transition"
              >
                포켓몬 도감
              </Link>
              <Link
                href="/analyzer"
                className="px-4 py-2 rounded-lg bg-white text-pokemon-blue font-semibold hover:bg-blue-50 transition"
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
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">포켓몬 스크린샷 업로드</h2>
          <p className="text-gray-600">
            포켓몬 정보 화면 스크린샷을 업로드하여 개체값을 분석하세요
          </p>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-4 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-pokemon-blue bg-blue-50'
              : 'border-gray-300 hover:border-pokemon-blue hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-6xl mb-4">📸</div>
          {isDragActive ? (
            <p className="text-xl text-pokemon-blue font-semibold">스크린샷을 여기에 놓으세요</p>
          ) : (
            <div>
              <p className="text-xl text-gray-700 mb-2">
                포켓몬 스크린샷을 드래그하여 놓으세요
              </p>
              <p className="text-sm text-gray-500">또는 클릭하여 파일을 선택하세요</p>
              <p className="text-xs text-gray-400 mt-4">
                지원 형식: PNG, JPG, JPEG, WEBP (최대 10MB)
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {loading && (
          <div className="mt-8 flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-pokemon-blue mb-4"></div>
            <p className="text-gray-600">포켓몬 분석 중...</p>
          </div>
        )}

        {analysis && !loading && (
          <div className="mt-8">
            <AnalysisResult analysis={analysis} />
          </div>
        )}

        {/* Instructions */}
        <div className="mt-12 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center">
            <span className="text-2xl mr-2">💡</span>
            사용 방법
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>포켓몬 GO를 열고 포켓몬 컬렉션으로 이동하세요</li>
            <li>포켓몬을 선택하고 정보 화면의 스크린샷을 촬영하세요</li>
            <li>스크린샷을 여기에 업로드하세요</li>
            <li>즉시 개체값 분석 결과와 추천 사항을 확인하세요</li>
          </ol>
          <p className="text-sm text-gray-600 mt-4">
            참고: 이 도구는 OCR을 사용하여 스크린샷을 읽습니다. 이미지가 선명하고
            포켓몬의 CP, HP, 이름이 잘 보이는지 확인하세요.
          </p>
        </div>
      </main>
    </div>
  );
}
