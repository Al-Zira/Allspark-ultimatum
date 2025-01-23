from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
import os
from dotenv import load_dotenv, set_key
from pydantic import BaseModel

class Settings(BaseModel):
    market_indices: Optional[Dict[str, str]] = None
    market_sectors: Optional[Dict[str, str]] = None
    technical_analysis: Optional[Dict[str, int]] = None
    portfolio_limits: Optional[Dict[str, float]] = None

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("")
async def get_settings() -> Dict:
    """Get current settings"""
    try:
        # Parse market indices
        indices_str = os.getenv('MARKET_INDICES', '')
        indices = {}
        if indices_str:
            for pair in indices_str.split(','):
                if ':' in pair:
                    symbol, name = pair.split(':')
                    indices[symbol.strip()] = name.strip()

        # Parse market sectors
        sectors_str = os.getenv('MARKET_SECTORS', '')
        sectors = {}
        if sectors_str:
            for pair in sectors_str.split(','):
                if ':' in pair:
                    symbol, name = pair.split(':')
                    sectors[symbol.strip()] = name.strip()

        return {
            "market_indices": indices,
            "market_sectors": sectors,
            "technical_analysis": {
                "rsi_period": int(os.getenv('RSI_PERIOD', 14)),
                "macd_fast": int(os.getenv('MACD_FAST', 12)),
                "macd_slow": int(os.getenv('MACD_SLOW', 26)),
                "macd_signal": int(os.getenv('MACD_SIGNAL', 9)),
                "bollinger_period": int(os.getenv('BOLLINGER_PERIOD', 20)),
                "bollinger_std": int(os.getenv('BOLLINGER_STD', 2))
            },
            "portfolio_limits": {
                "max_assets": int(os.getenv('MAX_ASSETS', 100)),
                "min_position_size": float(os.getenv('MIN_POSITION_SIZE', 0.01)),
                "max_position_size": float(os.getenv('MAX_POSITION_SIZE', 0.5))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def update_settings(settings: Settings) -> Dict:
    """Update settings"""
    try:
        if settings.market_indices is not None:
            indices_str = ','.join([f"{k}:{v}" for k, v in settings.market_indices.items()])
            set_key('.env', 'MARKET_INDICES', indices_str)

        if settings.market_sectors is not None:
            sectors_str = ','.join([f"{k}:{v}" for k, v in settings.market_sectors.items()])
            set_key('.env', 'MARKET_SECTORS', sectors_str)

        if settings.technical_analysis is not None:
            for key, value in settings.technical_analysis.items():
                env_key = key.upper()
                set_key('.env', env_key, str(value))

        if settings.portfolio_limits is not None:
            for key, value in settings.portfolio_limits.items():
                env_key = f"{'_'.join(key.split('_')).upper()}"
                set_key('.env', env_key, str(value))

        # Reload environment variables
        load_dotenv()
        
        return await get_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate")
async def validate_settings() -> Dict:
    """Validate current settings"""
    try:
        issues = []
        warnings = []

        # Validate market indices
        indices_str = os.getenv('MARKET_INDICES', '')
        if not indices_str:
            warnings.append("No market indices configured")
        else:
            for pair in indices_str.split(','):
                if ':' not in pair:
                    issues.append(f"Invalid market index format: {pair}")

        # Validate technical analysis parameters
        ta_params = {
            'RSI_PERIOD': (5, 50),
            'MACD_FAST': (5, 35),
            'MACD_SLOW': (15, 60),
            'MACD_SIGNAL': (5, 25),
            'BOLLINGER_PERIOD': (10, 50),
            'BOLLINGER_STD': (1, 4)
        }

        for param, (min_val, max_val) in ta_params.items():
            value = os.getenv(param)
            if value:
                try:
                    val = int(value)
                    if not min_val <= val <= max_val:
                        warnings.append(f"{param} value {val} is outside recommended range ({min_val}-{max_val})")
                except ValueError:
                    issues.append(f"Invalid {param} value: {value}")

        # Validate portfolio limits
        try:
            min_pos = float(os.getenv('MIN_POSITION_SIZE', 0.01))
            max_pos = float(os.getenv('MAX_POSITION_SIZE', 0.5))
            if min_pos >= max_pos:
                issues.append("MIN_POSITION_SIZE must be less than MAX_POSITION_SIZE")
            if not 0 < min_pos < 1:
                issues.append("MIN_POSITION_SIZE must be between 0 and 1")
            if not 0 < max_pos <= 1:
                issues.append("MAX_POSITION_SIZE must be between 0 and 1")
        except ValueError:
            issues.append("Invalid position size values")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 