import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import re

async def scrape_wikipedia_page(url):
    """
    Scrape a Wikipedia page and extract the most important content for LLM analysis
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle')
            
            # Extract the main content using JavaScript evaluation
            page_data = await page.evaluate("""
                () => {
                    // Helper function to clean text
                    const cleanText = (text) => text?.replace(/\\s+/g, ' ').trim() || '';
                    
                    // Get page title
                    const title = document.querySelector('h1.firstHeading')?.textContent || '';
                    
                    // Get the main summary/introduction (first paragraph)
                    const introElement = document.querySelector('#mw-content-text .mw-parser-output > p:first-of-type');
                    const introduction = cleanText(introElement?.textContent || '');
                    
                    // Get infobox data (very important for relationships)
                    const infobox = {};
                    const infoboxRows = document.querySelectorAll('.infobox tr');
                    infoboxRows.forEach(row => {
                        const header = row.querySelector('th, .infobox-label');
                        const data = row.querySelector('td, .infobox-data');
                        if (header && data) {
                            const key = cleanText(header.textContent);
                            const value = cleanText(data.textContent);
                            if (key && value) {
                                infobox[key] = value;
                            }
                        }
                    });
                    
                    // Get categories (important for classification)
                    const categories = Array.from(document.querySelectorAll('#mw-normal-catlinks ul li a'))
                        .map(link => cleanText(link.textContent))
                        .filter(cat => cat);
                    
                    // Get section headings and their content
                    const sections = [];
                    const headings = document.querySelectorAll('#mw-content-text h2, #mw-content-text h3');
                    
                    headings.forEach((heading, index) => {
                        const headingText = cleanText(heading.textContent.replace(/\\[edit\\]/g, ''));
                        if (!headingText) return;
                        
                        // Get content until next heading
                        let content = '';
                        let nextElement = heading.nextElementSibling;
                        const nextHeading = headings[index + 1];
                        
                        while (nextElement && nextElement !== nextHeading) {
                            if (nextElement.tagName === 'P') {
                                content += cleanText(nextElement.textContent) + ' ';
                            }
                            nextElement = nextElement.nextElementSibling;
                        }
                        
                        if (content.trim()) {
                            sections.push({
                                heading: headingText,
                                content: content.trim()
                            });
                        }
                    });
                    
                    // Get key facts from the first few paragraphs
                    const keyParagraphs = Array.from(document.querySelectorAll('#mw-content-text .mw-parser-output > p'))
                        .slice(0, 3)
                        .map(p => cleanText(p.textContent))
                        .filter(text => text.length > 50);
                    
                    // Extract notable links (other Wikipedia articles mentioned)
                    const notableLinks = Array.from(document.querySelectorAll('#mw-content-text a[href*="/wiki/"]:not([href*="Category:"]):not([href*="File:"]):not([href*="Template:"])'))
                        .map(link => ({
                            text: cleanText(link.textContent),
                            href: link.getAttribute('href')
                        }))
                        .filter(link => link.text && link.text.length > 2)
                        .slice(0, 20); // Limit to most relevant links
                    
                    // Get birth/death dates if available (for people)
                    const birthDeath = {};
                    const birthElement = document.querySelector('.bday');
                    const deathElement = document.querySelector('.dday');
                    if (birthElement) birthDeath.birth = cleanText(birthElement.textContent);
                    if (deathElement) birthDeath.death = cleanText(deathElement.textContent);
                    
                    // Get coordinates if available (for places)
                    const coordinates = {};
                    const coordElement = document.querySelector('.geo');
                    if (coordElement) {
                        const latElement = coordElement.querySelector('.latitude');
                        const lonElement = coordElement.querySelector('.longitude');
                        if (latElement) coordinates.latitude = latElement.textContent;
                        if (lonElement) coordinates.longitude = lonElement.textContent;
                    }
                    
                    return {
                        url: window.location.href,
                        title: title,
                        introduction: introduction,
                        infobox: infobox,
                        categories: categories,
                        sections: sections,
                        keyParagraphs: keyParagraphs,
                        notableLinks: notableLinks,
                        birthDeath: birthDeath,
                        coordinates: coordinates,
                        extractedAt: new Date().toISOString()
                    };
                }
            """)
            
            await browser.close()
            return page_data
            
        except Exception as e:
            await browser.close()
            raise Exception(f"Failed to scrape Wikipedia page: {str(e)}")