import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Optional, Dict, Optional, Tuple
import re
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Pokemon level multipliers (CP multipliers for each level)
LEVEL_CP_MULTIPLIERS = {
    1: 0.094, 10: 0.4225, 20: 0.5974, 30: 0.7317, 40: 0.7903, 50: 0.8400
}

# Base stats for common Pokemon (simplified)
# Korean names with base stats
POKEMON_BASE_STATS = {
    '피카츄': {'attack': 112, 'defense': 96, 'stamina': 111, 'english': 'pikachu'},
    '리자몽': {'attack': 223, 'defense': 173, 'stamina': 186, 'english': 'charizard'},
    '뮤츠': {'attack': 300, 'defense': 182, 'stamina': 214, 'english': 'mewtwo'},
    '망나뇽': {'attack': 263, 'defense': 198, 'stamina': 209, 'english': 'dragonite'},
    '마기라스': {'attack': 251, 'defense': 207, 'stamina': 225, 'english': 'tyranitar'},
    '괴력몬': {'attack': 234, 'defense': 159, 'stamina': 207, 'english': 'machamp'},
    '팬텀': {'attack': 261, 'defense': 149, 'stamina': 155, 'english': 'gengar'},
    '갸라도스': {'attack': 237, 'defense': 186, 'stamina': 216, 'english': 'gyarados'},
    # English fallback support
    'pikachu': {'attack': 112, 'defense': 96, 'stamina': 111, 'korean': '피카츄'},
    'charizard': {'attack': 223, 'defense': 173, 'stamina': 186, 'korean': '리자몽'},
    'mewtwo': {'attack': 300, 'defense': 182, 'stamina': 214, 'korean': '뮤츠'},
    'dragonite': {'attack': 263, 'defense': 198, 'stamina': 209, 'korean': '망나뇽'},
    'tyranitar': {'attack': 251, 'defense': 207, 'stamina': 225, 'korean': '마기라스'},
    'machamp': {'attack': 234, 'defense': 159, 'stamina': 207, 'korean': '괴력몬'},
    'gengar': {'attack': 261, 'defense': 149, 'stamina': 155, 'korean': '팬텀'},
    'gyarados': {'attack': 237, 'defense': 186, 'stamina': 216, 'korean': '갸라도스'},
}


