const newsContainer = document.querySelector("#news");
const highlights = document.querySelector("#highlights");
const refreshButton = document.querySelector("#refresh");
const limitSelect = document.querySelector("#limit");

const setLoading = (loading = true) => {
  if (loading) {
    highlights.textContent = "加载中...";
    newsContainer.innerHTML = "<p class=\"muted\">正在抓取新闻...</p>";
  }
};

const formatDate = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", { hour12: false });
};

const renderCards = (articles = []) => {
  if (!articles.length) {
    newsContainer.innerHTML = "<p class=\"muted\">没有获取到新闻，请稍后再试。</p>";
    return;
  }
  newsContainer.innerHTML = articles
    .map(
      (item) => `
      <article class="card">
        <h3>${item.title}</h3>
        <p class="meta">${formatDate(item.published)}</p>
        <p>${item.summary || item.description || "暂无摘要"}</p>
        <a href="${item.link}" target="_blank" rel="noreferrer">阅读原文</a>
      </article>
    `
    )
    .join("");
};

const loadDigest = async () => {
  setLoading(true);
  const limit = limitSelect.value;
  const response = await fetch(`/api/digest?limit=${limit}`);
  const data = await response.json();
  highlights.textContent = data.highlights || "今日暂无明显新闻亮点。";
  renderCards(data.articles || []);
};

refreshButton.addEventListener("click", () => {
  loadDigest();
});

limitSelect.addEventListener("change", () => {
  loadDigest();
});

loadDigest();
