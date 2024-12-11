function search() {
  const mySearch = document.getElementById("searchUser");
  mySearch.addEventListener("input", async (e) => {
    const keyword = e.target.value;
    let result = [];
    let searchRes = document.getElementById("search_friends_class");
    if (keyword.length)
      result = await fetchWithToken(
        glob_endp,
        `/friend/search/${keyword}/`,
        "GET"
      );
    searchRes.innerHTML = components
      .friends_list(result, "search_friends")
      .trim()
      .split("\n")
      .slice(1, -1)
      .join("\n");
  });
}
