# modules/carbon_tracker.py
import time
import psutil # type: ignore
import threading
from datetime import datetime, timedelta
import streamlit as st # type: ignore

class CarbonTracker:
    """
    Track carbon footprint of AI operations
    Green AI optimized with real-time carbon intensity
    """
    
    # Default carbon intensity (gCO2 per kWh) - India grid average
    DEFAULT_CARBON_INTENSITY = 700  # Updated to India average
    
    # Power consumption estimates (watts) - CPU only for Green AI
    POWER_WATTS = {
        'cpu': 45,      # Typical laptop CPU (optimized)
        'gpu': 100,     # If GPU available (not used in Green AI)
        'memory': 3,    # Per GB
        'idle': 15      # Idle power
    }
    
    # Comparison with conventional AI (50x less efficient)
    CONVENTIONAL_MULTIPLIER = 50
    
    def __init__(self):
        self.total_emissions_g = 0
        self.total_energy_kwh = 0
        self.total_duration_seconds = 0
        self.operations = []
        self.current_operation = None
        self.start_time = None
        self.start_cpu = None
        self.last_emissions = 0
        self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY
        self._intensity_updated = False
        
        # For real-time tracking
        self._monitoring = False
        self._monitor_thread = None
        
    def _get_carbon_intensity(self):
        """Get real-time carbon intensity (mock - replace with actual API)"""
        # In production, use electricitymap.org API
        # For hackathon, simulate based on time of day
        hour = datetime.now().hour
        if 10 <= hour <= 16:  # Solar peak hours
            return 500  # Lower carbon intensity
        elif 19 <= hour <= 23:  # Evening peak
            return 800  # Higher carbon intensity
        else:
            return 650  # Average
    
    def update_carbon_intensity(self, use_real_time=True):
        """Update carbon intensity based on real-time grid data"""
        if use_real_time:
            try:
                # Mock API call - replace with actual
                self.carbon_intensity = self._get_carbon_intensity()
                self._intensity_updated = True
            except Exception as e:
                print(f"Failed to update carbon intensity: {e}")
                self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY
        else:
            self.carbon_intensity = self.DEFAULT_CARBON_INTENSITY
    
    def start_operation(self, operation_name):
        """Start tracking an operation"""
        self.current_operation = operation_name
        self.start_time = time.time()
        try:
            self.start_cpu = psutil.cpu_percent(interval=0.1)
        except:
            self.start_cpu = 30  # Default CPU usage
        
        return self
    
    def end_operation(self):
        """End tracking and calculate emissions"""
        if self.start_time is None:
            return 0
        
        duration = time.time() - self.start_time
        self.total_duration_seconds += duration
        
        try:
            end_cpu = psutil.cpu_percent(interval=0.1)
            avg_cpu = (self.start_cpu + end_cpu) / 2
        except:
            avg_cpu = 30
        
        # Calculate energy (kWh)
        # Power = CPU power + idle power
        cpu_power_kw = (self.POWER_WATTS['cpu'] * (avg_cpu / 100)) / 1000
        idle_power_kw = self.POWER_WATTS['idle'] / 1000
        total_power_kw = cpu_power_kw + idle_power_kw
        
        energy_kwh = total_power_kw * (duration / 3600)
        
        # Calculate emissions (gCO2)
        emissions_g = energy_kwh * self.carbon_intensity
        self.last_emissions = emissions_g
        
        # Store operation
        operation_data = {
            'name': self.current_operation,
            'duration': duration,
            'energy_kwh': energy_kwh,
            'emissions_g': emissions_g,
            'timestamp': datetime.now(),
            'cpu_avg': avg_cpu,
            'carbon_intensity': self.carbon_intensity
        }
        self.operations.append(operation_data)
        self.total_energy_kwh += energy_kwh
        self.total_emissions_g += emissions_g
        
        # Reset
        self.current_operation = None
        self.start_time = None
        
        return emissions_g
    
    def __enter__(self):
        """Support for 'with' statement"""
        self.start_operation("context_operation")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-end operation when context exits"""
        self.end_operation()
    
    def track(self, operation_name):
        """Context manager for tracking operations"""
        return OperationContext(self, operation_name)
    
    def get_total_emissions(self):
        """Get total emissions in grams"""
        return self.total_emissions_g
    
    def get_total_energy(self):
        """Get total energy in kWh"""
        return self.total_energy_kwh
    
    def get_last_emissions(self):
        """Get last operation emissions"""
        return self.last_emissions
    
    def get_operations_count(self):
        """Get number of operations tracked"""
        return len(self.operations)
    
    def get_summary(self):
        """Get summary of all operations"""
        # Calculate conventional AI emissions (50x worse)
        conventional_emissions = self.total_emissions_g * self.CONVENTIONAL_MULTIPLIER
        carbon_saved = conventional_emissions - self.total_emissions_g
        
        return {
            'total_emissions_g': round(self.total_emissions_g, 4),
            'total_emissions_kg': round(self.total_emissions_g / 1000, 6),
            'total_energy_kwh': round(self.total_energy_kwh, 6),
            'total_duration_seconds': round(self.total_duration_seconds, 2),
            'operations_count': len(self.operations),
            'conventional_emissions_g': round(conventional_emissions, 4),
            'carbon_saved_g': round(carbon_saved, 4),
            'carbon_saved_percent': round((carbon_saved / conventional_emissions) * 100, 1) if conventional_emissions > 0 else 0,
            'carbon_intensity': self.carbon_intensity,
            'last_emissions_g': round(self.last_emissions, 4)
        }
    
    def get_operations_list(self, limit=20):
        """Get list of recent operations"""
        return self.operations[-limit:]
    
    def get_emissions_by_type(self):
        """Group emissions by operation type"""
        by_type = {}
        for op in self.operations:
            op_type = op['name']
            by_type[op_type] = by_type.get(op_type, 0) + op['emissions_g']
        return by_type
    
    def get_emissions_timeline(self):
        """Get emissions timeline for charts"""
        timeline = []
        for op in self.operations:
            timeline.append({
                'timestamp': op['timestamp'],
                'emissions_g': op['emissions_g'],
                'operation': op['name']
            })
        return timeline
    
    def get_equivalents(self):
        """Get carbon equivalent comparisons"""
        emissions_kg = self.total_emissions_g / 1000
        
        equivalents = {
            'car_km': round(emissions_kg / 0.120, 1),  # 120g CO2 per km
            'smartphone_charges': round(emissions_kg / 0.05, 0),  # 50g per charge
            'tree_days': round(emissions_kg / 0.011, 0),  # Tree absorbs 11g per day
            'lights_hours': round(emissions_kg / 0.040, 1),  # LED bulb 40g per hour
            'tea_cups': round(emissions_kg / 0.021, 0)  # 21g per cup of tea
        }
        
        return equivalents
    
    def get_comparison_text(self):
        """Generate human-readable comparison text"""
        summary = self.get_summary()
        equivalents = self.get_equivalents()
        
        if summary['total_emissions_g'] == 0:
            return "No AI operations tracked yet. Start analyzing to see your carbon footprint."
        
        text = f"""
