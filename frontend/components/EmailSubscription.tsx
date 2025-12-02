'use client';

import { useState } from 'react';
import { createSubscription, updateSubscription } from '@/lib/api';

export default function EmailSubscription() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
    null
  );
  const [isEditing, setIsEditing] = useState(false);
  const [currentEmail, setCurrentEmail] = useState('');

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setMessage({ type: 'error', text: '유효한 이메일 주소를 입력해주세요' });
      return;
    }

    try {
      setLoading(true);
      await createSubscription(email);
      setMessage({
        type: 'success',
        text: '✅ 이메일 구독이 완료되었습니다! 새로운 이벤트 소식을 받아보실 수 있습니다.',
      });
      setCurrentEmail(email);
      setEmail('');
      setIsEditing(false);
    } catch (err: any) {
      if (err.response?.status === 400) {
        setMessage({ type: 'error', text: '이미 구독 중인 이메일입니다' });
      } else {
        setMessage({ type: 'error', text: '구독에 실패했습니다. 다시 시도해주세요' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !email.includes('@')) {
      setMessage({ type: 'error', text: '유효한 이메일 주소를 입력해주세요' });
      return;
    }

    try {
      setLoading(true);
      await updateSubscription(currentEmail, email, true);
      setMessage({
        type: 'success',
        text: '✅ 이메일 주소가 업데이트되었습니다',
      });
      setCurrentEmail(email);
      setEmail('');
      setIsEditing(false);
    } catch (err) {
      setMessage({ type: 'error', text: '업데이트에 실패했습니다. 다시 시도해주세요' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 shadow-lg">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-2 flex items-center justify-center">
            <span className="text-3xl mr-2">📧</span>
            이메일 알림 구독
          </h3>
          <p className="text-gray-600">
            새로운 포켓몬고 이벤트 소식을 이메일로 받아보세요
          </p>
        </div>

        {!currentEmail || isEditing ? (
          <form onSubmit={isEditing ? handleUpdate : handleSubscribe} className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="이메일 주소를 입력하세요"
                className="flex-1 px-4 py-3 rounded-lg border-2 border-gray-300 focus:border-pokemon-blue focus:outline-none"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-pokemon-blue text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '처리 중...' : isEditing ? '이메일 변경' : '구독하기'}
              </button>
              {isEditing && (
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setEmail('');
                    setMessage(null);
                  }}
                  className="px-4 py-3 bg-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-400 transition"
                >
                  취소
                </button>
              )}
            </div>
          </form>
        ) : (
          <div className="text-center space-y-4">
            <div className="bg-green-100 border border-green-300 text-green-800 px-4 py-3 rounded-lg">
              <p className="font-semibold">구독 중: {currentEmail}</p>
            </div>
            <button
              onClick={() => setIsEditing(true)}
              className="px-6 py-2 bg-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-300 transition"
            >
              이메일 변경
            </button>
          </div>
        )}

        {message && (
          <div
            className={`mt-4 px-4 py-3 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-100 border border-green-400 text-green-700'
                : 'bg-red-100 border border-red-400 text-red-700'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="mt-6 text-xs text-gray-500 text-center">
          <p>스팸 메일을 보내지 않으며, 언제든지 구독을 취소할 수 있습니다</p>
        </div>
      </div>
    </div>
  );
}
