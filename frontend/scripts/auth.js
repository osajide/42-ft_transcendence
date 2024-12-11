async function auth42() {
  let data = "Error";
  const response = await fetch("http://127.0.0.1:8000/api/intra/redirect/");
  if (response.ok) data = await response.json();
  // window.location.href = data.auth_url
}
