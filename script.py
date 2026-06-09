import math
import re
import time
import tkinter as tk
import sys
import msvcrt

def parse_f3c(text):
    pattern = r"tp @s (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)"
    match = re.search(pattern, text)
    if match:
        return {
            "x": float(match.group(1)), "y": float(match.group(2)), "z": float(match.group(3)),
            "yaw": float(match.group(4)), "pitch": float(match.group(5))
        }
    return None

def calculate_xz(points):
    sum_AA, sum_AB, sum_BB, sum_AC, sum_BC = 0.0, 0.0, 0.0, 0.0, 0.0
    for p in points:
        rad_yaw = math.radians(p["yaw"])
        m_dx, m_dz = -math.sin(rad_yaw), math.cos(rad_yaw)
        a, b = -m_dz, m_dx
        c = a * p["x"] + b * p["z"]
        sum_AA += a * a
        sum_AB += a * b
        sum_BB += b * b
        sum_AC += a * c
        sum_BC += b * c
    det = sum_AA * sum_BB - sum_AB * sum_AB
    if abs(det) < 1e-5: return None, None
    return (sum_AC * sum_BB - sum_BC * sum_AB) / det, (sum_AA * sum_BC - sum_AB * sum_AC) / det

def calculate_y(ix, iz, p_low, p_high):
    def get_y(p):
        dist = math.sqrt((ix - p["x"])**2 + (iz - p["z"])**2)
        return p["y"] - (dist * math.tan(math.radians(p["pitch"])))
    return (get_y(p_low) + get_y(p_high)) / 2.0

def get_clip(root):
    try:
        return root.clipboard_get().strip()
    except:
        return ""

def main():
    root = tk.Tk()
    root.withdraw()
    
    print("Locator Bar Finder")
    print("Step 1: Copy position with f3 + c then move to the left and reposition ur locator bar.")
    print("  - Get 2 or more points for better accuracy.")
    print("  - Press Y if you want to get the y coord.")
    
    points, last_clip = [], ""
    while True:
        # check keyboard
        if msvcrt.kbhit():
            key = msvcrt.getch().decode().lower()
            if key == 'y':
                if len(points) < 2:
                    print("\n you need at least 2 points")
                else:
                    break
        
        # check clipboard
        clip = get_clip(root)
        if clip != last_clip and "tp @s" in clip:
            last_clip = clip
            data = parse_f3c(clip)
            if data:
                if not points or (data["x"] != points[-1]["x"] or data["z"] != points[-1]["z"]):
                    points.append(data)
                    print(f"got point #{len(points)}")
        
        time.sleep(0.1)

    ix, iz = calculate_xz(points)
    print(f"\nChanging to y with {len(points)} points: {ix:.1f}, {iz:.1f}")
    
    print("\nstep 2: Copy pos for bottom edge")
    p_low = None
    while not p_low:
        clip = get_clip(root)
        if clip != last_clip and "tp @s" in clip:
            last_clip = clip
            p_low = parse_f3c(clip)
            if p_low: print("Got the bottom edge pos")
        time.sleep(0.1)

    print("step 3: Copy pos for top edge")
    p_high = None
    while not p_high:
        clip = get_clip(root)
        if clip != last_clip and "tp @s" in clip:
            last_clip = clip
            p_high = parse_f3c(clip)
            if p_high: print("Got the top edge pos")
        time.sleep(0.1)

    iy = calculate_y(ix, iz, p_low, p_high)
    cmd = f"/tp @s {int(ix)} {int(iy)} {int(iz)}"
    print(f"\napproximate coords: {ix:.1f} {iy:.1f} {iz:.1f}")
    print(f"tp command: {cmd}")
    
    root.clipboard_clear()
    root.clipboard_append(cmd)
    print("\nCopied. Press any key to exit.")
    msvcrt.getch()

if __name__ == "__main__":
    main()
