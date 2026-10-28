import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .get_driver import get_driver

URL = "https://www.qfxcinemas.com/now-showing"
CARD_SELECTOR = "article.movie_n_fests_grid div.parent_poster_wrapper"

# Runs inside the browser: one call returns every movie.
EXTRACT_JS = r"""
const clean = s => (s || '').replace(/\s+/g, ' ').trim();

return Array.from(document.querySelectorAll(arguments[0])).map(w => {
  const article = w.querySelector('article');
  const img     = w.querySelector('img.img-fluid');
  const rating  = w.querySelector('.rating-tag');
  const span    = w.querySelector('.time_poster span');
  const titleEl = w.querySelector('.responsive_font_movie_title');

  // Title: prefer the article's title attribute
  let title = article ? article.getAttribute('title') : '';
  if (!title && titleEl) {
    // fallback: first direct text node only (avoids the nested details text)
    const node = Array.from(titleEl.childNodes)
      .find(n => n.nodeType === 3 && n.textContent.trim());
    title = node ? node.textContent : '';
  }

  const detail = clean(span ? span.textContent : '');   // "English Dubbed | Horror,Action,Drama"
  const parts  = detail.split('|').map(clean);

  return {
    title:    clean(title),
    image:    img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '',
    rating:   clean(rating ? rating.textContent : ''),
    language: parts[0] || '',
    genres:   parts[1] || '',
    detail:   detail
  };
});
"""


def _scroll_to_load_all(driver, pause=1.0, max_rounds=10):
    """Scroll until the number of cards stops growing (handles lazy loading)."""
    last_count = -1
    for _ in range(max_rounds):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        count = len(driver.find_elements(By.CSS_SELECTOR, CARD_SELECTOR))
        if count == last_count:
            break
        last_count = count


def scrape_movies():
    driver = get_driver()
    try:
        driver.get(URL)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, CARD_SELECTOR))
            )
        except TimeoutException:
            print("Timed out waiting for movie cards")
            return []

        _scroll_to_load_all(driver)

        raw = driver.execute_script(EXTRACT_JS, CARD_SELECTOR) or []
        print(f"Found {len(raw)} movie cards")

        movies, seen = [], set()
        for item in raw:
            title = item.get("title") or "N/A"
            if title in seen:          # avoid duplicates if the page repeats cards
                continue
            seen.add(title)

            genres = [g.strip() for g in (item.get("genres") or "").split(",") if g.strip()]

            movies.append({
                "Title": title,
                "Image_URL": item.get("image") or "N/A",
                "Rating": item.get("rating") or "N/A",
                "Language": item.get("language") or "N/A",
                "Genres": genres,
                "Genre_language": item.get("detail") or "N/A",
            })

        print(f"Total movies scraped: {len(movies)}")
        return movies
    finally:
        driver.quit()