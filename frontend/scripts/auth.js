async function auth42() {
  let data = "Error";
    const clientId = "u-s4t2ud-1619f031b401b49c5796f0b7dc500bab1bad5c24ab3c19bb97df8c83adbfc15f";
    const redirectUri = "https://127.0.0.1/api/intra/oauth/";
    const authorizationUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(
      redirectUri
    )}&response_type=code`;

    window.location.href = authorizationUrl;
}