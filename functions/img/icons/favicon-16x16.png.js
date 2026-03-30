const PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO2c2uQAAAAASUVORK5CYII=";

function b64ToU8(b64) {
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

export async function onRequestGet() {
  return new Response(b64ToU8(PNG_B64), {
    status: 200,
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=86400",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
