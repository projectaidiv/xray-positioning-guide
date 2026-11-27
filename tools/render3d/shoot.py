import sys
from playwright.sync_api import sync_playwright
ids = sys.argv[1:]
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width":1100,"height":700})
    pg.on("console", lambda m: print("console:", m.text) if m.type in ("error","warning") else None)
    pg.on("pageerror", lambda e: print("pageerror:", e))
    pg.goto("http://localhost:8700/index.html")
    pg.wait_for_function("window.__ready===true", timeout=20000)
    for i in ids:
        pg.evaluate(f"window.renderScene('{i}')")
        pg.wait_for_timeout(300)
        pg.locator("canvas").screenshot(path=f"/tmp/r_{i}.png")
        print("ok", i)
    b.close()
