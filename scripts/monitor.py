"""
Tiny Inference Lab - OCR benchmark resource monitor.
Usage:
  python monitor.py --name tesseract_page_test -- python run_ocr.py
Requires: psutil, nvidia-ml-py (GPU metrics optional).
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_OK = True
    GPU_HANDLE = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception:
    GPU_OK = False
    GPU_HANDLE = None

def gpu_metrics():
    if not GPU_OK:
        return "", ""
    try:
        util = pynvml.nvmlDeviceGetUtilizationRates(GPU_HANDLE).gpu
        mem = pynvml.nvmlDeviceGetMemoryInfo(GPU_HANDLE).used / (1024 ** 2)
        return util, round(mem, 1)
    except Exception:
        return "", ""

def process_tree(root):
    procs = []
    try:
        parent = psutil.Process(root)
        procs = [parent] + parent.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return procs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--output-dir", default="benchmarks")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        ap.error("Provide a command after --, e.g. -- python run_ocr.py")

    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = outdir / f"{args.name}_{stamp}_resources.csv"

    disk_before = shutil.disk_usage(os.getcwd()).used
    start = time.perf_counter()
    child = subprocess.Popen(command)
    root = psutil.Process(child.pid)

    # Prime CPU counters.
    for proc in process_tree(child.pid):
        try:
            proc.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    fields = [
        "timestamp_utc", "elapsed_s", "system_cpu_percent",
        "process_tree_cpu_percent", "process_tree_ram_mb",
        "process_tree_read_mb", "process_tree_write_mb",
        "gpu_util_percent", "gpu_memory_used_mb"
    ]
    peak_ram = 0.0
    peak_gpu = 0.0
    samples = 0

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        while child.poll() is None:
            time.sleep(args.interval)
            procs = process_tree(child.pid)
            cpu = ram = read_b = write_b = 0
            for proc in procs:
                try:
                    cpu += proc.cpu_percent(None)
                    mem = proc.memory_info()
                    ram += mem.rss
                    io = proc.io_counters()
                    read_b += io.read_bytes
                    write_b += io.write_bytes
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue

            gpu_util, gpu_mem = gpu_metrics()
            ram_mb = round(ram / (1024 ** 2), 1)
            peak_ram = max(peak_ram, ram_mb)
            if gpu_mem != "":
                peak_gpu = max(peak_gpu, float(gpu_mem))
            samples += 1
            writer.writerow({
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_s": round(time.perf_counter() - start, 2),
                "system_cpu_percent": psutil.cpu_percent(None),
                "process_tree_cpu_percent": round(cpu, 1),
                "process_tree_ram_mb": ram_mb,
                "process_tree_read_mb": round(read_b / (1024 ** 2), 2),
                "process_tree_write_mb": round(write_b / (1024 ** 2), 2),
                "gpu_util_percent": gpu_util,
                "gpu_memory_used_mb": gpu_mem
            })
            f.flush()

    elapsed = time.perf_counter() - start
    disk_after = shutil.disk_usage(os.getcwd()).used
    print(f"\nExit code: {child.returncode}")
    print(f"Elapsed: {elapsed:.2f} s")
    print(f"Peak process-tree RAM: {peak_ram:.1f} MB")
    print(f"Peak GPU memory observed: {peak_gpu:.1f} MB (global GPU reading)")
    print(f"Working-drive used-space delta: {(disk_after-disk_before)/(1024**2):.2f} MB")
    print(f"Resource log: {csv_path}")
    if not GPU_OK:
        print("GPU metrics unavailable: install nvidia-ml-py and check nvidia-smi.")
    raise SystemExit(child.returncode)

if __name__ == "__main__":
    main()