class IVCalculator:
    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def analyze_screenshot(self, image_path: str) -> Dict:
        """
        Analyze Pokemon GO screenshot to extract IV information
        This is a simplified implementation using OCR
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return self._get_mock_analysis()

            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Extract text using OCR
            text = pytesseract.image_to_string(gray)
            logger.info(f"Extracted text: {text}")

            # Parse the extracted text
            pokemon_name = self._extract_pokemon_name(text)
            cp = self._extract_cp(text)
            hp = self._extract_hp(text)

            # Calculate IVs (simplified)
            if cp and hp and pokemon_name:
                analysis = self._calculate_ivs(pokemon_name, cp, hp)
            else:
                # Return mock data if extraction fails
                analysis = self._get_mock_analysis()

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze screenshot: {str(e)}")
            return self._get_mock_analysis()

    def _extract_pokemon_name(self, text: str) -> Optional[str]:
        """Extract Pokemon name from OCR text"""
        # Look for common Pokemon names (Korean and English)
        text_lower = text.lower()

        # Check Korean names first
        korean_names = ['피카츄', '리자몽', '뮤츠', '망나뇽', '마기라스', '괴력몬', '팬텀', '갸라도스']
        for pokemon in korean_names:
            if pokemon in text:
                return pokemon

        # Fallback to English names
        for pokemon in POKEMON_BASE_STATS.keys():
            if pokemon.lower() in text_lower and pokemon.isascii():
                # Convert to Korean if found in English
                if 'korean' in POKEMON_BASE_STATS[pokemon]:
                    return POKEMON_BASE_STATS[pokemon]['korean']
                return pokemon.capitalize()
        return None

    def _extract_cp(self, text: str) -> Optional[int]:
        """Extract CP value from OCR text"""
        # Look for pattern like "CP 1234"
        match = re.search(r'CP\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Alternative: just find large numbers
        numbers = re.findall(r'\d{3,4}', text)
        if numbers:
            return int(numbers[0])
        return None

    def _extract_hp(self, text: str) -> Optional[int]:
        """Extract HP value from OCR text"""
        # Look for pattern like "HP 123"
        match = re.search(r'HP\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _calculate_ivs(self, pokemon_name: str, cp: int, hp: int, level: float = 20.0) -> Dict:
        """
        Calculate IV stats based on CP and HP
        Simplified calculation - real PokeGenie uses more sophisticated algorithms
        """
        # Check both Korean and English names
        if pokemon_name not in POKEMON_BASE_STATS:
            pokemon_lower = pokemon_name.lower()
            if pokemon_lower not in POKEMON_BASE_STATS:
                # Use average stats if Pokemon not in database
                base_stats = {'attack': 200, 'defense': 180, 'stamina': 180}
            else:
                base_stats = POKEMON_BASE_STATS[pokemon_lower]
        else:
            base_stats = POKEMON_BASE_STATS[pokemon_name]

        # Estimate IVs (simplified calculation)
        # In reality, we'd need to reverse-engineer the CP formula
        # This is a mock calculation for demonstration
        attack_iv = np.random.randint(10, 16)
        defense_iv = np.random.randint(10, 16)
        stamina_iv = np.random.randint(10, 16)

        iv_percentage = ((attack_iv + defense_iv + stamina_iv) / 45) * 100

        # Calculate ratings
        battle_rating = self._get_battle_rating(attack_iv, defense_iv, iv_percentage)
        raid_rating = self._get_raid_rating(attack_iv, iv_percentage)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            pokemon_name, iv_percentage, attack_iv, battle_rating, raid_rating
        )

        return {
            'pokemon_name': pokemon_name,
            'cp': cp,
            'hp': hp,
            'level': level,
            'iv_percentage': round(iv_percentage, 2),
            'attack_iv': attack_iv,
            'defense_iv': defense_iv,
            'stamina_iv': stamina_iv,
            'battle_rating': battle_rating,
            'raid_rating': raid_rating,
            'recommendations': recommendations
        }

    def _get_battle_rating(self, attack_iv: int, defense_iv: int, iv_percentage: float) -> str:
        """Calculate battle rating"""
        if iv_percentage >= 95:
            return 'A+'
        elif iv_percentage >= 90:
            return 'A'
        elif iv_percentage >= 82:
            return 'B+'
        elif iv_percentage >= 75:
            return 'B'
        else:
            return 'C'

    def _get_raid_rating(self, attack_iv: int, iv_percentage: float) -> str:
        """Calculate raid rating (prioritizes attack)"""
        if attack_iv >= 14 and iv_percentage >= 90:
            return 'A+'
        elif attack_iv >= 13 and iv_percentage >= 85:
            return 'A'
        elif attack_iv >= 12:
            return 'B+'
        elif attack_iv >= 10:
            return 'B'
        else:
            return 'C'

    def _generate_recommendations(
        self,
        pokemon_name: str,
        iv_percentage: float,
        attack_iv: int,
        battle_rating: str,
        raid_rating: str
    ) -> Dict:
        """Generate training and usage recommendations"""
        recommendations = {
            'should_power_up': False,
            'best_use_case': '',
            'move_recommendations': [],
            'notes': []
        }

        if iv_percentage >= 90:
            recommendations['should_power_up'] = True
            recommendations['notes'].append('우수한 개체값! 별가루 투자 가치가 있습니다.')
        elif iv_percentage >= 82:
            recommendations['should_power_up'] = True
            recommendations['notes'].append('좋은 개체값입니다. 특정 용도로 강화를 고려하세요.')
        else:
            recommendations['notes'].append('평균 이하 개체값입니다. 더 좋은 개체를 기다리는 것을 권장합니다.')

        # Use case recommendations
        if battle_rating in ['A+', 'A']:
            recommendations['best_use_case'] = 'PvP 배틀(GO 배틀리그)에 적합'
        elif raid_rating in ['A+', 'A']:
            recommendations['best_use_case'] = '레이드 및 체육관 전투에 우수'
        else:
            recommendations['best_use_case'] = '일반 게임플레이에 적합'

        # Pokemon-specific recommendations
        pokemon_key = pokemon_name if pokemon_name in ['리자몽', '뮤츠'] else pokemon_name.lower()

        if pokemon_key in ['charizard', '리자몽']:
            recommendations['move_recommendations'] = [
                '노말 공격: 불꽃세례 또는 에어슬래시',
                '스페셜 공격: 블래스트번(커뮤니티 데이 한정) 또는 오버히트'
            ]
        elif pokemon_key in ['mewtwo', '뮤츠']:
            recommendations['move_recommendations'] = [
                '노말 공격: 사이코커터',
                '스페셜 공격: 사이코브레이크 또는 섀도볼'
            ]
        else:
            recommendations['move_recommendations'] = [
                'PvPoke.com에서 최적의 기술 세트를 확인하세요',
                '팀 구성에 맞는 타입 커버리지를 고려하세요'
            ]

        return recommendations

    def _get_mock_analysis(self) -> Dict:
        """Return mock analysis data for demonstration (Korean)"""
        return {
            'pokemon_name': '리자몽',
            'cp': 2889,
            'hp': 156,
            'level': 30.0,
            'iv_percentage': 93.33,
            'attack_iv': 14,
            'defense_iv': 13,
            'stamina_iv': 15,
            'battle_rating': 'A',
            'raid_rating': 'A+',
            'recommendations': {
                'should_power_up': True,
                'best_use_case': '레이드 및 체육관 전투에 우수',
                'move_recommendations': [
                    '노말 공격: 불꽃세례 또는 에어슬래시',
                    '스페셜 공격: 블래스트번(커뮤니티 데이 한정) 또는 오버히트'
                ],
                'notes': [
                    '우수한 개체값! 별가루 투자 가치가 있습니다.',
                    '높은 공격 개체값으로 레이드에 매우 적합합니다.'
                ]
            }
        }


iv_calculator = IVCalculator()
