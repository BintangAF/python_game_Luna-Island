from world.rain_effect import RainEffect
from world.snow_effect import SnowEffect
from world.autumn_effect import AutumnEffect


class WeatherManager:
    
    def __init__(self):
        self.rain = RainEffect()
        self.snow = SnowEffect()
        self.autumn = AutumnEffect()
        
        self.current_effect = None
        self.current_type = None
    
    def set_weather(self, weather_type: str | None) -> None:
        """Set cuaca aktif: 'rain', 'snow', 'autumn', atau None"""
        # Nonaktifkan semua
        self.rain.set_active(False)
        self.snow.set_active(False)
        self.autumn.set_active(False)
        
        # Aktifkan yang dipilih
        if weather_type == 'rain':
            self.rain.set_active(True)
            self.current_effect = self.rain
        elif weather_type == 'snow':
            self.snow.set_active(True)
            self.current_effect = self.snow
        elif weather_type == 'autumn':
            self.autumn.set_active(True)
            self.current_effect = self.autumn
        else:
            self.current_effect = None
        
        self.current_type = weather_type
    
    def update(self, dt: float) -> None:
        """Update efek cuaca aktif"""
        if self.current_effect:
            self.current_effect.update(dt)
    
    def draw_darkness(self, alpha: int) -> None:
        """Draw darkness overlay (hanya untuk rain effect)"""
        if self.current_effect and hasattr(self.current_effect, 'draw_darkness'):
            self.current_effect.draw_darkness(alpha)
    
    # Method untuk kompatibilitas dengan kode lama
    def set_rain(self, value: bool) -> None:
        """Set rain active (kompatibilitas dengan WeatherOverlay)"""
        if value:
            self.set_weather('rain')
        elif self.current_type == 'rain':
            self.set_weather(None)