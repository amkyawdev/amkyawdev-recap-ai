"""
GPU Device Management
Handles GPU detection, memory management, and resource allocation
"""
import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Try to import GPU libraries
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available, GPU support disabled")

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    logger.warning("pynvml not available, NVIDIA GPU monitoring disabled")


@dataclass
class GPUInfo:
    """GPU device information"""
    id: int
    name: str
    memory_total: int
    memory_used: int
    memory_free: int
    utilization: float
    temperature: float
    power_draw: float


class GPUMonitor:
    """Monitor GPU status"""
    
    def __init__(self):
        self.initialized = False
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.initialized = True
                self.device_count = pynvml.nvmlDeviceGetCount()
            except Exception as e:
                logger.warning(f"Failed to initialize NVML: {e}")
    
    def get_gpu_info(self, device_id: int = 0) -> Optional[GPUInfo]:
        """Get information about a specific GPU"""
        if not self.initialized:
            return None
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            try:
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temperature = 0
            
            try:
                power_draw = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            except:
                power_draw = 0
            
            return GPUInfo(
                id=device_id,
                name=name,
                memory_total=memory_info.total,
                memory_used=memory_info.used,
                memory_free=memory_info.free,
                utilization=utilization.gpu,
                temperature=temperature,
                power_draw=power_draw
            )
        except Exception as e:
            logger.error(f"Failed to get GPU info: {e}")
            return None
    
    def get_all_gpus(self) -> List[GPUInfo]:
        """Get information about all available GPUs"""
        gpus = []
        if not self.initialized:
            return gpus
        
        for i in range(self.device_count):
            info = self.get_gpu_info(i)
            if info:
                gpus.append(info)
        
        return gpus
    
    def get_available_memory(self, device_id: int = 0) -> int:
        """Get available GPU memory in bytes"""
        if not self.initialized:
            return 0
        
        info = self.get_gpu_info(device_id)
        return info.memory_free if info else 0
    
    def release(self):
        """Release NVML resources"""
        if self.initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


class GPUMemoryPool:
    """GPU memory pool for efficient memory allocation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.allocated_blocks: Dict[int, Dict] = {}
        self.total_allocated = 0
    
    @contextmanager
    def allocate(self, size_mb: float, device_id: int = 0):
        """
        Context manager for GPU memory allocation
        
        Args:
            size_mb: Memory size in megabytes
            device_id: GPU device ID
        """
        if not TORCH_AVAILABLE:
            yield None
            return
        
        size_bytes = int(size_mb * 1024 * 1024)
        
        try:
            # Check available memory
            if torch.cuda.is_available():
                torch.cuda.set_device(device_id)
                torch.cuda.empty_cache()
                
                # Allocate
                self.allocated_blocks[device_id] = {
                    'size': size_bytes,
                    'tensor': torch.empty(size_bytes, dtype=torch.uint8, device=f'cuda:{device_id}')
                }
                self.total_allocated += size_bytes
                
                logger.debug(f"Allocated {size_mb}MB GPU memory on device {device_id}")
                
                yield self.allocated_blocks[device_id]['tensor']
            else:
                yield None
        except Exception as e:
            logger.error(f"GPU allocation failed: {e}")
            yield None
        finally:
            # Cleanup
            if device_id in self.allocated_blocks:
                del self.allocated_blocks[device_id]['tensor']
                del self.allocated_blocks[device_id]
                self.total_allocated -= size_bytes
    
    def clear_cache(self):
        """Clear GPU memory cache"""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()


class GPUManager:
    """
    Main GPU manager for the application
    Handles device selection, resource allocation, and cleanup
    """
    
    def __init__(self):
        self.monitor = GPUMonitor()
        self.memory_pool = GPUMemoryPool()
        self._available_devices: List[int] = []
        self._device_locks: Dict[int, int] = {}  # device_id -> lock count
        
        self._detect_devices()
    
    def _detect_devices(self):
        """Detect available GPU devices"""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self._available_devices = list(range(torch.cuda.device_count()))
            logger.info(f"Found {len(self._available_devices)} CUDA device(s)")
            
            for i in self._available_devices:
                name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                logger.info(f"  GPU {i}: {name} ({memory:.1f}GB)")
        else:
            logger.warning("No CUDA devices available, running in CPU mode")
            self._available_devices = []
    
    @property
    def is_available(self) -> bool:
        """Check if GPU is available"""
        return len(self._available_devices) > 0
    
    @property
    def device_count(self) -> int:
        """Get number of available devices"""
        return len(self._available_devices)
    
    def get_device(self, device_id: Optional[int] = None) -> str:
        """
        Get device string for PyTorch
        
        Args:
            device_id: Specific device ID, or None for auto-selection
            
        Returns:
            Device string like 'cuda:0' or 'cpu'
        """
        if not self.is_available:
            return 'cpu'
        
        if device_id is None:
            # Auto-select least utilized device
            device_id = self._select_best_device()
        elif device_id not in self._available_devices:
            logger.warning(f"Device {device_id} not available, using 0")
            device_id = 0
        
        return f'cuda:{device_id}'
    
    def _select_best_device(self) -> int:
        """Select the best device based on available memory"""
        if not self.monitor.initialized:
            return 0
        
        best_device = 0
        max_free_memory = 0
        
        for device_id in self._available_devices:
            info = self.monitor.get_gpu_info(device_id)
            if info and info.memory_free > max_free_memory:
                max_free_memory = info.memory_free
                best_device = device_id
        
        return best_device
    
    def acquire_device(self, device_id: Optional[int] = None) -> int:
        """
        Acquire a device lock (increments lock count)
        
        Args:
            device_id: Specific device ID
            
        Returns:
            Acquired device ID
        """
        if device_id is None:
            device_id = self._select_best_device()
        
        self._device_locks[device_id] = self._device_locks.get(device_id, 0) + 1
        return device_id
    
    def release_device(self, device_id: int):
        """Release a device lock (decrements lock count)"""
        if device_id in self._device_locks:
            self._device_locks[device_id] -= 1
            if self._device_locks[device_id] <= 0:
                del self._device_locks[device_id]
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall GPU status"""
        status = {
            'available': self.is_available,
            'device_count': self.device_count,
            'devices': []
        }
        
        for device_id in self._available_devices:
            info = self.monitor.get_gpu_info(device_id)
            if info:
                status['devices'].append({
                    'id': info.id,
                    'name': info.name,
                    'memory_total_gb': info.memory_total / (1024**3),
                    'memory_used_gb': info.memory_used / (1024**3),
                    'memory_free_gb': info.memory_free / (1024**3),
                    'utilization_percent': info.utilization,
                    'temperature_celsius': info.temperature,
                    'power_watts': info.power_draw,
                    'locked': self._device_locks.get(device_id, 0) > 0
                })
        
        return status
    
    def cleanup(self):
        """Cleanup all GPU resources"""
        self.memory_pool.clear_cache()
        self.monitor.release()


# Global GPU manager instance
gpu_manager = GPUManager()
