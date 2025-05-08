from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, Playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
from duckduckgo_search import DDGS
from logger import logger

mcp = FastMCP("Saqr Server")
    

@mcp.tool()
async def web_search(
    query: str,
) -> Dict[str, any]:
    """
    Get data from web.
    
    Args:
        query: The search query.
    
    Returns:
        A dictionary with extracted data (title, content) and status.
    """

    try:
        results = []
        links = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                link = r.get('href') or r.get('link')
                if link:
                    links.append(link)
            

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()

            for i, link in enumerate(links[:3]):
                logger.debug(f"Processing link {i+1}: {link}")
                page = await context.new_page()
                try:
                    async with asyncio.timeout(60):
                        await page.goto(link, timeout=60000)
                    
                    title = await page.title()
                    content_elements = await page.query_selector_all('p')
                    await page.eval_on_selector_all("p", """
                    (elements) => {
                        for (const el of elements) {
                            el.style.border = "3px solid red";
                            el.style.backgroundColor = "#fffae6";
                        }
                    }
                    """)
                    content = " ".join([await elem.inner_text() for elem in content_elements]).strip()[:1000]
                    
                    results.append({
                        "link": link,
                        "title": title,
                        "content": content,
                        "source": "Web"
                    })
                    logger.debug(f"Extracted data from {link}: {title}")

                except PlaywrightTimeoutError:
                    logger.warning(f"Timeout processing {link}")
                    results.append({"link": link, "error": "Timeout", "source": "Web"})
                except Exception as e:
                    logger.warning(f"Error processing {link}: {str(e)}")
                    results.append({"link": link, "error": str(e), "source": "Web"})
                finally:
                    await page.close()

            await browser.close()

        response = {
            "results": results,
            "status": "complete",
            "message": f"Processed {len(results)} pages"
        }
        logger.info(f"extract_web_data completed with {len(results)} results")
        return response
    except Exception as e:
        logger.error(f"Error in extract_web_data: {str(e)}")
        return {"error": f"Extraction error: {str(e)}", "status": "failed"}


def main():
    try:
        asyncio.run(mcp.run(transport="stdio"))
    except KeyboardInterrupt:
        logger.error("Server stopped")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()