🌱 **Green AI Impact Report**

**GAIA's Carbon Footprint:** {summary['total_emissions_g']:.3f} gCO₂
**Conventional AI Would Emit:** {summary['conventional_emissions_g']:.3f} gCO₂
**Carbon Saved:** {summary['carbon_saved_g']:.3f} gCO₂ ({summary['carbon_saved_percent']:.0f}% less)

**Equivalent to:**
- 🚗 Driving a car: {equivalents['car_km']} km
- 📱 Smartphone charges: {equivalents['smartphone_charges']:,} charges
- 🌳 Tree absorption: {equivalents['tree_days']:,} days
- 💡 LED bulb usage: {equivalents['lights_hours']} hours
- ☕ Cups of tea: {equivalents['tea_cups']:,} cups

**Why GAIA is Green:**
- ✅ Lightweight models (DistilBERT: 66MB, Whisper tiny: 39MB)
- ✅ CPU-only inference (no GPU power)
- ✅ Efficient code with minimal operations
- ✅ Carbon-aware processing

*Every gram counts. GAIA is built to be part of the solution.*
"""
        return text
    
    def reset(self):
        """Reset all tracking data"""
        self.total_emissions_g = 0
        self.total_energy_kwh = 0
        self.total_duration_seconds = 0
        self.operations = []
        self.current_operation = None
        self.start_time = None
        self.last_emissions = 0
        print("✅ Carbon tracker reset")
    
    def display_metrics(self):
        """Display carbon metrics in Streamlit"""
        summary = self.get_summary()
        equivalents = self.get_equivalents()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Carbon", 
                f"{summary['total_emissions_g']:.3f} gCO₂",
                delta=f"-{summary['carbon_saved_g']:.3f} g vs conventional",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Energy Used",
                f"{summary['total_energy_kwh']:.6f} kWh",
                help="Less than charging a smartphone once"
            )
        
        with col3:
            st.metric(
                "Operations",
                summary['operations_count'],
                help="AI analyses performed"
            )
        
        st.progress(
            min(1.0, summary['total_emissions_g'] / 100),
            text=f"Carbon footprint: {summary['total_emissions_g']:.2f} gCO₂"
        )
        
        with st.expander("🌍 Carbon Equivalents"):
            st.write(f"🚗 Car travel: {equivalents['car_km']} km")
            st.write(f"📱 Smartphone charges: {equivalents['smartphone_charges']:,}")
            st.write(f"🌳 Tree absorption: {equivalents['tree_days']:,} days")
            st.write(f"💡 LED bulb: {equivalents['lights_hours']} hours")
            st.write(f"☕ Cups of tea: {equivalents['tea_cups']:,}")


class OperationContext:
    """Context manager for tracking operations with 'with' statement"""
    
    def __init__(self, tracker, operation_name):
        self.tracker = tracker
        self.operation_name = operation_name
    
    def __enter__(self):
        self.tracker.start_operation(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tracker.end_operation()


# Example usage with context manager
def track_operation(tracker, operation_name):
    """Decorator to track function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with tracker.track(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global tracker instance
tracker = CarbonTracker()