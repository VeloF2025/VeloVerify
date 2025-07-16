#!/usr/bin/env python3
"""
Simple test to check if Python and basic modules work
"""

import sys
import os

print("Python Test - VeloVerify Environment Check")
print("=" * 50)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Current directory: {os.getcwd()}")
print()

# Test basic imports
try:
    import tkinter as tk
    print("✅ tkinter (GUI library) - Available")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("VeloVerify - Simple Test")
    root.geometry("400x300")
    
    # Add some content
    label = tk.Label(root, text="VeloVerify Test Window", font=("Arial", 16))
    label.pack(pady=20)
    
    info_text = tk.Text(root, height=10, width=50)
    info_text.pack(pady=10)
    info_text.insert(tk.END, "This is a simple test of the VeloVerify environment.\n\n")
    info_text.insert(tk.END, f"Python Version: {sys.version}\n")
    info_text.insert(tk.END, f"Current Directory: {os.getcwd()}\n\n")
    info_text.insert(tk.END, "If you can see this window, the basic GUI functionality works!\n")
    info_text.insert(tk.END, "Close this window to continue.")
    
    close_btn = tk.Button(root, text="Close", command=root.quit)
    close_btn.pack(pady=10)
    
    print("🚀 Starting simple GUI test window...")
    root.mainloop()
    print("✅ GUI test completed successfully!")
    
except ImportError as e:
    print(f"❌ tkinter not available: {e}")

print("\n" + "=" * 50)
print("Test completed.") 