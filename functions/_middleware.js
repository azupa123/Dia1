export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);
  const p = url.pathname.toLowerCase();

  if (p.endsWith("/undefined.jpg") || p.endsWith("/undefined.jpeg") || p.endsWith("/undefined.png") || p.endsWith("/undefined.webp")) {
    const png1x1 = Uint8Array.from(atob("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2c2uQAAAAASUVORK5CYII="), c => c.charCodeAt(0));
    return new Response(png1x1, {
      status: 200,
      headers: {
        "Content-Type": "image/png",
        "Cache-Control": "no-store",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  const res = await next();
  const headers = new Headers(res.headers);
  headers.set("Access-Control-Allow-Origin", "*");
  headers.set("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  return new Response(res.body, { status: res.status, headers });
}
