"""
html_to_image.py

Renders an HTML file (a folium map, an itables/styled table, any HTML)
in a real, invisible (headless) browser and saves it as a PNG.

This is fully automatic -- it launches Chromium in the background, loads
the file, waits for it to finish rendering (maps need a moment to draw
tiles/markers), and screenshots it. No human ever looks at a screen or
presses a key. It runs as part of the pipeline, same as any other step.

One-time setup (technical person, once per machine):
    pip install playwright
    playwright install chromium
"""

from pathlib import Path
from playwright.sync_api import sync_playwright


def html_to_png(html_path, png_path, width=900, height=600, wait_ms=800):
    html_path = Path(html_path).resolve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(html_path.as_uri())
        page.wait_for_timeout(wait_ms)  # let maps/tables finish rendering
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python html_to_image.py <input.html> <output.png>")
        sys.exit(1)
    html_to_png(sys.argv[1], sys.argv[2])
    print(f"Saved {sys.argv[2]}")
