from playwright.sync_api import sync_playwright, TimeoutError

def run(playwright):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    try:
        page.goto("http://localhost:5173/")

        # Wait for a fixed amount of time for the page to load
        page.wait_for_timeout(10000)

        # Click a non-error span
        page.locator('span.select-text').locator('text=const').first.click(timeout=60000)

        # Click an error span
        page.locator('span.select-text').locator('text=useState').first.click(timeout=60000)

        # Click another error span
        page.locator('span.select-text').locator('text=useRef').first.click(timeout=60000)

        # Wait for the reveal animation
        page.wait_for_timeout(1000)

        page.screenshot(path="jules-scratch/verification/verification.png")
    except TimeoutError:
        print("Timeout during test execution.")
        print(page.content())
        page.screenshot(path="jules-scratch/verification/timeout_error.png")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)