#!/usr/bin/env python3
"""
YouTube @handle에서 channel_id를 추출하는 스크립트
"""
import httpx
import re
import asyncio

async def get_channel_id_from_handle(handle: str) -> str:
    """
    YouTube @handle에서 channel_id 추출
    
    Args:
        handle: YouTube 핸들명 (예: @profwalnet 또는 profwalnet)
    
    Returns:
        channel_id 또는 None
    """
    # @ 기호 제거
    if handle.startswith('@'):
        handle = handle[1:]
    
    url = f"https://www.youtube.com/@{handle}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # HTML에서 channel_id 찾기
            # 방법 1: "channelId":"UCxxxx" 패턴
            pattern1 = r'"channelId":"(UC[^"]+)"'
            match = re.search(pattern1, response.text)
            if match:
                return match.group(1)
            
            # 방법 2: /channel/UCxxxx URL 패턴
            pattern2 = r'/channel/(UC[^/"]+)'
            match = re.search(pattern2, response.text)
            if match:
                return match.group(1)
            
            # 방법 3: "externalId":"UCxxxx" 패턴
            pattern3 = r'"externalId":"(UC[^"]+)"'
            match = re.search(pattern3, response.text)
            if match:
                return match.group(1)
            
            print(f"⚠️  {handle}: channel_id를 찾을 수 없습니다")
            return None
            
    except Exception as e:
        print(f"❌ {handle}: 오류 - {str(e)}")
        return None

async def main():
    # 사용자가 제공한 11개 채널 핸들
    handles = [
        "profwalnet",           # 이로치 헌터 호두박사
        "선지남",                # 선봉지는남자 선지남  
        "gobale2xbro",          # 고배리 이배속 아저씨
        "YvelCons",             # YvelCons PoGo
        "LuisAngelTC10",        # LuisAngelTC10
        "MarckPoGoW",           # MarckPoGoW
        "ItsAXN",               # ItsAXN
        "pikataro55",           # 피카타로 (일본어)
        "UCWNAsZwR-I219wzIKdTQ-Gg",  # 일본 채널 (이미 channel_id)
        "Reis2TheOccasion",     # Reis2TheOccasion
        "KingGBL",              # KingGBL
    ]
    
    print("🔍 YouTube 채널 ID 추출 중...\n")
    
    channel_ids = []
    for handle in handles:
        # 이미 channel_id 형식이면 그대로 사용
        if handle.startswith("UC") and len(handle) > 20:
            channel_ids.append(handle)
            print(f"✅ {handle}: {handle} (이미 channel_id)")
            continue
        
        channel_id = await get_channel_id_from_handle(handle)
        if channel_id:
            channel_ids.append(channel_id)
            print(f"✅ @{handle}: {channel_id}")
        else:
            print(f"❌ @{handle}: 실패")
        
        # API 제한 방지를 위한 딜레이
        await asyncio.sleep(1)
    
    print(f"\n\n📋 총 {len(channel_ids)}개 채널 ID 추출 완료\n")
    print("=" * 80)
    print("\n.env 파일에 추가할 RSS 피드 URL:\n")
    
    rss_urls = [f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}" for cid in channel_ids]
    print("YOUTUBE_RSS_FEEDS=" + ",".join(rss_urls))
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
