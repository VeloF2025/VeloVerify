"""
Performance Optimizer for VeloVerify
Provides optimized data processing capabilities for large files with memory management.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Callable, Any, Iterator, Tuple
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
import psutil
import os
import logging
from datetime import datetime
import tempfile
from pathlib import Path

from config import get_config

class MemoryMonitor:
    """Monitor memory usage and provide optimization suggestions."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = self.get_memory_usage()
        self.logger = logging.getLogger(__name__)
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_percent(self) -> float:
        """Get current memory usage as percentage of system memory."""
        return self.process.memory_percent()
    
    def check_memory_pressure(self) -> bool:
        """Check if memory usage is approaching system limits."""
        return self.get_memory_percent() > 80.0
    
    def log_memory_usage(self, context: str = ""):
        """Log current memory usage."""
        current = self.get_memory_usage()
        percent = self.get_memory_percent()
        delta = current - self.initial_memory
        
        self.logger.info(f"Memory Usage {context}: {current:.1f}MB ({percent:.1f}%) - Delta: {delta:+.1f}MB")

class ChunkedDataProcessor:
    """Process large datasets in chunks to manage memory usage."""
    
    def __init__(self, chunk_size: int = None, config=None):
        self.config = config or get_config()
        self.chunk_size = chunk_size or self.config.get('processing.chunk_size', 10000)
        self.memory_monitor = MemoryMonitor()
        self.logger = logging.getLogger(__name__)
        self.temp_files = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup_temp_files()
    
    def read_csv_chunked(self, file_path: str, **kwargs) -> Iterator[pd.DataFrame]:
        """Read CSV file in chunks."""
        self.logger.info(f"Reading CSV in chunks of {self.chunk_size}")
        
        try:
            chunk_reader = pd.read_csv(file_path, chunksize=self.chunk_size, **kwargs)
            chunk_count = 0
            
            for chunk in chunk_reader:
                chunk_count += 1
                self.logger.debug(f"Processing chunk {chunk_count}: {len(chunk)} rows")
                yield chunk
                
                # Monitor memory and force garbage collection if needed
                if self.memory_monitor.check_memory_pressure():
                    self.logger.warning("High memory usage detected, forcing garbage collection")
                    gc.collect()
                    
        except Exception as e:
            self.logger.error(f"Error reading CSV chunks: {e}")
            raise
    
    def process_chunks_parallel(self, 
                               chunks: List[pd.DataFrame], 
                               processor_func: Callable[[pd.DataFrame], pd.DataFrame],
                               max_workers: int = None) -> List[pd.DataFrame]:
        """Process chunks in parallel using threads."""
        if not max_workers:
            max_workers = min(self.config.get('advanced.max_worker_threads', 4), len(chunks))
        
        self.logger.info(f"Processing {len(chunks)} chunks with {max_workers} workers")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(processor_func, chunk) for chunk in chunks]
            
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    results.append(result)
                    self.logger.debug(f"Completed chunk {i+1}/{len(chunks)}")
                except Exception as e:
                    self.logger.error(f"Error processing chunk {i+1}: {e}")
                    raise
        
        return results
    
    def merge_processed_chunks(self, chunks: List[pd.DataFrame]) -> pd.DataFrame:
        """Merge processed chunks back into a single dataframe."""
        self.logger.info(f"Merging {len(chunks)} processed chunks")
        
        try:
            # Filter out empty chunks
            non_empty_chunks = [chunk for chunk in chunks if len(chunk) > 0]
            
            if not non_empty_chunks:
                return pd.DataFrame()
            
            # Use concat with ignore_index for better performance
            result = pd.concat(non_empty_chunks, ignore_index=True)
            
            # Force garbage collection
            del chunks, non_empty_chunks
            gc.collect()
            
            self.logger.info(f"Merged result: {len(result)} rows")
            return result
            
        except Exception as e:
            self.logger.error(f"Error merging chunks: {e}")
            raise
    
    def save_temp_chunk(self, chunk: pd.DataFrame, prefix: str = "chunk") -> str:
        """Save chunk to temporary file and return path."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.csv', 
            prefix=f"veloverify_{prefix}_",
            delete=False
        )
        
        chunk.to_csv(temp_file.name, index=False)
        self.temp_files.append(temp_file.name)
        
        self.logger.debug(f"Saved chunk to temporary file: {temp_file.name}")
        return temp_file.name
    
    def load_temp_chunk(self, file_path: str) -> pd.DataFrame:
        """Load chunk from temporary file."""
        return pd.read_csv(file_path)
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        if self.config.get('advanced.temp_file_cleanup', True):
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        self.logger.debug(f"Deleted temporary file: {temp_file}")
                except Exception as e:
                    self.logger.warning(f"Could not delete temporary file {temp_file}: {e}")
            
            self.temp_files.clear()

class OptimizedDataProcessor:
    """Main optimized data processor with performance enhancements."""
    
    def __init__(self, progress_callback: Callable = None, config=None):
        self.config = config or get_config()
        self.progress_callback = progress_callback
        self.memory_monitor = MemoryMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Performance settings
        self.chunk_size = self.config.get('processing.chunk_size', 10000)
        self.use_parallel = self.config.get('advanced.parallel_processing', True)
        self.memory_optimization = self.config.get('advanced.memory_optimization', True)
        self.max_workers = self.config.get('advanced.max_worker_threads', 4)
        
        # Statistics
        self.processing_stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'peak_memory_mb': 0,
            'chunks_processed': 0,
            'optimization_level': 'standard'
        }
    
    def _update_progress(self, message: str, percentage: float = 0):
        """Update progress callback with memory info."""
        if self.progress_callback:
            memory_mb = self.memory_monitor.get_memory_usage()
            detailed_message = f"{message} (Memory: {memory_mb:.1f}MB)"
            self.progress_callback(detailed_message, percentage)
        
        # Update peak memory
        current_memory = self.memory_monitor.get_memory_usage()
        if current_memory > self.processing_stats['peak_memory_mb']:
            self.processing_stats['peak_memory_mb'] = current_memory
    
    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize dataframe memory usage."""
        if not self.memory_optimization:
            return df
        
        self.logger.info("Optimizing dataframe memory usage")
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024
        
        optimized_df = df.copy()
        
        # Optimize numeric columns
        for col in optimized_df.select_dtypes(include=['int64']).columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='integer')
        
        for col in optimized_df.select_dtypes(include=['float64']).columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        # Optimize string columns
        for col in optimized_df.select_dtypes(include=['object']).columns:
            num_unique_values = len(optimized_df[col].unique())
            num_total_values = len(optimized_df[col])
            
            # If less than 50% unique values, convert to category
            if num_unique_values / num_total_values < 0.5:
                optimized_df[col] = optimized_df[col].astype('category')
        
        new_memory = optimized_df.memory_usage(deep=True).sum() / 1024 / 1024
        memory_reduction = ((original_memory - new_memory) / original_memory) * 100
        
        self.logger.info(f"Memory optimization: {original_memory:.1f}MB -> {new_memory:.1f}MB ({memory_reduction:.1f}% reduction)")
        
        return optimized_df
    
    def detect_optimal_strategy(self, file_path: str) -> str:
        """Detect optimal processing strategy based on file size and system resources."""
        file_size_mb = os.path.getsize(file_path) / 1024 / 1024
        available_memory_mb = psutil.virtual_memory().available / 1024 / 1024
        
        # Estimate memory needed (rough heuristic: CSV file size * 3-5x when loaded)
        estimated_memory_mb = file_size_mb * 4
        
        if estimated_memory_mb < available_memory_mb * 0.5:
            strategy = "memory_efficient"
            self.processing_stats['optimization_level'] = 'standard'
        elif estimated_memory_mb < available_memory_mb * 0.8:
            strategy = "chunked_processing"
            self.processing_stats['optimization_level'] = 'chunked'
        else:
            strategy = "disk_based_processing"
            self.processing_stats['optimization_level'] = 'aggressive'
        
        self.logger.info(f"File: {file_size_mb:.1f}MB, Available Memory: {available_memory_mb:.1f}MB")
        self.logger.info(f"Selected strategy: {strategy}")
        
        return strategy
    
    def process_large_file(self, file_path: str, processor_func: Callable) -> pd.DataFrame:
        """Process large file using optimal strategy."""
        self.processing_stats['start_time'] = datetime.now()
        
        strategy = self.detect_optimal_strategy(file_path)
        
        try:
            if strategy == "memory_efficient":
                result = self._process_memory_efficient(file_path, processor_func)
            elif strategy == "chunked_processing":
                result = self._process_chunked(file_path, processor_func)
            else:  # disk_based_processing
                result = self._process_disk_based(file_path, processor_func)
            
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['duration_seconds'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()
            
            self._log_performance_stats()
            return result
            
        except Exception as e:
            self.logger.error(f"Error in large file processing: {e}")
            raise
    
    def _process_memory_efficient(self, file_path: str, processor_func: Callable) -> pd.DataFrame:
        """Process file in memory with optimizations."""
        self._update_progress("Loading file into memory", 10)
        
        # Load with optimal dtypes
        df = pd.read_csv(file_path, low_memory=False)
        
        self._update_progress("Optimizing memory usage", 20)
        df = self.optimize_dataframe(df)
        
        self._update_progress("Processing data", 50)
        result = processor_func(df)
        
        self._update_progress("Finalizing results", 90)
        return result
    
    def _process_chunked(self, file_path: str, processor_func: Callable) -> pd.DataFrame:
        """Process file in chunks."""
        with ChunkedDataProcessor(self.chunk_size, self.config) as chunked_processor:
            
            self._update_progress("Reading file in chunks", 10)
            chunks = list(chunked_processor.read_csv_chunked(file_path))
            self.processing_stats['chunks_processed'] = len(chunks)
            
            self._update_progress("Processing chunks", 30)
            
            if self.use_parallel and len(chunks) > 1:
                processed_chunks = chunked_processor.process_chunks_parallel(
                    chunks, processor_func, self.max_workers
                )
            else:
                processed_chunks = [processor_func(chunk) for chunk in chunks]
            
            self._update_progress("Merging results", 80)
            result = chunked_processor.merge_processed_chunks(processed_chunks)
            
            return result
    
    def _process_disk_based(self, file_path: str, processor_func: Callable) -> pd.DataFrame:
        """Process file using disk-based approach for very large files."""
        with ChunkedDataProcessor(self.chunk_size // 2, self.config) as chunked_processor:
            
            self._update_progress("Processing with disk-based approach", 10)
            
            temp_results = []
            chunks = chunked_processor.read_csv_chunked(file_path)
            
            for i, chunk in enumerate(chunks):
                self._update_progress(f"Processing chunk {i+1}", 20 + (i * 60 / 100))
                
                # Process chunk
                processed_chunk = processor_func(chunk)
                
                # Save to temporary file if chunk is large
                if len(processed_chunk) > 1000:
                    temp_file = chunked_processor.save_temp_chunk(processed_chunk, f"result_{i}")
                    temp_results.append(temp_file)
                else:
                    temp_results.append(processed_chunk)
                
                # Force garbage collection
                del chunk, processed_chunk
                gc.collect()
            
            self._update_progress("Combining results", 85)
            
            # Combine results
            final_chunks = []
            for result in temp_results:
                if isinstance(result, str):  # File path
                    chunk = chunked_processor.load_temp_chunk(result)
                    final_chunks.append(chunk)
                else:  # DataFrame
                    final_chunks.append(result)
            
            result = chunked_processor.merge_processed_chunks(final_chunks)
            return result
    
    def _log_performance_stats(self):
        """Log performance statistics."""
        stats = self.processing_stats
        
        self.logger.info("Performance Statistics:")
        self.logger.info(f"  Duration: {stats['duration_seconds']:.2f} seconds")
        self.logger.info(f"  Peak Memory: {stats['peak_memory_mb']:.1f} MB")
        self.logger.info(f"  Optimization Level: {stats['optimization_level']}")
        if stats['chunks_processed'] > 0:
            self.logger.info(f"  Chunks Processed: {stats['chunks_processed']}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report."""
        return {
            'processing_stats': self.processing_stats,
            'system_info': {
                'cpu_count': mp.cpu_count(),
                'total_memory_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024,
                'available_memory_gb': psutil.virtual_memory().available / 1024 / 1024 / 1024
            },
            'configuration': {
                'chunk_size': self.chunk_size,
                'parallel_processing': self.use_parallel,
                'memory_optimization': self.memory_optimization,
                'max_workers': self.max_workers
            }
        }

def create_optimized_processor(progress_callback: Callable = None, config=None) -> OptimizedDataProcessor:
    """Factory function to create optimized processor."""
    return OptimizedDataProcessor(progress_callback, config) 