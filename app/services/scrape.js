async function scrapePlayerHTML(playerId) {
  try {
    const url = `https://www.espncricinfo.com/ci/content/player/${playerId}.html`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();

    return {
      html: html,
      url: url,
      scraped_at: new Date().toISOString(),
    };
  } catch (error) {
    throw error;
  }
}

module.exports = {
  scrapePlayerHTML,
};

