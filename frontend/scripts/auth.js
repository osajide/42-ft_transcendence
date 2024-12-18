async function auth42() {
  let data = "Error";
  const response = await fetch(glob_endp + "/api/intra/redirect/");
  if (response.ok) data = await response.json();
  // window.location.href = data.auth_url
}
