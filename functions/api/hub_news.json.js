function json(payload) {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

export async function onRequestGet() {
  const items = [0, 1, 2, 3, 4, 5].map((n) => {
    const url = `/api/news/${n}.jpg`;
    return {
      id: n,
      title: `news-${n}`,
      text: [""],
      img: url,
      image: url,
      photo: url,
      date: "",
    };
  });

  return json(items);
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
